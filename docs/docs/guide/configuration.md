# Configuration

## Global config

Global configuration is done in `mkdocs.yml` file. It will be applied to
all diagrams in the project. To override it for a single diagram, see local
configuration for fenced code blocks and image tags below.

```yaml
plugins:
  - d2:
      executable: d2 # path to d2 executable
      cache: True
      cache_dir: .config/plugin/d2
      layout: dagre
      theme: 0
      dark_theme: False
      sketch: False
      pad: 100
      scale: -1.0
      force_appendix: False
```

If an option is not specified, default value (seen above) will be used.

Run `d2 --help` for more information about the options.

### Cache

Caching is enabled by default. It is recommended to keep it enabled to
speed up the build process. By default, cache is stored in `.cache`
directory, similar to other MkDocs plugins. For this reason it's recommended
to add `.cache` to `.gitignore` file.

If you want to pregenerate cache and use it on a different machine, make
sure both systems use the same [backend](https://docs.python.org/3/library/dbm.html).

## Local config

You can override locally everything except:

* `executable`
* `cache`
* `cache_dir`

### Fenced code blocks

Configuration options are specified as key="value" pairs after the
language tag.

````md
```d2 pad="20" scale="0.8"
Bob -> Alice
```
````

**Quotes around values are mandatory.** Without them,
the plugin will fail silently. If you know how to change this behavior of
[SuperFences](https://facelessuser.github.io/pymdown-extensions/extensions/superfences/),
please let me know by opening an issue or a PR.

There is one special option, `render="False"`, available only in fenced code blocks.
This option disables rendering of the diagram and allows you to display
the diagram definition instead.

#### Examples

##### Padding and scale

````md
```d2 pad="20" scale="0.7"
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
````

```d2 pad="20" scale="0.7"
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```

##### Disabled rendering

````md
```d2 render="False"
Bob -> Alice
```
````

```d2 render="False"
Bob -> Alice
```

### Image tags

Image tags use [attr_list](https://python-markdown.github.io/extensions/attr_list/)
extension to specify configuration options.

```md
![Diagram](diagram.d2){sketch="True" pad="30"}
```

Contrary to fenced code blocks, quotes around values are optional. However
**white space before opening brace is not allowed**. Add space and you will
se no error but the diagram will be rendered with global configuration only.

#### Examples

##### Padding and scale

```md
![Cloud](cloud.d2){pad="30" scale="0.8}
```

![Cloud](cloud.d2){pad="30" scale="0.8"}

##### Theme and layout

```md
![Cloud](cloud.d2){theme=101 layout=elk}
```

![Cloud](cloud.d2){theme=101 layout=elk}
