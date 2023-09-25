# mkdocs-d2-plugin
A plugin for the MkDocs documentation site generator which automatically
generates and embeds [D2](https://d2lang.com) diagrams.


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
The plugin will automatically generate and embed D2 diagrams from code blocks
with the `d2` language tag.

### Example
<pre>
```d2
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
</pre>


## Configuration
The plugin can be configured globally in your `mkdocs.yml` file.
```yaml
plugins:
  - d2:
      theme: 1
      sketch: False
      pad: 100
      scale: -1.0
```

Or locally in a code block.
<pre>
```d2 theme=1 sketch=true pad=100 scale=-1.0
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
</pre>

[List of available themes](https://d2lang.com/tour/themes/)
