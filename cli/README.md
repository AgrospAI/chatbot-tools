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


To run your own configuration workflow `config.yaml` with verbosity.

```bash
fastrag run -v config.yaml
```

Delete the cached files after all these executions (with prompt)

```bash
fastrag clean config.yaml
```

Delete the cached files (without prompt)

```bash
fastrag clean -y config.yaml
```

To serve the inference endpoints

```bash
fastrag serve config.yaml
```

## Documentation

To generate the [automatic documentation](USAGE.md)

```bash
typer ./fastrag/__main__.py utils docs > USAGE.md
```

## Architecture

The main benefit of using plugins is being able to expand the workflow execution capabilities, which requires to understand how it works, as of now, the core components forming FastRAG are:

- **_ICache_** handles the caching capabilities of the workflow.
  - Implementation provided for `LocalCache (supported="local")`.
- **_IConfigLoader_** provides a loading method to transform the given config file into a configuration object.
  - Implementation provided for `YamlLoader (supported=[".yaml", ".yml"])` (will decide based on configuration file extension).
- **_IRunner_** orchestrates the steps in the configuration object.
  - Implementation provided for `AsyncRunner (supported="async")`.
- **_IStep_** defines the tasks to be performed in every step, handles the communication of data between steps.
  - Implementation provided for `Fetching (supported="fetching")`, `Parsing (supported="parsing")`, `Chunking (supported="chunking")`, `Embedding (supported="embedding")` and `Benchmarking (supported="benchmarking")`.
- **_Task_** executes the declared task.
  - Implementation provided for:
    - `Fetching`:
      - `HttpFetcher (supported=["URL"])`
      - `LocalFetcher (supported=["Path"]) `
      - `SitemapXMLFetcher (supported=["SitemapXML"])`
      - `CrawlerFetcher (supported=["Crawling"]) `
    - `Parsing`:
      - `HtmlParser (supported=["HtmlParser"])`
      - `FileParser (supported=["FileParser"])`
    - `Chunking`:
      - `ParentChildChunker (supported=["ParentChild"])`
      - `RecursiveChunker (supported=["RecursiveChunker"])`
      - `SlidingWindowChunker (supported=["SlidingWindow"])`
    - `Embedding`:
      - `OpenAISimple (supported=["OpenAI-Simple", "openai-simple"])`
    - `Benchmarking`:
      - `ChunkQualityBenchmarking (supported=["ChunkQuality"])`
      - `QuerySetBenchmarking (supported=["QuerySet"])`
    

Providing a new implementation for any of these components is as easy as inheriting from them and executing _fastRAG_ with the plugin base dir as:

```bash
fastrag run config.yaml --plugins <IMPLEMENTATION_DIR> -v
```

### Implementing Tasks

The most generic components are Tasks, since they do from fetching from a URL, to parsing HTML to Markdown, to creating embeddings; hence we will make an example of `Task` implementation:

```python
@dataclass(frozen=True)
class HttpFetcher(Task):
    supported: ClassVar[str] = "URL"

    url: URLField = URLField()
    _cached: bool = field(init=False, default=False, hash=False, compare=False)

    @override
    async def run(self) -> Run:
        if self.cache.is_present(self.url):
            object.__setattr__(self, "_cached", True)
            return

        try:
            async with AsyncClient(timeout=10) as client:
                res = await client.get(self.url)
        except Exception as e:
            yield Event(Event.Type.EXCEPTION, f"ERROR: {e}")
            return

        entry = await self.cache.create(
            self.url,
            res.text.encode(),
            {
                "step": "fetching",
                "format": "html",
                "strategy": HttpFetcher.supported,
            },
        )

        self.result = entry.path

    @override
    def completed_callback(self) -> Event:
        return Event(
            Event.Type.COMPLETED,
            f"{'Cached' if self._cached else 'Fetched'} {self.url}",
        )
```

#### Plugin Architecture

Here we can see a few things, first of all, we have our class which inherits from `Task` which will register the implementation, to do so it's also needed to specify a `supported` attribute.

```python
class HttpFetcher(Task):
    # It supports using it as URL
    supported: str = "URL"

class HttpFetcher(Task):
    # It supports using both URL or HTTP
    supported: str = ["URL", "HTTP"]

@dataclass(frozen=True)
class HttpFetcher(Task):
    # The same but with dataclasses
    supported: ClassVar[str] = "URL"
```

This `supported` attribute is the one that must match the configuration step strategy and will be used when deciding which implementation to use.

```yaml
# config.yaml
steps:
  fetching:
    - strategy: URL # Must match this
    - strategy: HTTP # or this
```

#### Initialization and Arguments

Although it depends of the `Step` implementation, generally when defining the tasks to perform, upon injecting the needed implementations, the class will be provided with its constructor parameters from the given configuration object, in this case, it will pass the `url` argument.

```yaml
# config.yaml
steps:
  fetching:
      - strategy: URL
          params:
            url: https://agrospai.udl.cat
      - strategy: HTTP
          params:
            url: https://agrospai.udl.cat
```

#### Task Methods

As of the `run` method, which is inherited from `Task`, it's the one supposed to do the heavy-lifting. There are two cases, the shown, which is the simpler, where it does not recieve any parameters, and another on which will be discussed later.

```python
@override
async def run(self) -> AsyncGenerator[Event, None]:
    ...
```

As shown in the type hinting, the method is expected to _yield_ events, we provide an event base class and some subclasses for each workflow step. These events are nothing but feedback to show in the terminal (behaviour defined in `Step`). In this shown example, we only show feedback upon failure.

```python
async def run(self) -> AsyncGenerator[Event, None]:
    ...
    except Exception as e:
        yield Event(Event.Type.EXCEPTION, f"ERROR: {e}")
        return
```

Once the main purpose of this `Task` is finished, we must also define a `completed_callback` method which, instead of yielding, returns a feedback event.

```python
@override
def completed_callback(self) -> Event:
    return Event(
        Event.Type.COMPLETED,
        f"{'Cached' if self._cached else 'Fetched'} {self.url}",
    )
```

#### Task Communication

Apart from executing as supposed and giving feedback, a `Task` is expected to communicate with other steps, otherwise it wouldn't be a workflow. To do so, it should make use of the **cache**, as in the shown example:

Firstly, for skipping the execution if the expected result is already cached to save time and resources. Secondly, to cache the results to use in the next steps.

```python
async def run(self) -> AsyncGenerator[Event, None]:
    if self.cache.is_present(self.url):
        object.__setattr__(self, "_cached", True)
        return
```

```python
async def run(self) -> AsyncGenerator[Event, None]:
    ...
    await self.cache.create(
        self.url,
        res.text.encode(),
        "fetching",
        {"format": "html", "strategy": HttpFetcher.supported},
    )
```

The cache main methods are those two:

- `is_present`: Check for cache entry existence given a **URI**. Also checks for lifetime validity in case of `LocalCache`.
- `create`: Creates a new cache entry given its **uri** (in this case the url), **contents**, **step** (in this case fetching) and **metadata** (arbitrary data). Besides the given data, the entries will also contain a **timestamp** and **path**.

Now that we have covered how to make a simple `Task` for http retrieving, we will cover how to make other kind of tasks that depend on previous results (cache entries). As commented earlier, there are two ways of using `callback`, the simpler way, without any arguments, and the following.

We will present you with another `Task` example, this time the `HtmlParser`. In this case, the purpose of this task is to transform **HTML** files into **Markdown**, since LLMs like Markdown better. To do this task, we need to access the previous fetching step results, since this is a common occurence in multiple steps, it has been abstracted away.

```python
@dataclass(frozen=True)
class HtmlParser(Task):
    supported: ClassVar[str] = "HtmlParser"
    filter: ClassVar[Filter] = MetadataFilter(step="fetching", format="html")

    @override
    async def run(
        self,
        uri: str,
        entry: CacheEntry,
    ) -> AsyncGenerator[Event, None]:
        ...
```

As we can see in the previous code, there are two main differences with the `HttpFetcher`. Firstly, the definition of the `filter` attribute, and lastly, the `callback` method signature.

```python
@override
async def run(
    self,
    uri: str,
    entry: CacheEntry,
) -> AsyncGenerator[Event, None]:
    ...
```

This method signature implies that the data (cache entry) is being passed to the function call and that the task implementation doesn't have to worry about it. To declare which subset of Cache Entries the task instance will process, a `filter` class attribute is defined. This `filter` is an instance of `Filter[CacheEntry]`, which will be used to filter out the cache entries that are fitted to use in this task. The responsable of doing this labor is the `Step` implementation, which will gather all the relevant cache entries.

```python
# Rewrote for non-dataclasses
filter: Filter = MetadataFilter(step="fetching", format="html")
```

This `filter` uses a special subclass of `Filter`, the `MetadataFilter`, which only accepts the cache entries that have the given _kwargs_ in their metadata. The operator `&` joins both filters in an `AndFilter`, which is a basic filter that ensures all its sub-filters accept the given entry for it to accept it, in case it's needed, there is also an `OrFilter` with the operator `|`.

> **NOTE** that for every entry compliant with the given filter, with the default `Step` implementations, an `asyncio.Task` will be created and waited for.
