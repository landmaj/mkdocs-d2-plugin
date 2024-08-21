# mkdocs-d2-plugin

A plugin for embedding D2 diagrams in MkDocs.

## Flow

![Flow](flow.d2){ pad="30" }

## Requirements

* [Python](https://www.python.org/) >= 3.9
* [MkDocs](https://www.mkdocs.org/) >= 1.6.0
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

The plugin will automatically add `pymdownx.superfences` and `attr_list` to the
list of enabled markdown extensions.
