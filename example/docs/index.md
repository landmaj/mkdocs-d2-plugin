---
hide:
  - navigation
---

```d2 pad=30 scale=1.5 force_appendix=True
shape: sequence_diagram

Alice {
  link: https://en.wikipedia.org/wiki/Alice%27s_Adventures_in_Wonderland
}

John {
  tooltip: John Doe
}

Alice -> John: Hello John, how are you?
Alice -> John.ack: John, can you hear me?
John.ack -> Alice: Hi Alice, I can hear you!
John -> Alice: I feel great!
```
