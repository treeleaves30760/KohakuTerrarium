"""Plugin protocol and base class for KohakuTerrarium.

Plugins hook into agent lifecycle events for observability, safety,
augmentation, and custom behaviors. They do NOT replace the module
system (tools, inputs, outputs, triggers) — they intercept the
interactions *between* modules.

Two error types:
  - PluginBlockError: policy rejection → becomes tool result the model sees
  - Regular Exception: plugin bug → logged and skipped, never reaches model
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class PluginBlockError(Exception):
    """Raised by a plugin to block tool/sub-agent execution.

    The error message is returned to the model as the tool result,
    so the model can adjust its approach. Only meaningful in
    ``on_tool_start`` and ``on_subagent_start`` hooks.
    """


@dataclass
class PluginContext:
    """Context provided to plugins on load.

    Read access to agent state + controlled write methods.
    No raw agent reference — plugins cannot access conversation,
    controller, or executor directly.
    """

    agent_name: str = ""
    working_dir: Path = field(default_factory=Path.cwd)
    session_id: str = ""
    model: str = ""

    # Internal references (set by bootstrap, not by plugins)
    _agent: Any = field(default=None, repr=False)

    def switch_model(self, name: str) -> str:
        """Switch the LLM model. Returns resolved model name."""
        if self._agent and hasattr(self._agent, "switch_model"):
            return self._agent.switch_model(name)
        return ""

    def inject_event(self, event: Any) -> None:
        """Push a trigger event into the agent's event queue."""
        if self._agent and hasattr(self._agent, "controller"):
            self._agent.controller.push_event_sync(event)

    def get_state(self, key: str) -> Any:
        """Read plugin-scoped state from session store."""
        if (
            self._agent
            and hasattr(self._agent, "session_store")
            and self._agent.session_store
        ):
            full_key = f"plugin:{self._plugin_name}:{key}"
            return self._agent.session_store.state.get(full_key)
        return None

    def set_state(self, key: str, value: Any) -> None:
        """Write plugin-scoped state to session store."""
        if (
            self._agent
            and hasattr(self._agent, "session_store")
            and self._agent.session_store
        ):
            full_key = f"plugin:{self._plugin_name}:{key}"
            self._agent.session_store.state[full_key] = value

    _plugin_name: str = field(default="", repr=False)


class BasePlugin:
    """Base class for plugins. Override only the hooks you need.

    All hooks are async. Sync plugins can override with regular methods —
    the manager wraps them automatically.
    """

    name: str = "unnamed"
    priority: int = 50  # Lower = earlier. Default 50.

    # ── Lifecycle ──

    async def on_load(self, context: PluginContext) -> None:
        """Called when plugin is loaded into an agent."""

    async def on_unload(self) -> None:
        """Called when agent shuts down."""

    async def on_agent_start(self) -> None:
        """Called after agent.start() completes."""

    async def on_agent_stop(self) -> None:
        """Called before agent.stop() begins."""

    # ── LLM hooks (pipeline) ──

    async def on_llm_start(
        self, messages: list[dict], tools: list | None, model: str
    ) -> list[dict] | None:
        """Before LLM call. Return modified messages or None to keep original."""
        return None

    async def on_llm_end(self, response: str, usage: dict, model: str) -> str | None:
        """After LLM response. Return modified text or None."""
        return None

    # ── Tool hooks (pipeline, PluginBlockError to block) ──

    async def on_tool_start(
        self, args: dict, tool_name: str, job_id: str
    ) -> dict | None:
        """Before tool execution. Return modified args or None.
        Raise PluginBlockError to block execution."""
        return None

    async def on_tool_end(self, result: Any, tool_name: str, job_id: str) -> Any | None:
        """After tool execution. Return modified result or None."""
        return None

    # ── Sub-agent hooks (pipeline) ──

    async def on_subagent_start(
        self, task: str, name: str, is_background: bool
    ) -> str | None:
        """Before sub-agent spawn. Return modified task or None.
        Raise PluginBlockError to block."""
        return None

    async def on_subagent_end(self, result: Any, name: str, job_id: str) -> Any | None:
        """After sub-agent completes. Return modified result or None."""
        return None

    # ── Backgroundify (fire-and-forget) ──

    async def on_task_promoted(self, job_id: str, tool_name: str) -> None:
        """Called when a direct task is promoted to background."""

    # ── Event (callback — observe only) ──

    async def on_event(self, event: Any) -> None:
        """Called on incoming trigger event. Cannot modify or block."""

    # ── Output (pipeline) ──

    async def on_output(self, text: str, target: str) -> str | None:
        """Before output is written. Return modified text or None."""
        return None

    # ── Interrupt (fire-and-forget) ──

    async def on_interrupt(self) -> None:
        """Called when user interrupts the agent."""

    # ── Compact (fire-and-forget) ──

    async def on_compact_start(self, context_length: int) -> None:
        """Called before context compaction."""

    async def on_compact_end(self, summary: str, messages_removed: int) -> None:
        """Called after context compaction."""
