import json
import logging
import os

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "qwen").lower()
        self.qwen_model = os.getenv("QWEN_MODEL", "Qwen/Qwen2.5-3B-Instruct")
        self.qwen_tokenizer = None
        self.qwen_model_instance = None
        self._load_attempted = False

    def _load_qwen(self):
        if self.qwen_model_instance is not None:
            return
        if self._load_attempted:
            raise RuntimeError("Qwen model unavailable")

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            self._load_attempted = True
            raise RuntimeError(
                "Transformers / Torch is not installed. Run: pip install -r requirements.txt"
            ) from exc

        try:
            # Check if weights already downloaded locally
            self.qwen_tokenizer = AutoTokenizer.from_pretrained(
                self.qwen_model,
                trust_remote_code=True,
                local_files_only=True,
            )
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            self.qwen_model_instance = AutoModelForCausalLM.from_pretrained(
                self.qwen_model,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                local_files_only=True,
            )
            if torch.cuda.is_available():
                self.qwen_model_instance = self.qwen_model_instance.to("cuda")
            self.qwen_model_instance.eval()
        except Exception as exc:
            self._load_attempted = True
            logger.info("Local Qwen weights not cached (%s); using fast deterministic inference pipeline.", exc)
            raise RuntimeError("Qwen weights not cached locally") from exc

    def _qwen_json(self, system_prompt: str, payload: dict) -> dict:
        self._load_qwen()
        import torch

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload)},
        ]
        prompt = self.qwen_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.qwen_tokenizer(prompt, return_tensors="pt")
        device = next(self.qwen_model_instance.parameters()).device
        inputs = {name: value.to(device) for name, value in inputs.items()}
        with torch.inference_mode():
            output = self.qwen_model_instance.generate(
                **inputs,
                max_new_tokens=600,
                do_sample=False,
                pad_token_id=self.qwen_tokenizer.eos_token_id,
            )
        generated = output[0][inputs["input_ids"].shape[1]:]
        content = self.qwen_tokenizer.decode(generated, skip_special_tokens=True).strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start < 0 or end <= start:
                raise ValueError("Qwen returned invalid JSON")
            return json.loads(content[start:end + 1])

    def analyze_resume(self, resume_text: str, deterministic_analysis: dict) -> dict:
        prompt = {
            "resume_text": resume_text[:12000],
            "required_output": {
                "skills": [{
                    "name": "canonical skill name (e.g., Python, FastAPI, PostgreSQL, Docker)",
                    "category": "Programming Language, Framework, Database, Tool, Cloud, AI/ML, or Soft Skills",
                    "evidence": "evidence from the resume",
                    "confidence": 0.95,
                }],
                "education": [{
                    "degree": "Degree name or qualification (e.g. B.Tech in Computer Science)",
                    "institution": "University or Institute name",
                    "year": "Graduation period (e.g. 2020 - 2024)",
                    "gpa": "Grade / CGPA or Distinction",
                    "details": "Summary of major and coursework",
                }],
                "experience": [{
                    "role": "Job title or role",
                    "company": "Company or organization name",
                    "duration": "Duration (e.g. 2023 - Present)",
                    "location": "Location",
                    "description": "Key contributions and engineering impact",
                    "highlights": ["Bullet point 1", "Bullet point 2"],
                }],
                "internships": [{
                    "role": "Internship role title",
                    "company": "Company or lab name",
                    "duration": "Duration",
                    "description": "Internship responsibilities and projects built",
                }],
                "projects": [{
                    "title": "Project name",
                    "technologies": ["Tech 1", "Tech 2"],
                    "description": "Project overview, architecture, and results",
                    "highlights": ["Key feature or achievement"],
                }],
                "certifications": [{
                    "name": "Certification or course name",
                    "issuer": "Issuing organization (AWS, Coursera, HackerRank, etc.)",
                    "year": "Year issued",
                }],
                "achievements": [{
                    "title": "Achievement or award title",
                    "description": "Description of recognition, hackathon rank, or milestone",
                    "year": "Year",
                }],
                "suggested_roles": ["Suggested Role 1", "Suggested Role 2", "Suggested Role 3"],
                "domains": ["Technical Domain 1", "Technical Domain 2"],
            },
        }
        if self.provider == "qwen":
            system_prompt = (
                "You are an expert ATS and Senior Technical Recruiter. "
                "Analyze the provided resume text thoroughly and extract structured details for all sections: "
                "Skills, Education, Experience, Internships, Projects, Certifications, Achievements, Suggested Roles, and Domains. "
                "If an exact section is not explicitly titled, intelligently extract and organize the relevant details from the candidate's background. "
                "Always populate each field with realistic, structured items based on the candidate's profile. "
                "Return only valid JSON matching required_output."
            )
            result = self._qwen_json(system_prompt, prompt)
            result["status"] = "complete"
            result["provider"] = "qwen"
            return result

        raise RuntimeError("Qwen provider is required; set AI_PROVIDER=qwen")

    def recommend_for_job(self, job_description: str, resume_analysis: dict) -> dict:
        prompt = {
            "job_description": job_description[:12000],
            "resume_analysis": resume_analysis,
            "required_output": {
                "overall_fit": "score between 0 and 100",
                "key_matches": ["skills and experiences that align with the job"],
                "gaps": ["missing skills or weak areas"],
                "recommendation": "summary of why the candidate is a fit",
                "next_steps": ["specific actions to improve fit"],
            },
        }
        if self.provider == "qwen":
            result = self._qwen_json(
                "You are a hiring advisor. Return only valid JSON with evidence from the resume.",
                prompt,
            )
            result["status"] = "complete"
            result["provider"] = "qwen"
            return result

        raise RuntimeError("Qwen provider is required; set AI_PROVIDER=qwen")

    def generate_resume(self, name: str, user_choice: str) -> dict:
        prompt = {
            "candidate_name": name,
            "candidate_input": user_choice[:6000],
            "required_output": {
                "name": name,
                "headline": "target professional headline (e.g. Senior Backend Engineer)",
                "summary": "comprehensive professional summary",
                "skills": ["Skill 1", "Skill 2", "Skill 3"],
                "experience": [{
                    "role": "Role title",
                    "company": "Company name",
                    "duration": "Duration (e.g. 2023 - Present)",
                    "location": "Location",
                    "description": "Key contributions and engineering impact",
                    "highlights": ["Highlight 1", "Highlight 2"],
                }],
                "projects": [{
                    "title": "Project title",
                    "technologies": ["Tech 1", "Tech 2"],
                    "description": "Architecture, system design, and results",
                    "highlights": ["Highlight 1", "Highlight 2"],
                }],
                "education": [{
                    "degree": "Degree name",
                    "institution": "Institute or University name",
                    "year": "Year period",
                    "gpa": "Grade / CGPA",
                    "details": "Core coursework and specialization",
                }],
                "certifications": ["Certification 1", "Certification 2"],
                "achievements": ["Achievement 1", "Achievement 2"],
                "domains": ["Domain 1", "Domain 2"],
                "formatted_resume": "plain-text formatted ATS-friendly resume",
            },
        }
        if self.provider == "qwen":
            system_prompt = (
                "You are a professional Executive Resume Writer and Career Coach. "
                "Generate a top-tier, comprehensive, ATS-optimized CV/resume based on the candidate's inputs. "
                "Synthesize rich, professional content for all fields: Headline, Summary, Skills, Experience, "
                "Projects, Education, Certifications, Achievements, Domains, and Formatted Resume. "
                "Ensure no section is left empty or null. Return only valid JSON."
            )
            result = self._qwen_json(system_prompt, prompt)
            result["status"] = "complete"
            result["provider"] = "qwen"
            return result

        raise RuntimeError("Qwen provider is required; set AI_PROVIDER=qwen")

    def generate_interview_final_report(self, interview_context: dict, transcript_history: list) -> dict:
        """10. Final evaluation: Generates comprehensive final report using the entire interview history with Qwen LLM."""
        prompt = {
            "interview_context": interview_context,
            "interview_transcript_history": transcript_history,
            "required_output": {
                "overall_score": 0.0,
                "technical_score": 0.0,
                "problem_solving_score": 0.0,
                "communication_score": 0.0,
                "overall_performance": "Detailed narrative summary of candidate's overall performance across the interview.",
                "technical_knowledge": "Evaluation of candidate's core technical understanding and accuracy.",
                "problem_solving": "Evaluation of candidate's reasoning, problem-solving approach, and algorithmic depth.",
                "communication": "Evaluation of clarity, structure, and communication effectiveness.",
                "strong_areas": ["Key strong skill or area 1", "Key strong skill 2"],
                "weak_areas": ["Weak area or gap 1", "Weak area 2"],
                "topics_that_need_improvement": ["Specific concept 1", "Specific concept 2"],
                "question_wise_performance": [
                    {
                        "question_id": 0,
                        "question_text": "...",
                        "candidate_answer": "...",
                        "score": 0.0,
                        "feedback": "...",
                        "keywords_detected": [],
                        "time_taken_seconds": 0,
                    }
                ],
                "recommended_preparation_topics": ["Actionable preparation topic 1", "Actionable preparation topic 2"],
            },
        }
        if self.provider == "qwen":
            system_prompt = (
                "You are a Principal Engineering Interviewer and Hiring Committee Chair. "
                "Analyze the candidate's entire interview history (all questions asked and candidate answers given). "
                "Provide an exhaustive, balanced evaluation covering Overall Performance, Technical Knowledge, "
                "Problem-Solving, Communication, Strong Areas, Weak Areas, Topics that need improvement, "
                "Question-wise performance, and Recommended preparation topics. "
                "Return only valid JSON matching the required_output format."
            )
            result = self._qwen_json(system_prompt, prompt)
            result["status"] = "complete"
            result["provider"] = "qwen"
            return result

        raise RuntimeError("Qwen provider is required; set AI_PROVIDER=qwen")
