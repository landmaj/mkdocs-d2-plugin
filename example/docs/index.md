---
hide:
  - navigation
---

# mkdocs-d2-plugin

A plugin for embedding D2 diagrams in MkDocs.

## Flow

![Flow](flow.d2){ pad="30" }

## Requirements

* [MkDocs](https://www.mkdocs.org/) >= 1.4.0
* [D2](https://d2lang.com)

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

There are two ways to use the plugin:

* fenced code block
* image tag

The end result is exactly the same, so which one you choose is a matter of
personal preference.

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

Only files with `.d2` extension are processed.

## Configuration

The plugin can be configured in your `mkdocs.yml` file.

```yaml
plugins:
  - d2:
      executable: d2
      layout: dagre
      theme: 0
      dark_theme: False
      sketch: False
      pad: 100
      scale: -1.0
      force_appendix: False
```

Run `d2 --help` for more information about the options.

Everything (except executable path) can be overriden locally.

### Fenced code block

````md
```d2 pad="20" scale="0.8"
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
````

```d2 pad="20" scale="0.8"
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```

**Quotes around values are mandatory.**
Without them, the plugin will fail silently. This is due to
[SuperFences](https://facelessuser.github.io/pymdown-extensions/extensions/superfences/).
If someone knows how to fix this, please open an issue or a PR.

There is one special option, available only in fenced code blocks:

````md
```d2 render="False"
Bob -> Alice
```
````

This option disables rendering of the diagram, but still allows you to use
`d2` language tag to highlight the code.

### Image tag

```md
![Diagram](diagram.d2){sketch="True" pad="30")
```

Contrary to fenced code blocks, quotes around values are optional. However
**white space before opening brace is not allowed**. Blame
[attr_list](https://python-markdown.github.io/extensions/attr_list/).

## Example

You can find example app in the `example` directory.
Live version is available [here](https://landmaj.github.io/mkdocs-d2-plugin/).

To run in locally:

```bash
cd example
python3 -m venv .venv
source .venv/bin/activate
pip install mkdocs-material mkdocs-d2-plugin
mkdocs serve
```

To run it using Docker:

```bash
cd example
docker build --tag mkdocs-d2-plugin:latest .
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs mkdocs-d2-plugin:latest
```

## Known issues I plan to fix

* [Layered diagrams](https://d2lang.com/tour/composition/) (animations) are not supported.
  D2 does not allow outputing such diagrams to stdout.
* Image tags require paths relative to base docs directory.
