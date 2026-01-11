import uuid
import json
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from fastrag.steps.chunking.model import Chunk 
from langchain_huggingface import HuggingFaceEmbeddings


def chunker_logic(text: str, source_name: str, embedding_model_name: str) -> bytes:
    
    embed_model = HuggingFaceEmbeddings(model_name=embedding_model_name)
    
    parent_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    )
    child_splitter = SemanticChunker(
        embeddings=embed_model,
        breakpoint_threshold_type="percentile"
    )

    all_chunks = []
    parent_docs = parent_splitter.split_text(text)

    for p_doc in parent_docs:
        headers = [p_doc.metadata.get(k, "") for k in ["Header 1", "Header 2", "Header 3"]]
        title_path = " > ".join(filter(None, headers))
        
        parent_content = f"Context: {title_path}\n\n{p_doc.page_content}" if title_path else p_doc.page_content
        parent_id = str(uuid.uuid4())
        
        all_chunks.append({
            "chunk_id": parent_id,
            "content": parent_content,
            "metadata": {**p_doc.metadata, "source": source_name, "chunk_type": "parent", "title_path": title_path},
            "level": "parent",
            "parent_id": None
        })

        if "| ---" in p_doc.page_content or "```" in p_doc.page_content:
             all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "content": parent_content,
                "metadata": {**p_doc.metadata, "source": source_name, "chunk_type": "child"},
                "level": "child",
                "parent_id": parent_id
             })
             continue

        try:
            child_docs = child_splitter.create_documents([p_doc.page_content])
        except Exception:
            child_docs = [p_doc]

        for i, c_doc in enumerate(child_docs):
            child_content = c_doc.page_content
            if title_path and not child_content.startswith("Context:"):
                 child_content = f"Context: {title_path}\n{child_content}"

            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "content": child_content,
                "metadata": {**p_doc.metadata, "source": source_name, "chunk_type": "child", "child_index": i},
                "level": "child",
                "parent_id": parent_id
            })

    return json.dumps(all_chunks).encode("utf-8")
