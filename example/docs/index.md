---
hide:
  - navigation
---

# mkdocs-d2-plugin

## Summary

To add diagrams to your documentation, place them in fenced code blocks with the language `d2`. The plugin will compile the diagram and replace the fenced code block with an inlined svg.

You can use links to redirect users to external resources or other pages/sections of your documentation.

## Diagram

```d2 pad="30"
shape: sequence_diagram

md: Markdown {
  link: "#source"
  tooltip: "Click on me to navigate to diagram source"
}
mkdocs: MkDocs {
  link: https://www.mkdocs.org
}
plugin: mkdocs-d2-plugin {
  link: https://github.com/landmaj/mkdocs-d2-plugin
}
d2: D2 {
  link: https://d2lang.com
}

mkdocs->mkdocs: build/serve
mkdocs->plugin: markdown files
plugin->md: regex

subprocess: {
  link: https://docs.python.org/3/library/subprocess.html
  plugin->d2.sub: compile
  d2.sub->plugin: svg
}

plugin->md: replace fenced code block\nwith inlined svg
```

## Source

```d2 render="False"
shape: sequence_diagram

md: Markdown {
  link: "#source"
  tooltip: "Click on me to navigate to diagram source"
}
mkdocs: MkDocs {
  link: https://www.mkdocs.org
}
plugin: mkdocs-d2-plugin {
  link: https://github.com/landmaj/mkdocs-d2-plugin
}
d2: D2 {
  link: https://d2lang.com
}

mkdocs->mkdocs: build/serve
mkdocs->plugin: markdown files
plugin->md: regex

subprocess: {
  link: https://docs.python.org/3/library/subprocess.html
  plugin->d2.sub: compile
  d2.sub->plugin: svg
}

plugin->md: replace fenced code block\nwith inlined svg
```
