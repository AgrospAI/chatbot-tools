from dataclasses import dataclass
from typing import override

from fastrag.embeddings import IEmbeddings
from fastrag.serve.prompt_builder.interfaces import Context, IPromptBuilder
from fastrag.stores import IVectorStore


@dataclass
class PromptBuilder(IPromptBuilder):
    embedding_model: IEmbeddings
    vector_store: IVectorStore

    @override
    def build_prompt(
        self,
        context: str,
        question: str,
    ) -> str:
        return f"""
        You are a helpful assistant and expert in data spaces.

        Always use inline references in the form [<NUMBER OF DOCUMENT>](ref:<NUMBER OF DOCUMENT>)
        ONLY if you use information from a document. For example, if you use the information from
        Document[3], you should write [3](ref:3) at the end of the sentence where you used that
        information.
        Give a precise, accurate and structured answer without repeating the question.
        
        These are the documents:
        {context}

        Question:
        {question}

        Answer:
        """.strip()

    @override
    async def get_context(
        self,
        question: str,
    ) -> Context:
        query_embedding = await self.embedding_model.aembed_query(
            question,
        )

        results = await self.vector_store.similarity_search(
            query=question,
            query_embedding=query_embedding,
            k=5,
        )

        sources = list(doc.metadata["source"] for doc in results)
        context = "\n\n".join(
            f"Document[{i}]: {doc.page_content}" for i, doc in enumerate(results)
        )
        print(f"Found {len(sources)} sources")
        print(results)
        print(sources)
        print(context)

        return Context(
            sources=sources,
            prompt=self.build_prompt(context, question),
        )
