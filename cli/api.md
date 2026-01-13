External services (those one which connect to third party APIs):

- LLM
- Vector Store
- Embedding Model

Artifacts:

- Document: basic unit of data (text, metadata, uri, etc)
- Source: where to get documents from (sitemap, url list, pdf folder, etc) and how to fetch, parse and chunk them.

Components involved when doing RAG:

- Store:
  - Embedding: convert text to vectors
  - Vector Store: store and retrieve vectors
- Indexing: fill the vector store with data
  - Sources:
    - Fetching: getting raw data from source.
    - Parsing: extracting text and metadata from raw data: create Documents.
    - Chunking: splitting Documents into smaller Documents.
- Retrieval: getting relevant documents from vector store.
  - Retriever: how to get relevant documents (similarity search, hybrid search, etc). It can apply techniques like re-ranking, filtering, etc.
- Querying: using LLM to answer questions based on retrieved documents.
  - LLM: large language model to generate answers
  - Prompt Template: template to format the prompt for the LLM
  - Tooling: using external tools to enhance the LLM capabilities (e.g., calculators, search engines, etc.)
- Benchmarking: evaluating the performance of the RAG system.
  - Dataset: collection of questions and expected answers to evaluate against.
  - Metrics: criteria to measure performance (accuracy, latency, cost, etc).

Project structure:

- .cache/
- tests/
- core/
- artifacts/
  - document.py
  - source.py
- steps/
  - base.py
  - fetching/
    - base.py
    - url_fetcher.py
    - sitemap_fetcher.py
  - parsing/
    - base.py
    - html_parser.py
    - pdf_parser.py
  - chunking/
    - base.py
    - recursive_text_splitter.py
    - default_splitter.py
  - embedding/
    - base.py
    - default_embedder.py
  - storing/
    - base.py
    - vectorstore_storer.py
  - querying/
    - base.py
    - default_querier.py
  - benchmarking/
    - base.py
    - benchmarker.py
- services/
  - base.py
  - llm/
    - base.py
    - openai.py
    - openrouter.py
  - vectorstore/
    - base.py
    - pinecone.py
    - milvus.py
  - embedding/
    - base.py
    - openwebui.py
    - openai.py
- indexing/
  - indexer.py
- retrieval/
  - retriever.py
- cli/
  - main.py
  - config.py
  - commands/
    - query.py
    - benchmark.py
- .env

Indexing:

```python
from fastrag.indexing import Indexer
from fastrag.artifacts import Source
from fastrag.steps.fetching import URLFetcher
from fastrag.steps.parsing import HTMLParser
from fastrag.steps.chunking import RecursiveChunker
from fastrag.services.embedding import OpenAIEmbedding
from fastrag.services.artifacts import Store
from fastrag.services.vectorstores import Milvus

store = Store(
    embedding=OpenAIEmbedding(),
    vector_store=Milvus()
)

sources = [Source(
    fetching=SitemapFetcher(url="https://example.com/sitemap.xml"),
    parsing=HTMLParser(),
    chunking=RecursiveChunker(chunk_size=500)
)]

indexer = Indexer(
    name="sitemap_recursive_500_openai",
    collection_name="my_collection" # default: name,
    sources=sources,
    store=store
)

await indexer.arun()
```

Custom fetching:

```python
from fastrag.steps.fetching import Fetcher

class SitemapFetcher(Fetcher):
  def fetch(self) -> list[Document]:
    ...

class URLFetcher(Fetcher):
  def fetch(self) -> list[Document]:
    ...
```

Custom Chunker:

```python
from fastrag.chunking import Chunker

class SemanticChunker(Chunker):
    name = "semantic"

    def chunk(self, document: Document) -> list[Document]:
        ...
```

Querying:

```python
from fastrag.strategies import QueryStrategy
from fastrag.llms import OpenWebUILLM

querying = QueryStrategy(
    store=store,
    llm=OpenWebUILLM(),
    prompt_template="You are a helpful assistant...",
)

querying.save("id")
response = querying.ask("What is fastrag?")
```

Serve ask endpoint:

```python
from fastrag import QueryStrategy
from fastrag.services import QueryServer

querying = QueryStrategy.load("id")
server = QueryServer(querying=querying, host="0.0.0.0", port=8000)
server.run()
```

Benchmarking:

```python
from fastrag.benchmarking import Benchmark
from fastrag.datasets import QADataset

benchmark = Benchmark(
    dataset=QADataset.from_json("eval.json"),
    metrics=["accuracy", "faithfulness"]
)

indexing = IndexingStrategy.load("id")
querying = QueryStrategy.load("id")

results = benchmark.run(
    indexing=indexing,
    querying=querying
)

results.save("benchmark_results.json")
```

Options:

1. CLI with config file to define pipelines
2. Python SDK to define pipelines programmatically
