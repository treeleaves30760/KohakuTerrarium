"""Plugin manager — lifecycle and hook dispatch.

Three dispatch modes:
  - call_hook: fire-and-forget (lifecycle, interrupts, compaction)
  - call_hook_chain: pipeline (LLM, tools — each plugin transforms the value)

Critical: when no plugins are registered, all methods return immediately
with zero overhead. The agent loop should not slow down without plugins.
"""

import inspect
from typing import Any

from kohakuterrarium.modules.plugin.base import (
    BasePlugin,
    PluginBlockError,
    PluginContext,
)
from kohakuterrarium.utils.logging import get_logger

logger = get_logger(__name__)


class PluginManager:
    """Manages plugin lifecycle and hook dispatch."""

    def __init__(self) -> None:
        self._plugins: list[BasePlugin] = []

    def __bool__(self) -> bool:
        """Falsy when empty — allows ``if self.plugins:`` guards."""
        return len(self._plugins) > 0

    def __len__(self) -> int:
        return len(self._plugins)

    def register(self, plugin: BasePlugin) -> None:
        """Register a plugin and maintain priority order."""
        self._plugins.append(plugin)
        self._plugins.sort(key=lambda p: getattr(p, "priority", 50))
        logger.info(
            "Plugin registered",
            plugin_name=getattr(plugin, "name", "?"),
            priority=getattr(plugin, "priority", 50),
        )

    async def load_all(self, context: PluginContext) -> None:
        """Call on_load for all plugins."""
        for plugin in self._plugins:
            try:
                ctx = PluginContext(
                    agent_name=context.agent_name,
                    working_dir=context.working_dir,
                    session_id=context.session_id,
                    model=context.model,
                    _agent=context._agent,
                    _plugin_name=getattr(plugin, "name", "unnamed"),
                )
                await self._call(plugin, "on_load", context=ctx)
            except Exception:
                logger.warning(
                    "Plugin on_load failed",
                    plugin_name=getattr(plugin, "name", "?"),
                    exc_info=True,
                )

    async def unload_all(self) -> None:
        """Call on_unload for all plugins (reverse order)."""
        for plugin in reversed(self._plugins):
            try:
                await self._call(plugin, "on_unload")
            except Exception:
                logger.debug(
                    "Plugin on_unload failed",
                    plugin_name=getattr(plugin, "name", "?"),
                    exc_info=True,
                )

    async def call_hook(self, hook_name: str, **kwargs: Any) -> None:
        """Fire-and-forget: call all plugins, ignore returns.

        Used for lifecycle hooks, interrupts, compaction, event observation.
        """
        if not self._plugins:
            return

        for plugin in self._plugins:
            method = getattr(plugin, hook_name, None)
            if method is None:
                continue
            try:
                await self._call(plugin, hook_name, **kwargs)
            except Exception:
                logger.warning(
                    "Plugin hook failed",
                    plugin_name=getattr(plugin, "name", "?"),
                    hook=hook_name,
                    exc_info=True,
                )

    async def call_hook_chain(self, hook_name: str, value: Any, **kwargs: Any) -> Any:
        """Pipeline: each plugin transforms the value.

        First non-None return replaces the value for the next plugin.
        PluginBlockError propagates to the caller (tool/sub-agent blocked).
        Regular exceptions are logged and the plugin is skipped.
        """
        if not self._plugins:
            return value

        for plugin in self._plugins:
            method = getattr(plugin, hook_name, None)
            if method is None:
                continue
            try:
                result = await self._call(plugin, hook_name, value, **kwargs)
                if result is not None:
                    value = result
            except PluginBlockError:
                raise  # Propagate — caller handles as tool error
            except Exception:
                logger.warning(
                    "Plugin hook failed",
                    plugin_name=getattr(plugin, "name", "?"),
                    hook=hook_name,
                    exc_info=True,
                )

        return value

    @staticmethod
    async def _call(
        plugin: BasePlugin, method_name: str, *args: Any, **kwargs: Any
    ) -> Any:
        """Call a plugin method, handling both sync and async."""
        method = getattr(plugin, method_name, None)
        if method is None:
            return None
        if inspect.iscoroutinefunction(method):
            return await method(*args, **kwargs)
        # Sync method — call directly (don't block event loop for long)
        return method(*args, **kwargs)
