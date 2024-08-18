# Usage

There are two ways to use the plugin, both documented below.
The end result is exactly the same, so which one you choose is a
matter of personal preference.

## Fenced code blocks

Fenced code blocks allow you to place diagram definitions in markdown.

````md
```d2
shape: sequence_diagram
Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
````

## Image tags

You can also link to external files using an image tag. Only local
files with `.d2` extension are supported.

```md
![Diagram](diagram.d2)
```

Path to diagram must be relative to the markdown file.
Given following documentation structure:

```md
├── guide
│   ├── configuration.md
│   └── usage.md
├── flow.d2
└── index.md
```

To link to `flow.d2` from `usage.md` you would use:

```md
![Diagram](../flow.d2)
```

### Imports

Diagrams included using image tags support [imports](https://d2lang.com/tour/imports).

````md
importer.d2
```d2
a: @imported
a -> b
```

imported.d2
```d2
x: {
    shape: circle
}
```

In MkDocs:
![Diagram](../importer.d2)
````

![Diagram with import](importer.d2){pad="20" scale="1"}

!!! warning
    This feature is somehwat broken due to caching of rendered diagrams.
    Diagrams are not re-rendered when an imported file changes. You can either update
    the main diagram (re-render is triggered by modification time, no changes
    are needed) or [disable the cache](configuration.md#cache) altogether.
