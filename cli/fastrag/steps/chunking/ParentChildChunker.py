import uuid
from typing import List
from fastrag.chunking.model import Chunk
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_experimental.text_splitter import SemanticChunker

class ParentChildChunker:
    def __init__(self, embedding_model): # Constructor
        self.embedding_model = embedding_model

        # Splitter for parent
        self.parent_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )

        # Splitter for child
        self.child_splitter = SemanticChunker(
            embeddings=embedding_model,
            breakpoint_threshold_type="percentile" # Looks to 5% of the top highly differences sentences
        )

    def process_markdown(self, markdown_text: str, source_name: str = "unknown") -> List[Chunk]:
        all_chunks = []
        # Split markdown depending on headers "#","##","###"
        parent_chunks = self.parent_splitter.split_text(markdown_text)

        for p_chunk in parent_chunks:
            headers = [
                p_chunk.metadata.get("Header 1", ""),
                p_chunk.metadata.get("Header 2", ""),
                p_chunk.metadata.get("Header 3", "")
            ]
            title_path = " > ".join(filter(None, headers)) # Construct title path like 'Header 1 < Header 2 < Header 3'            
            p_chunk.page_content = title_path + "\n\n" + p_chunk.page_content
            parent_id = str(uuid.uuid4())
            parent_metadata = p_chunk.metadata.copy()
            parent_metadata.update({
                "source": source_name,
                "chunk_type": "parent_context",
                "length": len(p_chunk.page_content),
                "title_path": title_path
            })

            parent_chunk = Chunk(
                chunk_id=parent_id,
                content=p_chunk.page_content,
                metadata=parent_metadata,
                level="parent"
            )
            
            all_chunks.append(parent_chunk)

            has_table = "| ---" in p_chunk.page_content or ("|" in p_chunk.page_content and "\n|" in p_chunk.page_content)
            has_code = "```" in p_chunk.page_content
            
            is_short = len(p_chunk.page_content) < 200
            if has_table or has_code or is_short:
                 self._create_single_child(p_chunk.page_content, parent_id, parent_metadata, all_chunks)
                 continue

            try:
                # Uses embedding model to split the child semantically
                child_chunks = self.child_splitter.create_documents([p_chunk.page_content])
            except Exception as e:
                print(f"Warning: Semantic chunking failed for parent {parent_id}, falling back.")
                # If couldn't split, just create entire child as one chunk
                self._create_single_child(p_chunk.page_content, parent_id, parent_metadata, all_chunks)
                continue

            for i, c_chunk in enumerate(child_chunks):
                child_metadata = parent_metadata.copy()
                child_metadata.update({
                    "chunk_type": "child_retrieval",
                    "child_index": i,
                    "parent_id": parent_id
                })

                # For the rest of the child chunks, reinject the title for context
                if i > 0 and title_path:
                    c_chunk.page_content = title_path + "\n\n" + c_chunk.page_content

                child_chunk = Chunk(
                    chunk_id=str(uuid.uuid4()),
                    content=c_chunk.page_content,
                    metadata=child_metadata,
                    parent_id=parent_id,
                    level="child"
                )
                all_chunks.append(child_chunk)

        return all_chunks

    def _create_single_child(self, content, parent_id, metadata, output_list):
        child_metadata = metadata.copy()
        child_metadata.update({"chunk_type": "child_retrieval", "parent_id": parent_id})
        output_list.append(Chunk(
            chunk_id=str(uuid.uuid4()),
            content=content,
            metadata=child_metadata,
            parent_id=parent_id,
            level="child"
        ))