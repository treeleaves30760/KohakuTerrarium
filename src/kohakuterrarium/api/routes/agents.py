"""Standalone agent routes."""

from fastapi import APIRouter, Depends, HTTPException

from kohakuterrarium.api.deps import get_manager
from kohakuterrarium.api.schemas import (
    AgentChat,
    AgentCreate,
    ModelSwitch,
    SlashCommand,
)

router = APIRouter()


@router.post("")
async def create_agent(req: AgentCreate, manager=Depends(get_manager)):
    """Create and start a standalone agent."""
    try:
        agent_id = await manager.agent_create(
            config_path=req.config_path, llm_override=req.llm, pwd=req.pwd
        )
        return {"agent_id": agent_id, "status": "running"}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("")
async def list_agents(manager=Depends(get_manager)):
    """List all running agents."""
    return manager.agent_list()


@router.get("/{agent_id}")
async def get_agent(agent_id: str, manager=Depends(get_manager)):
    """Get status of a specific agent."""
    try:
        return manager.agent_status(agent_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{agent_id}")
async def stop_agent(agent_id: str, manager=Depends(get_manager)):
    """Stop and cleanup an agent."""
    try:
        await manager.agent_stop(agent_id)
        return {"status": "stopped"}
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/{agent_id}/interrupt")
async def interrupt_agent(agent_id: str, manager=Depends(get_manager)):
    """Interrupt the agent's current processing. Agent stays alive."""
    try:
        manager.agent_interrupt(agent_id)
        return {"status": "interrupted"}
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/{agent_id}/promote/{job_id}")
async def promote_task(agent_id: str, job_id: str, manager=Depends(get_manager)):
    """Promote a running direct task to background."""
    try:
        session = manager._agents.get(agent_id)
        if not session:
            raise ValueError(f"Agent {agent_id} not found")
        ok = session.agent._promote_handle(job_id)
        return {"status": "promoted" if ok else "not_found"}
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/{agent_id}/plugins")
async def list_plugins(agent_id: str, manager=Depends(get_manager)):
    """List plugins and their enabled/disabled status."""
    session = manager._agents.get(agent_id)
    if not session:
        raise HTTPException(404, f"Agent {agent_id} not found")
    if not session.agent.plugins:
        return []
    return session.agent.plugins.list_plugins()


@router.post("/{agent_id}/plugins/{plugin_name}/toggle")
async def toggle_plugin(agent_id: str, plugin_name: str, manager=Depends(get_manager)):
    """Enable or disable a plugin at runtime."""
    session = manager._agents.get(agent_id)
    if not session:
        raise HTTPException(404, f"Agent {agent_id} not found")
    if not session.agent.plugins:
        raise HTTPException(404, "No plugins loaded")
    mgr = session.agent.plugins
    if mgr.is_enabled(plugin_name):
        mgr.disable(plugin_name)
        return {"name": plugin_name, "enabled": False}
    else:
        mgr.enable(plugin_name)
        await mgr.load_pending()
        return {"name": plugin_name, "enabled": True}


@router.get("/{agent_id}/jobs")
async def agent_jobs(agent_id: str, manager=Depends(get_manager)):
    """List running background jobs for an agent."""
    try:
        return manager.agent_get_jobs(agent_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/{agent_id}/tasks/{job_id}/stop")
async def stop_agent_task(agent_id: str, job_id: str, manager=Depends(get_manager)):
    """Stop a specific background task."""
    try:
        if await manager.agent_cancel_job(agent_id, job_id):
            return {"status": "cancelled", "job_id": job_id}
        raise HTTPException(404, f"Task not found or already completed: {job_id}")
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/{agent_id}/history")
async def agent_history(agent_id: str, manager=Depends(get_manager)):
    """Get conversation history + event log for a standalone agent."""
    try:
        history = manager.agent_get_history(agent_id)
        return {"agent_id": agent_id, "events": history}
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/{agent_id}/model")
async def switch_agent_model(
    agent_id: str, req: ModelSwitch, manager=Depends(get_manager)
):
    """Switch the agent's LLM model mid-session."""
    try:
        model = manager.agent_switch_model(agent_id, req.model)
        return {"status": "switched", "model": model}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{agent_id}/command")
async def execute_command(
    agent_id: str, req: SlashCommand, manager=Depends(get_manager)
):
    """Execute a slash command on an agent (e.g. /model, /status)."""
    try:
        return await manager.agent_execute_command(agent_id, req.command, req.args)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{agent_id}/chat")
async def chat_agent(agent_id: str, req: AgentChat, manager=Depends(get_manager)):
    """Non-streaming chat with an agent."""
    try:
        chunks = []
        async for chunk in manager.agent_chat(agent_id, req.message):
            chunks.append(chunk)
        return {"response": "".join(chunks)}
    except ValueError as e:
        raise HTTPException(404, str(e))
