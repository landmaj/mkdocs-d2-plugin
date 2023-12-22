# mkdocs-d2-plugin

A plugin for embedding D2 diagrams in MkDocs.

## Flow

![Flow](flow.d2){ pad="30" }

## Requirements

* [MkDocs](https://www.mkdocs.org/) >= 1.5.0
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

The plugin will automatically add `pymdownx.superfences` and `attr_list` to the
list of enabled markdown extensions.
