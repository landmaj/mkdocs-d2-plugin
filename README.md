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
```d2 name=sequence pad=50 scale=0.5
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
</pre>

### Options
 - `name`: output file name (**required**)
 - `pad`: pixels padded around the rendered diagram (default 100, optional)
 - `scale`: e.g. 0.5 to halve the default size; -1 means that SVG's will fit to screen; etting to 1 turns off SVG fitting to screen (default -1, optional)


## Configuration
The plugin can be configured in your `mkdocs.yml` file.
```yaml
plugins:
  - d2:
      theme: 1
      sketch: False
      output_dir: assets/diagrams
```

[List of available themes](https://d2lang.com/tour/themes/)
