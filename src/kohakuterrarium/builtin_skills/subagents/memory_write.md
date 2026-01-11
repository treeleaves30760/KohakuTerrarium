---
name: memory_write
description: Store information to memory system
category: subagent
tags: [memory, storage, persistence]
---

# memory_write

Sub-agent for storing and updating information in the memory folder.

## WHEN TO USE

- Storing new facts or information
- Updating existing memory files
- Recording user preferences
- Saving conversation context

## WHEN NOT TO USE

- Just reading information (use memory_read)
- Modifying protected files
- Writing outside memory folder

## HOW TO USE

```
[/memory_write]
what to store
[memory_write/]
```

## Arguments

| Arg | Type | Description |
|-----|------|-------------|
| body | content | What information to store and where |

## Examples

```
[/memory_write]
Remember that the user prefers dark mode
[memory_write/]
```

```
[/memory_write]
Update context with current project: KohakuTerrarium
[memory_write/]
```

```
[/memory_write]
Save preference: user likes concise responses
[memory_write/]
```

```
[/memory_write]
Add to facts: user is working on an agent framework
[memory_write/]
```

## CAPABILITIES

The memory_write sub-agent has access to:
- `tree` - List files in memory folder
- `read` - Read existing content
- `write` - Create new files
- `edit` - Modify existing files

It will:
1. Check existing memory structure
2. Determine appropriate file to update/create
3. Write content with proper format

## FILE FORMAT

Memory files use markdown with frontmatter:

```markdown
---
title: Title
summary: Brief description
protected: false
updated: 2024-01-15
---

Content here...
```

## LIMITATIONS

- Cannot modify protected files (character.md, rules.md)
- Only writes to configured memory path
- Respects file access rules from config
