# FastRAG CLI
[![PyPI](https://img.shields.io/pypi/v/fastrag-cli?label=pypi&style=flat-square)](https://pypi.org/project/fastrag-cli/)

**Installation**

```bash
pip install fastrag-cli
# or
uv add fastrag-cli
```

## General Usage

Generally to use the CLI you will need a configuration file. The default plugins provide a `yaml` configuration reader, but it can be of any format, as long as you provide an `IConfigLoader` that can handle it.

To run fastrag with our default toy workflow with verbosity.

```bash
fastrag run -v
```

To run your own configuration workflow `config.yaml` with verbosity.

```bash
fastrag run -v config.yaml
```

To run your own configuration workflow `config.yaml` and stop execution after *Step 1*.

```bash
fastrag run -v config.yaml --step 1
```

Delete the cached files after all these executions (with prompt)

```bash
fastrag clean
```

Delete the cached files (without prompt)

```bash
fastrag clean -y
```

To serve the inference endpoints

```bash
fastrag serve
```

## Documentation

To generate the [automatic documentation](USAGE.md)

```bash
typer ./fastrag/__main__.py utils docs > USAGE.md
```

## Architecture

Being able to expand the workflow execution capabilities means to understand how it works, 

