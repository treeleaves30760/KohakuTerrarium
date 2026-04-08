"""Tests for the plugin system (manager, base class, bootstrap)."""

import pytest

from kohakuterrarium.modules.plugin.base import (
    BasePlugin,
    PluginBlockError,
    PluginContext,
)
from kohakuterrarium.modules.plugin.manager import PluginManager

# ── Test plugins ──


class CounterPlugin(BasePlugin):
    name = "counter"
    priority = 10

    def __init__(self):
        self.calls: dict[str, int] = {}

    async def on_agent_start(self):
        self.calls["agent_start"] = self.calls.get("agent_start", 0) + 1

    async def on_agent_stop(self):
        self.calls["agent_stop"] = self.calls.get("agent_stop", 0) + 1

    async def on_event(self, event=None):
        self.calls["event"] = self.calls.get("event", 0) + 1

    async def on_tool_start(self, args, tool_name="", job_id=""):
        self.calls["tool_start"] = self.calls.get("tool_start", 0) + 1
        return None

    async def on_tool_end(self, result, tool_name="", job_id=""):
        self.calls["tool_end"] = self.calls.get("tool_end", 0) + 1
        return None


class TransformPlugin(BasePlugin):
    name = "transform"
    priority = 20

    async def on_llm_start(self, messages, tools=None, model=""):
        # Append a marker to prove pipeline works
        return messages + [{"role": "system", "content": "[transformed]"}]

    async def on_tool_end(self, result, tool_name="", job_id=""):
        if hasattr(result, "output"):
            result.output = result.output + " [filtered]"
            return result
        return None


class BlockerPlugin(BasePlugin):
    name = "blocker"
    priority = 5

    async def on_tool_start(self, args, tool_name="", job_id=""):
        if tool_name == "dangerous":
            raise PluginBlockError("Tool 'dangerous' is blocked by policy")
        return None


class BuggyPlugin(BasePlugin):
    name = "buggy"
    priority = 50

    async def on_agent_start(self):
        raise RuntimeError("Plugin bug!")

    async def on_tool_start(self, args, tool_name="", job_id=""):
        raise ValueError("Another bug!")


class SyncPlugin(BasePlugin):
    """Plugin with sync methods (should still work)."""

    name = "sync_plugin"
    priority = 30

    def on_agent_start(self):
        self.started = True

    def on_tool_start(self, args, tool_name="", job_id=""):
        return {"injected": True, **args}


# ── PluginManager tests ──


class TestPluginManager:
    def test_empty_is_falsy(self):
        mgr = PluginManager()
        assert not mgr
        assert len(mgr) == 0

    def test_register_is_truthy(self):
        mgr = PluginManager()
        mgr.register(CounterPlugin())
        assert mgr
        assert len(mgr) == 1

    def test_priority_ordering(self):
        mgr = PluginManager()
        p1 = CounterPlugin()  # priority 10
        p2 = TransformPlugin()  # priority 20
        p3 = BlockerPlugin()  # priority 5
        mgr.register(p1)
        mgr.register(p2)
        mgr.register(p3)
        assert mgr._plugins[0] is p3  # priority 5 first
        assert mgr._plugins[1] is p1  # priority 10
        assert mgr._plugins[2] is p2  # priority 20


class TestCallHook:
    @pytest.mark.asyncio
    async def test_fire_and_forget(self):
        mgr = PluginManager()
        counter = CounterPlugin()
        mgr.register(counter)

        await mgr.call_hook("on_agent_start")
        assert counter.calls["agent_start"] == 1

        await mgr.call_hook("on_agent_start")
        assert counter.calls["agent_start"] == 2

    @pytest.mark.asyncio
    async def test_no_plugins_no_op(self):
        mgr = PluginManager()
        # Should not raise
        await mgr.call_hook("on_agent_start")

    @pytest.mark.asyncio
    async def test_buggy_plugin_logged_not_raised(self):
        mgr = PluginManager()
        mgr.register(BuggyPlugin())
        # Should not raise — error logged and skipped
        await mgr.call_hook("on_agent_start")

    @pytest.mark.asyncio
    async def test_multiple_plugins_all_called(self):
        mgr = PluginManager()
        c1 = CounterPlugin()
        c2 = CounterPlugin()
        c2.name = "counter2"
        c2.priority = 20
        mgr.register(c1)
        mgr.register(c2)

        await mgr.call_hook("on_event", event="test")
        assert c1.calls["event"] == 1
        assert c2.calls["event"] == 1


class TestCallHookChain:
    @pytest.mark.asyncio
    async def test_pipeline_transforms_value(self):
        mgr = PluginManager()
        mgr.register(TransformPlugin())

        messages = [{"role": "user", "content": "hello"}]
        result = await mgr.call_hook_chain(
            "on_llm_start", messages, tools=None, model="test"
        )

        assert len(result) == 2
        assert result[1]["content"] == "[transformed]"

    @pytest.mark.asyncio
    async def test_no_plugins_returns_original(self):
        mgr = PluginManager()
        result = await mgr.call_hook_chain("on_llm_start", "original")
        assert result == "original"

    @pytest.mark.asyncio
    async def test_none_return_keeps_value(self):
        mgr = PluginManager()
        mgr.register(CounterPlugin())  # on_tool_start returns None

        result = await mgr.call_hook_chain(
            "on_tool_start", {"cmd": "ls"}, tool_name="bash", job_id="j1"
        )
        assert result == {"cmd": "ls"}

    @pytest.mark.asyncio
    async def test_block_error_propagates(self):
        mgr = PluginManager()
        mgr.register(BlockerPlugin())

        with pytest.raises(PluginBlockError, match="blocked by policy"):
            await mgr.call_hook_chain(
                "on_tool_start", {}, tool_name="dangerous", job_id="j1"
            )

    @pytest.mark.asyncio
    async def test_block_error_safe_tool_passes(self):
        mgr = PluginManager()
        mgr.register(BlockerPlugin())

        result = await mgr.call_hook_chain(
            "on_tool_start", {"safe": True}, tool_name="read", job_id="j1"
        )
        assert result == {"safe": True}

    @pytest.mark.asyncio
    async def test_buggy_plugin_skipped_in_chain(self):
        mgr = PluginManager()
        mgr.register(BuggyPlugin())
        mgr.register(CounterPlugin())  # Should still run after buggy

        result = await mgr.call_hook_chain(
            "on_tool_start", {"cmd": "ls"}, tool_name="bash", job_id="j1"
        )
        assert result == {"cmd": "ls"}

    @pytest.mark.asyncio
    async def test_sync_plugin_in_chain(self):
        mgr = PluginManager()
        mgr.register(SyncPlugin())

        result = await mgr.call_hook_chain(
            "on_tool_start", {"cmd": "ls"}, tool_name="bash", job_id="j1"
        )
        assert result["injected"] is True
        assert result["cmd"] == "ls"


class TestLoadUnload:
    @pytest.mark.asyncio
    async def test_load_all(self):
        mgr = PluginManager()
        counter = CounterPlugin()
        loaded = []

        async def _on_load(context):
            loaded.append(context.agent_name)

        counter.on_load = _on_load
        mgr.register(counter)

        ctx = PluginContext(agent_name="test_agent")
        await mgr.load_all(ctx)
        assert loaded == ["test_agent"]

    @pytest.mark.asyncio
    async def test_unload_reverse_order(self):
        mgr = PluginManager()
        order = []

        p1 = BasePlugin()
        p1.name = "first"
        p1.priority = 10

        async def _unload1():
            order.append("first")

        p1.on_unload = _unload1

        p2 = BasePlugin()
        p2.name = "second"
        p2.priority = 20

        async def _unload2():
            order.append("second")

        p2.on_unload = _unload2

        mgr.register(p1)
        mgr.register(p2)
        await mgr.unload_all()
        assert order == ["second", "first"]  # Reverse priority order


# ── Bootstrap tests ──


class TestBootstrapPlugins:
    def test_empty_config(self):
        from kohakuterrarium.bootstrap.plugins import init_plugins

        mgr = init_plugins([])
        assert not mgr
        assert len(mgr) == 0

    def test_string_config_warns(self):
        from kohakuterrarium.bootstrap.plugins import init_plugins

        mgr = init_plugins(["nonexistent_builtin"])
        assert len(mgr) == 0

    def test_missing_module_warns(self):
        from kohakuterrarium.bootstrap.plugins import init_plugins

        mgr = init_plugins([{"name": "bad", "module": "", "class": ""}])
        assert len(mgr) == 0


# ── PluginContext tests ──


class TestPluginContext:
    def test_defaults(self):
        ctx = PluginContext()
        assert ctx.agent_name == ""
        assert ctx.session_id == ""

    def test_get_set_state_no_agent(self):
        ctx = PluginContext(_plugin_name="test")
        # Should not raise without agent
        assert ctx.get_state("key") is None
        ctx.set_state("key", "value")  # no-op

    def test_switch_model_no_agent(self):
        ctx = PluginContext()
        assert ctx.switch_model("gpt-5") == ""

    def test_inject_event_no_agent(self):
        ctx = PluginContext()
        ctx.inject_event(None)  # no-op, should not raise
