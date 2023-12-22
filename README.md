# mkdocs-d2-plugin

A plugin for embedding D2 diagrams in MkDocs.

**Documentation and live demo can be found
[here](https://landmaj.github.io/mkdocs-d2-plugin/).**

## Requirements

* [MkDocs](https://www.mkdocs.org/) >= 1.5.0
* [D2](https://d2lang.com) >= 0.6.3

## Installation

Install the plugin using pip:

```bash
pip install mkdocs-d2-plugin
```

And add it to your `mkdocs.yml`:

```yaml
plugins:
  - d2
```

## Usage

### Fenced code block

````md
```d2
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
````

### Image tag

```md
![Diagram](diagram.d2)
```

## Demo app

You can find demo app in the `docs` directory.
Live version is available [here](https://landmaj.github.io/mkdocs-d2-plugin/).

To run in locally:

```bash
cd docs
python3 -m venv .venv
source .venv/bin/activate
pip install mkdocs-material mkdocs-d2-plugin
mkdocs serve
```

To run it using Docker:

```bash
cd docs
docker build --tag mkdocs-d2-plugin:latest .
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs mkdocs-d2-plugin:latest
```
