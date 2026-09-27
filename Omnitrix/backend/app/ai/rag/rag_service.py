from app.ai.rag.retriever import RAGRetriever
class RAGService:
    """
    Service layer for retrieving RAG knowledge.

    The service passes recently used topics to the retriever
    so that topic diversity can be encouraged without
    completely banning previously used topics.
    """

    def __init__(self, section: str):
        self.section = section

        self.retriever = RAGRetriever(
            section
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        used_topics: set[str] | None = None,
    ) -> list[dict]:
        """
        Retrieve relevant RAG chunks.

        used_topics contains topics that appeared in
        recently generated questions.

        These topics are NOT excluded completely.
        The retriever only applies a soft penalty.
        """

        return self.retriever.retrieve(
            query=query,
            top_k=top_k,
            used_topics=used_topics,
        )

    def retrieve_context(
        self,
        query: str,
        top_k: int = 3,
        used_topics: set[str] | None = None,
    ) -> str:
        """
        Retrieve RAG chunks and combine them into
        a single context string for the LLM.
        """

        results = self.retrieve(
            query=query,
            top_k=top_k,
            used_topics=used_topics,
        )

        if not results:
            return ""

        context_parts = []

        for index, result in enumerate(
            results,
            start=1,
        ):
            context_parts.append(
                f"[Knowledge Chunk {index}]\n"
                f"Topic: {result['topic']}\n"
                f"{result['text']}"
            )

        return "\n\n".join(
            context_parts
        )
