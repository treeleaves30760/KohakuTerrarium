"""Plugin command — list and toggle plugins at runtime."""

from kohakuterrarium.builtins.user_commands import register_user_command
from kohakuterrarium.modules.user_command.base import (
    BaseUserCommand,
    CommandLayer,
    UserCommandContext,
    UserCommandResult,
    ui_info_panel,
)


@register_user_command("plugin")
class PluginCommand(BaseUserCommand):
    name = "plugin"
    aliases = ["plugins"]
    description = "List plugins or toggle enable/disable"
    layer = CommandLayer.AGENT

    async def _execute(
        self, args: str, context: UserCommandContext
    ) -> UserCommandResult:
        if not context.agent:
            return UserCommandResult(error="No agent context.")

        mgr = context.agent.plugins
        if not mgr:
            return UserCommandResult(output="No plugins loaded.")

        parts = args.strip().split(maxsplit=1)
        subcmd = parts[0] if parts else ""

        # /plugin toggle <name>
        if subcmd == "toggle" and len(parts) > 1:
            name = parts[1].strip()
            if mgr.is_enabled(name):
                mgr.disable(name)
                return UserCommandResult(output=f"Plugin '{name}' disabled.")
            elif mgr.enable(name):
                await mgr.load_pending()
                return UserCommandResult(output=f"Plugin '{name}' enabled.")
            else:
                return UserCommandResult(error=f"Plugin not found: {name}")

        # /plugin enable <name>
        if subcmd == "enable" and len(parts) > 1:
            name = parts[1].strip()
            if mgr.enable(name):
                await mgr.load_pending()
                return UserCommandResult(output=f"Plugin '{name}' enabled.")
            return UserCommandResult(error=f"Plugin not found: {name}")

        # /plugin disable <name>
        if subcmd == "disable" and len(parts) > 1:
            name = parts[1].strip()
            if mgr.disable(name):
                return UserCommandResult(output=f"Plugin '{name}' disabled.")
            return UserCommandResult(error=f"Plugin not found: {name}")

        # /plugin (list)
        plugins = mgr.list_plugins()
        if not plugins:
            return UserCommandResult(output="No plugins loaded.")

        fields = []
        for p in plugins:
            status = "enabled" if p["enabled"] else "disabled"
            fields.append(
                {"key": p["name"], "value": f"{status} (priority {p['priority']})"}
            )

        lines = [
            f"{'enabled' if p['enabled'] else 'disabled':>8}  {p['name']}"
            for p in plugins
        ]
        lines.append("")
        lines.append("Use /plugin toggle <name> to enable/disable")

        return UserCommandResult(
            output="\n".join(lines),
            data=ui_info_panel("Plugins", fields),
        )
