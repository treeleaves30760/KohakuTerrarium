"""Bootstrap plugin loading from agent config."""

import importlib
from typing import Any

from kohakuterrarium.core.loader import ModuleLoader
from kohakuterrarium.modules.plugin.base import BasePlugin
from kohakuterrarium.modules.plugin.manager import PluginManager
from kohakuterrarium.utils.logging import get_logger

logger = get_logger(__name__)


def init_plugins(
    plugin_configs: list[dict[str, Any]],
    loader: ModuleLoader | None = None,
) -> PluginManager:
    """Create and populate a PluginManager from config entries.

    Each entry in plugin_configs follows the same pattern as tools::

        - name: cost_tracker          # builtin (future)
        - name: my_plugin
          type: custom
          module: ./plugins/my_plugin.py
          class: MyPlugin
          options: {budget: 5.0}
        - name: pkg_plugin
          type: package
          module: my_pack.plugins.guard
          class: PermissionGuard
          options: {}

    Returns an empty PluginManager if no configs (zero overhead).
    """
    manager = PluginManager()

    if not plugin_configs:
        return manager

    for cfg in plugin_configs:
        if isinstance(cfg, str):
            # Short form: just a name (builtin lookup, future)
            logger.warning("Builtin plugin not found", plugin_name=cfg)
            continue

        name = cfg.get("name", "")
        ptype = cfg.get("type", "custom")
        module = cfg.get("module", "")
        class_name = cfg.get("class", cfg.get("class_name", ""))
        options = cfg.get("options", {})

        if not module or not class_name:
            logger.warning("Plugin missing module/class", plugin_name=name)
            continue

        try:
            if loader:
                plugin = loader.load_instance(
                    module, class_name, module_type=ptype, options=options
                )
            else:
                mod = importlib.import_module(module)
                cls = getattr(mod, class_name)
                plugin = cls(options=options) if options else cls()

            if not isinstance(plugin, BasePlugin):
                logger.warning(
                    "Plugin does not extend BasePlugin",
                    plugin_name=name,
                    plugin_type=type(plugin).__name__,
                )
                continue

            if not getattr(plugin, "name", "") or plugin.name == "unnamed":
                plugin.name = name

            manager.register(plugin)

        except Exception:
            logger.warning(
                "Failed to load plugin",
                plugin_name=name,
                module=module,
                exc_info=True,
            )

    return manager
