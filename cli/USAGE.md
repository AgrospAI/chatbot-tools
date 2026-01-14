# CLI

FastRAG CLI

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `serve`: Start the FastRAG API server for question...
* `clean`: Clean the cache
* `run`: Go through the process of generating a...

## `serve`

Start the FastRAG API server for question answering.

**Usage**:

```console
$ serve [OPTIONS] [CONFIG]
```

**Arguments**:

* `[CONFIG]`: Path to the config file.  [default: /Users/spin3l/Documents/_dev/AgrospAI/chatbot-tools/cli/resources/config.yaml]

**Options**:

* `-p, --plugins PATH`: Path to the plugins directory.
* `-h, --host TEXT`: Host to bind the server to.  [default: 0.0.0.0]
* `--port INTEGER`: Port to bind the server to.  [default: 8000]
* `-r, --reload`: Enable auto-reload for development.
* `-v, --verbose`: Verbose prints
* `--help`: Show this message and exit.

## `clean`

Clean the cache

**Usage**:

```console
$ clean [OPTIONS] [CONFIG]
```

**Arguments**:

* `[CONFIG]`: Path to the config file.  [default: /Users/spin3l/Documents/_dev/AgrospAI/chatbot-tools/cli/resources/config.yaml]

**Options**:

* `-y, --yes`
* `-p, --plugins PATH`: Path to the plugins directory.
* `--help`: Show this message and exit.

## `run`

Go through the process of generating a fastRAG.

**Usage**:

```console
$ run [OPTIONS] [CONFIG]
```

**Arguments**:

* `[CONFIG]`: Path to the config file.  [default: /Users/spin3l/Documents/_dev/AgrospAI/chatbot-tools/cli/resources/config.yaml]

**Options**:

* `-p, --plugins PATH`: Path to the plugins directory.
* `-v, --verbose`: Verbose prints
* `--help`: Show this message and exit.

