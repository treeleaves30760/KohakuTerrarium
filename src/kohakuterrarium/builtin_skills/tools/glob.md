---
name: glob
description: Find files matching a glob pattern
category: builtin
tags: [file, search]
---

# glob

Find files matching a glob pattern.

## WHEN TO USE

- Finding files by name or extension
- Exploring project structure
- Locating specific file types

## HOW TO USE

```
[/glob]
pattern
[glob/]
```

Or with optional parameters:

```
[/glob]
@@path=base_dir
@@limit=50
pattern
[glob/]
```

## Arguments

| Arg | Type | Description |
|-----|------|-------------|
| pattern | body | Glob pattern (required) |
| path | @@arg | Base directory (default: cwd) |
| limit | @@arg | Max results (default: 100) |

## Pattern Syntax

| Pattern | Matches |
|---------|---------|
| `*` | Any chars except `/` |
| `**` | Any chars including `/` (recursive) |
| `?` | Single character |
| `[abc]` | a, b, or c |

## Examples

```
[/glob]
**/*.py
[glob/]
```

```
[/glob]
@@path=src/components
*.ts
[glob/]
```

```
[/glob]
**/*.{json,yaml,toml}
[glob/]
```

```
[/glob]
@@path=.
@@limit=50
**/*.md
[glob/]
```

## Output Format

```
src/main.py
src/utils/helpers.py
tests/test_main.py
```

## LIMITATIONS

- Returns file paths only (not contents)
- Results sorted by modification time (newest first)

## TIPS

- Use `**/*.ext` for recursive search
- Combine with `read` to examine found files
- Use specific patterns to narrow results
