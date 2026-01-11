---
name: read
description: Read file contents with optional line range
category: builtin
tags: [file, io]
---

# read

Read file contents with optional line range.

## WHEN TO USE

- Examining source code or config files
- Checking file contents before editing
- Reading logs or text data
- Understanding existing code

## HOW TO USE

```
[/read]
@@path=file_path
[read/]
```

Or with optional parameters:

```
[/read]
@@path=file_path
@@offset=10
@@limit=20
[read/]
```

## Arguments

| Arg | Type | Description |
|-----|------|-------------|
| path | @@arg | Path to file (required) |
| offset | @@arg | Starting line (0-based, default: 0) |
| limit | @@arg | Max lines to read (default: all) |

## Examples

```
[/read]
@@path=src/main.py
[read/]
```

```
[/read]
@@path=src/main.py
@@offset=10
@@limit=20
[read/]
```

## Output Format

```
     1→first line content
     2→second line content
     3→...
```

## LIMITATIONS

- UTF-8 encoding (binary files show replacement chars)
- Very large files should use offset/limit

## TIPS

- Use `glob` first to find files
- Use `grep` to locate relevant lines, then `read` to examine
- For large files, read in chunks with offset/limit
