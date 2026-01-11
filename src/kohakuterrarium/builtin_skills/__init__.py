"""
Builtin skills - default documentation for builtin tools and subagents.

These files are packaged with the library and serve as default documentation.
Users can override them by placing files in their agent's prompts/tools/ folder.
"""

from pathlib import Path

# Path to builtin skills directory
BUILTIN_SKILLS_DIR = Path(__file__).parent


def get_builtin_tool_doc(name: str) -> str | None:
    """
    Get builtin tool documentation by name.

    Args:
        name: Tool name (e.g., "bash", "read")

    Returns:
        Documentation content or None if not found
    """
    doc_path = BUILTIN_SKILLS_DIR / "tools" / f"{name}.md"
    if doc_path.exists():
        return doc_path.read_text(encoding="utf-8")
    return None


def get_builtin_subagent_doc(name: str) -> str | None:
    """
    Get builtin subagent documentation by name.

    Args:
        name: Subagent name

    Returns:
        Documentation content or None if not found
    """
    doc_path = BUILTIN_SKILLS_DIR / "subagents" / f"{name}.md"
    if doc_path.exists():
        return doc_path.read_text(encoding="utf-8")
    return None


def list_builtin_tool_docs() -> list[str]:
    """List all builtin tool names that have documentation."""
    tools_dir = BUILTIN_SKILLS_DIR / "tools"
    if not tools_dir.exists():
        return []
    return [p.stem for p in tools_dir.glob("*.md")]


def list_builtin_subagent_docs() -> list[str]:
    """List all builtin subagent names that have documentation."""
    subagents_dir = BUILTIN_SKILLS_DIR / "subagents"
    if not subagents_dir.exists():
        return []
    return [p.stem for p in subagents_dir.glob("*.md")]


def get_all_tool_docs(tool_names: list[str] | None = None) -> dict[str, str]:
    """
    Get documentation for multiple tools.

    Args:
        tool_names: List of tool names, or None for all builtin tools

    Returns:
        Dict of tool_name -> documentation
    """
    if tool_names is None:
        tool_names = list_builtin_tool_docs()

    docs = {}
    for name in tool_names:
        doc = get_builtin_tool_doc(name)
        if doc:
            docs[name] = doc
    return docs


def get_all_subagent_docs(subagent_names: list[str] | None = None) -> dict[str, str]:
    """
    Get documentation for multiple subagents.

    Args:
        subagent_names: List of subagent names, or None for all builtin

    Returns:
        Dict of subagent_name -> documentation
    """
    if subagent_names is None:
        subagent_names = list_builtin_subagent_docs()

    docs = {}
    for name in subagent_names:
        doc = get_builtin_subagent_doc(name)
        if doc:
            docs[name] = doc
    return docs
