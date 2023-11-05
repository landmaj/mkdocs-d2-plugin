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
