"""
Inline output module. Claude Code / Codex CLI-style terminal output.

Streams text inline (no alternate screen buffer), shows tool activity
with args and output previews, renders markdown for completed text.
Works over SSH/tmux/any terminal. Uses Rich for styling.
"""

import sys

from rich.console import Console
from rich.markdown import Markdown as RichMarkdown
from rich.panel import Panel
from rich.text import Text

from kohakuterrarium.modules.output.base import BaseOutputModule
from kohakuterrarium.utils.logging import get_logger

logger = get_logger(__name__)


class InlineOutput(BaseOutputModule):
    """Inline terminal output using Rich. No alternate screen buffer.

    Config:
        output:
          type: inline
    """

    def __init__(self, **options):
        super().__init__()
        self._console = Console(highlight=False)
        self._text_buffer: list[str] = []
        self._in_turn = False

    async def _on_start(self) -> None:
        logger.debug("Inline output started")

    async def _on_stop(self) -> None:
        if self._in_turn:
            self._end_turn()
        logger.debug("Inline output stopped")

    async def on_user_input(self, text: str) -> None:
        """Render user input as a panel (overwrites the raw prompt line)."""
        if not text:
            return
        # Move cursor up to overwrite the prompt line that prompt_toolkit wrote
        sys.stdout.write("\033[A\033[2K")
        sys.stdout.flush()
        self._console.print(
            Panel(
                text,
                title="[bold cyan]You[/]",
                title_align="left",
                border_style="cyan",
                padding=(0, 1),
            )
        )

    async def on_processing_start(self) -> None:
        self._text_buffer.clear()

    async def on_processing_end(self) -> None:
        self._flush_text_as_markdown()
        if self._in_turn:
            self._end_turn()

    async def write(self, content: str) -> None:
        if content:
            self._ensure_turn()
            self._text_buffer.append(content)

    async def write_stream(self, chunk: str) -> None:
        if chunk:
            self._ensure_turn()
            self._text_buffer.append(chunk)

    async def flush(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def _ensure_turn(self) -> None:
        if not self._in_turn:
            self._in_turn = True

    def _end_turn(self) -> None:
        self._console.print()
        self._in_turn = False

    def _flush_text_as_markdown(self) -> None:
        """Render accumulated text as markdown via Rich."""
        if not self._text_buffer:
            return
        text = "".join(self._text_buffer).strip()
        self._text_buffer.clear()
        if not text:
            return
        try:
            self._console.print(RichMarkdown(text))
        except Exception:
            self._console.print(text)

    # ── Activity rendering ──────────────────────────────────────

    def on_activity(self, activity_type: str, detail: str) -> None:
        name, rest = _parse_detail(detail)
        # Flush buffered text before showing activity
        self._flush_text_as_markdown()
        self._ensure_turn()
        _render_activity(self._console, activity_type, name, rest)

    def on_activity_with_metadata(
        self, activity_type: str, detail: str, metadata: dict
    ) -> None:
        name, rest = _parse_detail(detail)
        self._flush_text_as_markdown()
        self._ensure_turn()
        _render_activity(self._console, activity_type, name, rest, metadata)

    # ── Resume history rendering ────────────────────────────────

    async def on_resume(self, events: list[dict]) -> None:
        """Render session history with full detail."""
        if not events:
            return

        turns = _group_into_turns(events)
        if not turns:
            return

        self._console.print()
        header = Text()
        header.append(" Resumed session ", style="bold reverse")
        header.append(f"  {len(turns)} turns", style="dim")
        self._console.print(header)
        self._console.print()

        for turn in turns:
            _render_turn(self._console, turn)

        sep = Text("\u2500" * 50, style="dim")
        self._console.print(sep)
        self._console.print()


# ── Helpers ─────────────────────────────────────────────────────


def _parse_detail(detail: str) -> tuple[str, str]:
    """Extract [name] prefix from detail string.

    Detail format: "[tool_name[job_id]] arg_preview" or "[tool_name] rest".
    Strips the [job_id] suffix to get a clean tool name.
    """
    if detail.startswith("["):
        try:
            end = detail.index("]", 1)
            raw_name = detail[1:end]
            rest = detail[end + 2 :]
            # Strip job_id suffix: "info[9b4270" -> "info"
            if "[" in raw_name:
                raw_name = raw_name[: raw_name.index("[")]
            return raw_name, rest
        except (ValueError, IndexError):
            pass
    return "unknown", detail


def _render_activity(
    console: Console,
    activity_type: str,
    name: str,
    rest: str,
    metadata: dict | None = None,
) -> None:
    """Render a single activity event to console."""
    metadata = metadata or {}

    match activity_type:
        case "tool_start":
            t = Text("  \u25cb ", style="dim cyan")
            t.append(name, style="bold cyan")
            # Show key args
            args_preview = _format_args_preview(name, metadata.get("args", {}))
            if args_preview:
                t.append(f"  {args_preview}", style="dim")
            elif rest:
                t.append(f"  {rest[:80]}", style="dim")
            console.print(t)

        case "tool_done":
            t = Text("  \u25cf ", style="green")
            t.append(name, style="bold cyan")
            if rest:
                preview = rest[:100].replace("\n", " ")
                t.append(f"  {preview}", style="dim")
            console.print(t)

        case "tool_error":
            t = Text("  \u2717 ", style="red")
            t.append(name, style="bold red")
            if rest:
                t.append(f"  {rest[:100]}", style="red")
            console.print(t)

        case "subagent_start":
            console.print()
            t = Text("  \u25b7 ", style="dim magenta")
            t.append(name, style="bold magenta")
            task = metadata.get("task", rest)
            if task:
                t.append(f"  {task[:80]}", style="dim")
            console.print(t)

        case "subagent_done":
            result = metadata.get("result", rest)
            tools_used = metadata.get("tools_used", [])
            t = Text("  \u25b6 ", style="green")
            t.append(name, style="bold magenta")
            if tools_used:
                t.append(f"  [{', '.join(tools_used)}]", style="dim")
            console.print(t)
            # Show result preview indented
            if result:
                preview = str(result)[:200].strip()
                if preview:
                    for line in preview.split("\n")[:3]:
                        console.print(Text(f"    {line}", style="dim"))
            console.print()

        case "subagent_error":
            t = Text("  \u2717 ", style="red")
            t.append(name, style="bold red")
            if rest:
                t.append(f"  {rest[:100]}", style="red")
            console.print(t)
            console.print()

        # Sub-agent's internal tool activity (nested)
        case s if s.startswith("subagent_tool_"):
            sub_name = metadata.get("subagent", "")
            tool_name = metadata.get("tool", "")
            sub_detail = metadata.get("detail", rest)
            sub_activity = s.replace("subagent_", "")

            if sub_activity == "tool_start":
                t = Text("    \u251c\u2500 \u25cb ", style="dim")
                t.append(tool_name, style="cyan")
                if sub_detail:
                    t.append(f"  {sub_detail[:60]}", style="dim")
                console.print(t)
            elif sub_activity == "tool_done":
                t = Text("    \u251c\u2500 \u25cf ", style="dim green")
                t.append(tool_name, style="cyan")
                if sub_detail:
                    preview = sub_detail[:60].replace("\n", " ")
                    t.append(f"  {preview}", style="dim")
                console.print(t)
            elif sub_activity == "tool_error":
                t = Text("    \u251c\u2500 \u2717 ", style="red")
                t.append(tool_name, style="bold red")
                console.print(t)

        case _:
            pass


def _format_args_preview(tool_name: str, args: dict) -> str:
    """Format tool args as a concise preview string."""
    if not args:
        return ""
    match tool_name:
        case "bash":
            return args.get("command", "")[:80]
        case "read":
            path = args.get("path", "")
            offset = args.get("offset")
            limit = args.get("limit")
            suffix = ""
            if offset or limit:
                suffix = f" ({offset or 0}:{(offset or 0) + (limit or 0)})"
            return f"{path}{suffix}"
        case "write":
            return args.get("path", "")[:80]
        case "edit":
            return args.get("file_path", args.get("path", ""))[:80]
        case "glob":
            return args.get("pattern", "")[:80]
        case "grep":
            pattern = args.get("pattern", "")
            path = args.get("path", "")
            return f'"{pattern}" {path}'.strip()[:80]
        case "send_message":
            ch = args.get("channel", "")
            return f"-> {ch}"
        case "think":
            thought = str(args.get("thought", args.get("content", "")))
            return thought[:60]
        case _:
            # Generic: show first key=value pair
            for k, v in args.items():
                if k == "content":
                    continue
                return f"{k}={str(v)[:50]}"
            return ""


# ── Resume rendering ────────────────────────────────────────────


def _render_turn(console: Console, turn: dict) -> None:
    """Render one conversation turn with full detail."""
    # User input / trigger
    if turn["input_type"] == "user_input":
        console.print(
            Panel(
                turn["input"],
                title="[bold cyan]You[/]",
                title_align="left",
                border_style="cyan",
                padding=(0, 1),
            )
        )
    else:
        console.print(
            Panel(
                turn["input"][:300],
                title="[bold yellow]Trigger[/]",
                title_align="left",
                border_style="yellow",
                padding=(0, 1),
            )
        )

    # Tool calls with args and output
    in_subagent = False
    for evt in turn["events"]:
        etype = evt.get("type", "")

        if etype == "tool_call":
            name = evt.get("name", "tool")
            args = evt.get("args", {})
            t = Text("  \u25cb ", style="dim cyan")
            t.append(name, style="bold cyan")
            args_preview = _format_args_preview(name, args)
            if args_preview:
                t.append(f"  {args_preview}", style="dim")
            console.print(t)

        elif etype == "tool_result":
            name = evt.get("name", "tool")
            output = evt.get("output", "")
            error = evt.get("error")
            if error:
                t = Text("  \u2717 ", style="red")
                t.append(name, style="bold red")
                t.append(f"  {str(error)[:100]}", style="red")
                console.print(t)
            else:
                t = Text("  \u25cf ", style="green")
                t.append(name, style="bold cyan")
                # Show output preview
                if output:
                    lines = str(output).strip().split("\n")
                    line_count = len(lines)
                    if line_count <= 1:
                        preview = lines[0][:100]
                        t.append(f"  {preview}", style="dim")
                    else:
                        t.append(f"  ({line_count} lines)", style="dim")
                console.print(t)

        elif etype == "subagent_call":
            in_subagent = True
            name = evt.get("name", "subagent")
            task = evt.get("task", "")
            console.print()
            t = Text("  \u25b7 ", style="dim magenta")
            t.append(name, style="bold magenta")
            if task:
                t.append(f"  {task[:80]}", style="dim")
            console.print(t)

        elif etype == "subagent_result":
            name = evt.get("name", "subagent")
            tools = evt.get("tools_used", [])
            output = evt.get("output", "")
            turns_count = evt.get("turns", 0)
            t = Text("  \u25b6 ", style="green")
            t.append(name, style="bold magenta")
            parts = []
            if tools:
                parts.append(", ".join(tools))
            if turns_count:
                parts.append(f"{turns_count} turns")
            if parts:
                t.append(f"  [{'; '.join(parts)}]", style="dim")
            console.print(t)
            # Show result preview
            if output:
                preview = str(output).strip()[:200]
                if preview:
                    for line in preview.split("\n")[:3]:
                        console.print(Text(f"    {line}", style="dim"))
            console.print()
            in_subagent = False

        elif etype == "subagent_tool":
            tool_name = evt.get("tool_name", "")
            activity = evt.get("activity", "")
            if activity == "tool_start":
                t = Text("    \u251c\u2500 \u25cb ", style="dim")
                t.append(tool_name, style="cyan")
                console.print(t)
            elif activity == "tool_done":
                t = Text("    \u251c\u2500 \u25cf ", style="dim green")
                t.append(tool_name, style="cyan")
                console.print(t)
            elif activity == "tool_error":
                t = Text("    \u251c\u2500 \u2717 ", style="red")
                t.append(tool_name, style="bold red")
                console.print(t)

    # Assistant text (rendered as markdown)
    text = "".join(turn["text_parts"]).strip()
    if text:
        console.print()
        try:
            console.print(RichMarkdown(text))
        except Exception:
            console.print(text)

    console.print()


def _group_into_turns(events: list[dict]) -> list[dict]:
    """Group session events into turns for resume display.

    Each turn has input, text_parts, and a full events list
    preserving all tool/subagent events with their data.
    """
    turns: list[dict] = []
    current: dict | None = None

    for evt in events:
        etype = evt.get("type", "")
        if etype == "user_input":
            if current:
                turns.append(current)
            current = {
                "input_type": "user_input",
                "input": evt.get("content", ""),
                "text_parts": [],
                "events": [],
            }
        elif etype == "trigger_fired":
            if current:
                turns.append(current)
            ch = evt.get("channel", "")
            sender = evt.get("sender", "")
            content = evt.get("content", "")
            current = {
                "input_type": "trigger",
                "input": f"[{ch}] {sender}: {content}",
                "text_parts": [],
                "events": [],
            }
        elif current is not None:
            if etype == "text":
                current["text_parts"].append(evt.get("content", ""))
            elif etype in (
                "tool_call",
                "tool_result",
                "subagent_call",
                "subagent_result",
                "subagent_tool",
            ):
                current["events"].append(evt)

    if current:
        turns.append(current)
    return turns
