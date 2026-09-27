from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.company import Company
from app.models.job import Job

router = APIRouter(prefix="/companies", tags=["Companies"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


TOP_COMPANIES_DATA = [
    {
        "name": "Google",
        "industry": "Technology & Artificial Intelligence",
        "website": "https://google.com",
        "location": "Mountain View, CA & Bengaluru, India",
        "description": "Global technology leader pioneering large-scale search, cloud computing, machine learning, Android, and distributed systems.",
        "size": "150,000+",
        "jobs": [
            {
                "title": "Software Engineer III - Backend Systems",
                "description": "Design and build massively scalable microservices and distributed storage systems powering billions of daily search queries.",
                "required_skills": ["Python", "C++", "Distributed Systems", "SQL", "Go", "GCP"],
                "location": "Mountain View, CA / Bengaluru",
                "salary_range": "$140,000 - $210,000 / ₹35 - 55 LPA",
                "job_type": "Full-time",
            },
            {
                "title": "Machine Learning Engineer - Large Models",
                "description": "Develop and fine-tune multimodal generative AI models, transformer architectures, and high-performance inference pipelines.",
                "required_skills": ["Python", "PyTorch", "TensorFlow", "Deep Learning", "NLP", "CUDA"],
                "location": "Sunnyvale, CA / Hybrid",
                "salary_range": "$160,000 - $240,000 / ₹40 - 65 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Microsoft",
        "industry": "Cloud Computing & Enterprise Software",
        "website": "https://microsoft.com",
        "location": "Redmond, WA & Hyderabad, India",
        "description": "Empowering every person and organization with Azure Cloud, developer tools, AI copilot platforms, and operating systems.",
        "size": "200,000+",
        "jobs": [
            {
                "title": "Cloud Solutions Architect - Azure Platform",
                "description": "Architect mission-critical enterprise cloud architectures, Kubernetes clusters, and asynchronous event streams.",
                "required_skills": ["Azure", "Docker", "Kubernetes", "C#", "Python", "CI/CD"],
                "location": "Redmond, WA / Remote",
                "salary_range": "$135,000 - $195,000 / ₹32 - 50 LPA",
                "job_type": "Full-time",
            },
            {
                "title": "Full Stack Engineer - Developer Platforms",
                "description": "Build high-performance web applications, developer portals, and collaborative engineering tools.",
                "required_skills": ["TypeScript", "React", "Node.js", "GraphQL", "Azure DevOps"],
                "location": "Hyderabad, India / Hybrid",
                "salary_range": "$120,000 - $175,000 / ₹28 - 45 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Amazon",
        "industry": "E-commerce & Cloud Infrastructure",
        "website": "https://amazon.com",
        "location": "Seattle, WA & Bengaluru, India",
        "description": "World's leading e-commerce enterprise and pioneer of AWS cloud infrastructure, serverless computing, and supply chain automation.",
        "size": "1,500,000+",
        "jobs": [
            {
                "title": "Software Development Engineer II (SDE-2)",
                "description": "Engineer low-latency distributed microservices for AWS core infrastructure handling millions of transactions per second.",
                "required_skills": ["Java", "Python", "AWS DynamoDB", "Distributed Systems", "REST APIs"],
                "location": "Seattle, WA / Bengaluru",
                "salary_range": "$145,000 - $215,000 / ₹36 - 60 LPA",
                "job_type": "Full-time",
            },
            {
                "title": "DevOps / SRE Engineer - AWS Cloud",
                "description": "Automate cloud infrastructure deployments, terraform modules, observability dashboards, and incident remediation.",
                "required_skills": ["AWS", "Terraform", "Docker", "Kubernetes", "Linux", "Python"],
                "location": "Austin, TX / Remote",
                "salary_range": "$130,000 - $185,000 / ₹30 - 48 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Meta",
        "industry": "Social Technology & AI Research",
        "website": "https://meta.com",
        "location": "Menlo Park, CA & London, UK",
        "description": "Building the future of connection, open-source AI frameworks (PyTorch, Llama), and next-generation social platforms.",
        "size": "70,000+",
        "jobs": [
            {
                "title": "Production Engineer - Core Infrastructure",
                "description": "Ensure reliability, scalability, and performance of large-scale distributed systems serving over 3 billion active users.",
                "required_skills": ["Python", "C++", "Linux Systems", "TCP/IP", "Distributed Systems"],
                "location": "Menlo Park, CA / Remote",
                "salary_range": "$155,000 - $225,000 / ₹42 - 68 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Apple",
        "industry": "Consumer Electronics & Operating Systems",
        "website": "https://apple.com",
        "location": "Cupertino, CA & Hyderabad, India",
        "description": "Creating seamless user experiences through hardware, macOS, iOS, Apple Silicon, and secure global cloud services.",
        "size": "160,000+",
        "jobs": [
            {
                "title": "Backend Software Engineer - Apple Cloud Services",
                "description": "Develop high-security, high-availability distributed backend services for iCloud, Apple Music, and App Store.",
                "required_skills": ["Java", "Python", "Cassandra", "Kafka", "Microservices", "REST APIs"],
                "location": "Cupertino, CA / Hybrid",
                "salary_range": "$150,000 - $220,000 / ₹38 - 58 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Netflix",
        "industry": "Media Streaming & Cloud Architecture",
        "website": "https://netflix.com",
        "location": "Los Gatos, CA & Remote",
        "description": "World leader in entertainment streaming, pioneering chaos engineering, microservice architectures, and recommendation systems.",
        "size": "13,000+",
        "jobs": [
            {
                "title": "Senior Distributed Systems Engineer",
                "description": "Scale global video encoding and dynamic content delivery networks delivering 4K streams to 250M+ subscribers worldwide.",
                "required_skills": ["Java", "Go", "AWS", "Kafka", "Microservices", "System Design"],
                "location": "Los Gatos, CA / Remote",
                "salary_range": "$220,000 - $350,000",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "NVIDIA",
        "industry": "Accelerated Computing & AI Hardware",
        "website": "https://nvidia.com",
        "location": "Santa Clara, CA & Pune, India",
        "description": "Inventor of the GPU and world leader in accelerated computing platforms for AI, autonomous vehicles, and high-performance computing.",
        "size": "30,000+",
        "jobs": [
            {
                "title": "AI Infrastructure Software Engineer",
                "description": "Develop high-performance CUDA/C++ runtimes, TensorRT acceleration kernels, and distributed GPU cluster orchestrators.",
                "required_skills": ["C++", "Python", "CUDA", "PyTorch", "High Performance Computing"],
                "location": "Santa Clara, CA / Pune",
                "salary_range": "$150,000 - $230,000 / ₹38 - 60 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "OpenAI",
        "industry": "Artificial General Intelligence",
        "website": "https://openai.com",
        "location": "San Francisco, CA",
        "description": "Research and deployment company dedicated to ensuring artificial general intelligence benefits all of humanity.",
        "size": "2,000+",
        "jobs": [
            {
                "title": "Full Stack API & Systems Engineer",
                "description": "Build high-throughput developer APIs, real-time WebSocket streaming services, and developer platforms for frontier AI models.",
                "required_skills": ["Python", "FastAPI", "TypeScript", "React", "PostgreSQL", "Redis"],
                "location": "San Francisco, CA / Hybrid",
                "salary_range": "$190,000 - $300,000",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Stripe",
        "industry": "Financial Technology & Payment Infrastructure",
        "website": "https://stripe.com",
        "location": "San Francisco, CA & Dublin, Ireland",
        "description": "Financial infrastructure platform for the internet, powering transactions for startups to Fortune 500 enterprises.",
        "size": "8,000+",
        "jobs": [
            {
                "title": "Backend Payments Infrastructure Engineer",
                "description": "Build fault-tolerant banking integrations and ledger accounting systems processing billions in financial volume.",
                "required_skills": ["Ruby", "Java", "Go", "SQL", "Distributed Systems", "Idempotency"],
                "location": "Remote / San Francisco, CA",
                "salary_range": "$160,000 - $235,000",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Uber",
        "industry": "Mobility, Logistics & Real-time Systems",
        "website": "https://uber.com",
        "location": "San Francisco, CA & Hyderabad, India",
        "description": "Transforming urban mobility and logistics through real-time geospatial dispatching, dynamic pricing, and autonomous systems.",
        "size": "30,000+",
        "jobs": [
            {
                "title": "Senior Backend Engineer - Marketplace Dispatch",
                "description": "Engineer low-latency geospatial matching engines handling millions of ride requests and driver updates every second.",
                "required_skills": ["Go", "Java", "Kafka", "Redis", "Microservices", "System Design"],
                "location": "Hyderabad, India / San Francisco",
                "salary_range": "$140,000 - $205,000 / ₹35 - 55 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Spotify",
        "industry": "Audio Streaming & Content Discovery",
        "website": "https://spotify.com",
        "location": "Stockholm, Sweden & New York, NY",
        "description": "Connecting creators with millions of listeners through dynamic personalized discovery algorithms and audio streaming.",
        "size": "9,000+",
        "jobs": [
            {
                "title": "Data & ML Engineer - Recommendation Engine",
                "description": "Build real-time personalization pipelines and collaborative filtering models powering Discover Weekly.",
                "required_skills": ["Python", "Java", "GCP", "Apache Spark", "Scikit-Learn", "BigQuery"],
                "location": "New York, NY / Stockholm",
                "salary_range": "$145,000 - $210,000",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Adobe",
        "industry": "Digital Media & Creative Cloud",
        "website": "https://adobe.com",
        "location": "San Jose, CA & Noida, India",
        "description": "Changing the world through digital experiences, Photoshop, Acrobat, Firefly AI, and enterprise analytics platforms.",
        "size": "29,000+",
        "jobs": [
            {
                "title": "Software Engineer - Creative Cloud AI",
                "description": "Integrate generative AI image models and high-performance WebAssembly rendering into cloud creative applications.",
                "required_skills": ["C++", "JavaScript", "WebAssembly", "Python", "Computer Vision"],
                "location": "Noida, India / San Jose, CA",
                "salary_range": "$130,000 - $185,000 / ₹28 - 48 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Salesforce",
        "industry": "Enterprise CRM & Cloud Applications",
        "website": "https://salesforce.com",
        "location": "San Francisco, CA & Bengaluru, India",
        "description": "World's #1 CRM platform empowering businesses of all sizes with AI-driven customer relationship management.",
        "size": "73,000+",
        "jobs": [
            {
                "title": "Software Engineer - Enterprise Data Cloud",
                "description": "Develop multi-tenant cloud storage engines, real-time query analyzers, and automated data ingestion pipelines.",
                "required_skills": ["Java", "Python", "PostgreSQL", "Kafka", "AWS", "Spring Boot"],
                "location": "Bengaluru, India / San Francisco",
                "salary_range": "$130,000 - $190,000 / ₹30 - 50 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Snowflake",
        "industry": "Data Cloud & Warehousing",
        "website": "https://snowflake.com",
        "location": "Bozeman, MT & San Mateo, CA",
        "description": "Pioneering the Data Cloud, uniting siloed data, discovering insights, and executing diverse analytic workloads.",
        "size": "7,000+",
        "jobs": [
            {
                "title": "Core Database Engine Developer",
                "description": "Implement distributed SQL execution engines, columnar storage optimizations, and query vectorization.",
                "required_skills": ["C++", "Java", "Distributed Query Engines", "SQL", "Linux"],
                "location": "San Mateo, CA / Remote",
                "salary_range": "$160,000 - $240,000",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Databricks",
        "industry": "Data Lakehouse & Unified Analytics",
        "website": "https://databricks.com",
        "location": "San Francisco, CA & Bengaluru, India",
        "description": "Pioneering the Data Lakehouse architecture, Apache Spark, MLflow, and generative AI platforms.",
        "size": "6,500+",
        "jobs": [
            {
                "title": "Distributed Systems Engineer - Spark Core",
                "description": "Enhance Apache Spark distributed execution, memory management, and cloud runtime optimization.",
                "required_skills": ["Scala", "Java", "Python", "Apache Spark", "Distributed Computing"],
                "location": "San Francisco, CA / Bengaluru",
                "salary_range": "$165,000 - $245,000 / ₹40 - 65 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Atlassian",
        "industry": "DevOps & Team Collaboration",
        "website": "https://atlassian.com",
        "location": "Sydney, Australia & Bengaluru, India",
        "description": "Empowering teams worldwide with Jira, Confluence, Trello, and enterprise DevOps collaboration suites.",
        "size": "11,000+",
        "jobs": [
            {
                "title": "Full Stack Engineer - Jira Cloud",
                "description": "Design responsive, high-performance web applications and backend GraphQL services serving 10M+ daily engineers.",
                "required_skills": ["React", "TypeScript", "Node.js", "Java", "AWS", "GraphQL"],
                "location": "Bengaluru, India / Sydney",
                "salary_range": "$125,000 - $180,000 / ₹28 - 46 LPA",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "GitHub",
        "industry": "Developer Tools & Open Source",
        "website": "https://github.com",
        "location": "San Francisco, CA & Global Remote",
        "description": "Home for 100M+ developers, hosting Git repositories, GitHub Actions CI/CD, and AI Copilot pair programming.",
        "size": "4,000+",
        "jobs": [
            {
                "title": "Systems Engineer - Git Core & Actions",
                "description": "Scale continuous integration runners, container isolation sandboxes, and high-performance Git backend infrastructure.",
                "required_skills": ["Go", "Ruby", "Linux", "Docker", "Kubernetes", "Git Internals"],
                "location": "Global Remote",
                "salary_range": "$145,000 - $215,000",
                "job_type": "Full-time",
            },
        ],
    },
    {
        "name": "Airbnb",
        "industry": "Global Marketplace & Hospitality",
        "website": "https://airbnb.com",
        "location": "San Francisco, CA & Remote",
        "description": "Powering unique travel and hospitality experiences worldwide with trusted distributed marketplace technology.",
        "size": "6,800+",
        "jobs": [
            {
                "title": "Backend Engineer - Search & Ranking",
                "description": "Develop high-precision search ranking algorithms and dynamic pricing models across millions of worldwide listings.",
                "required_skills": ["Java", "Kotlin", "Python", "Machine Learning", "Elasticsearch", "SQL"],
                "location": "San Francisco, CA / Remote",
                "salary_range": "$150,000 - $225,000",
                "job_type": "Full-time",
            },
        ],
    },
]


def _ensure_seed_companies_and_jobs(db: Session):
    """Seed comprehensive company catalog and active jobs if not already present."""
    existing_count = db.query(Company).count()
    if existing_count < len(TOP_COMPANIES_DATA):
        for data in TOP_COMPANIES_DATA:
            comp = db.query(Company).filter(Company.name == data["name"]).first()
            if not comp:
                comp = Company(
                    name=data["name"],
                    industry=data["industry"],
                    website=data["website"],
                    location=data["location"],
                    description=data["description"],
                    size=data["size"],
                )
                db.add(comp)
                db.flush()

            # Add jobs for this company
            for j_data in data.get("jobs", []):
                existing_job = db.query(Job).filter(
                    Job.company_id == comp.id,
                    Job.title == j_data["title"],
                ).first()
                if not existing_job:
                    job = Job(
                        company_id=comp.id,
                        title=j_data["title"],
                        description=j_data["description"],
                        required_skills=j_data["required_skills"],
                        location=j_data["location"],
                        salary_range=j_data["salary_range"],
                        job_type=j_data["job_type"],
                        status="active",
                    )
                    db.add(job)
        db.commit()


@router.get("/")
def list_companies(db: Session = Depends(get_db)):
    """List hiring partner companies across AI, Cloud, Big Tech, FinTech, and SaaS."""
    _ensure_seed_companies_and_jobs(db)
    companies = db.query(Company).all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "industry": c.industry,
            "website": c.website,
            "location": c.location,
            "description": c.description,
            "size": c.size,
            "open_roles_count": db.query(Job).filter(Job.company_id == c.id, Job.status == "active").count(),
        }
        for c in companies
    ]


@router.get("/{company_id}")
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get company profile and all open job postings."""
    comp = db.query(Company).filter(Company.id == company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    jobs = db.query(Job).filter(Job.company_id == comp.id).all()
    return {
        "id": comp.id,
        "name": comp.name,
        "industry": comp.industry,
        "website": comp.website,
        "location": comp.location,
        "description": comp.description,
        "size": comp.size,
        "jobs": [
            {
                "id": j.id,
                "title": j.title,
                "description": j.description,
                "required_skills": j.required_skills,
                "location": j.location,
                "salary_range": j.salary_range,
                "job_type": j.job_type,
                "status": j.status,
            }
            for j in jobs
        ],
    }
