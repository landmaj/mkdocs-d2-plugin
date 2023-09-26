# mkdocs-d2-plugin
A plugin for the MkDocs documentation site generator which automatically
generates and embeds [D2](https://d2lang.com) diagrams.


## Requirements
* [MkDocs](https://www.mkdocs.org/) >= 1.4.0
* [Pydantic](https://pydantic-docs.helpmanual.io/)
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
The plugin will automatically generate and embed D2 diagrams from code blocks
with the `d2` language tag.

````
```d2
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
````


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
````
```d2 sketch=true force_appendix=True
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
````

[List of available themes](https://d2lang.com/tour/themes/)


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


### \<rant\>
Why this fenced code block format?
````
```d2 key=value
[...]
```
````
MkDocs uses [python-markdown](https://python-markdown.github.io/extensions/fenced_code_blocks/)
library, which expects key-value pairs in a following format:
````
```{ .d2 key="value" }
[...]
```
````

This breaks syntax highlighting in most editors. The format used by this plugin
breaks python-markdown library instead, however the entire code block is 
replaced anyway, so it doesn't matter. And according to 
[CommonMark specification](https://spec.commonmark.org/0.30/#info-string)
it is a valid Markdown.
### \</rant\>
