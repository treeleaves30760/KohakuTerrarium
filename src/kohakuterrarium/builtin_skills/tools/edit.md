---
name: edit
description: Edit file using unified diff format
category: builtin
tags: [file, io, edit, diff, patch]
---

# edit

Apply unified diff patches to modify files precisely.

## WHEN TO USE

- Modifying existing code (functions, classes, etc.)
- Fixing bugs in existing files
- Adding/removing lines at specific locations
- Making targeted, precise changes

## HOW TO USE

```
[/edit]
@@path=file_path
@@ -start,count +start,count @@
-removed line
+added line
 context line
[edit/]
```

## Arguments

| Arg | Type | Description |
|-----|------|-------------|
| path | @@arg | Path to file (required) |
| content | body | Unified diff content |

## Diff Format

Standard unified diff format:

```
@@ -start,count +start,count @@
```

- **`-start,count`**: Starting line and number of lines in original
- **`+start,count`**: Starting line and number of lines in new version
- Lines starting with `-` are **removed**
- Lines starting with `+` are **added**
- Lines starting with ` ` (space) are **context** (must match exactly)

## Examples

### Replace a function

```
[/edit]
@@path=src/main.py
@@ -5,3 +5,3 @@
-def hello():
-    print("Hi")
+def hello():
+    print("Hello, World!")
[edit/]
```

### Add import after existing import

```
[/edit]
@@path=src/utils.py
@@ -1,1 +1,2 @@
 import os
+import sys
[edit/]
```

### Delete lines

```
[/edit]
@@path=src/old.py
@@ -10,3 +10,1 @@
 # Keep this comment
-# Delete this
-# And this
[edit/]
```

### Multiple changes in one diff

```
[/edit]
@@path=src/app.py
@@ -1,2 +1,3 @@
 import os
+import json
 import sys
@@ -20,2 +21,2 @@
-    return None
+    return {}
[edit/]
```

## Output Format

```
Edited /path/to/file.py
  2 hunk(s) applied
  +5 -3 lines
```

## TIPS

- Use `[/read]@@path=file.py[read/]` first to see exact line numbers
- Include context lines (` ` prefix) to anchor changes
- Line numbers in `@@` header are 1-indexed
- Multiple hunks can be in one diff

## LIMITATIONS

- Context lines must match the file exactly
- Cannot create new files (use `write` for that)
