# chatbot-tools
Monorepo with our tools to build RAG chatbots from dynamic sources.

## [FastRAG CLI](cli/README.md)
[![PyPI](https://img.shields.io/pypi/v/fastrag-cli?label=pypi&style=flat-square)](https://pypi.org/project/fastrag-cli/)

CLI tool that leverages the execution of RAG generation workflows using configuration files. This tool will help you with:

1. Declare and gather different sources of data, both locally and remotely.
1. Parse this data into a LLM friendly format (MarkDown).
1. Chunk the data with your desired chunking strategy.
1. Embed the chunks with your model and upload them to your vector store.
1. Serve an API to make prompts making use of your vector store.

[Read more on its usage and examples](cli/README.md)


**Features**

- **Expandability** Every step of the workflow can we tweaked and expanded thanks to its *Plugin Architecture*, allowing end-customers to add new steps and implementations.
- **Declarative workflow orchestration** The behaviour of the system is controlled by configuration files, making the executions really flexible and reproducible.
- **Traceability** We grant that the resulting chunks of information are fully traceable to their sources.


