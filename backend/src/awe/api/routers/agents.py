"""Agent API endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from awe.api.deps import get_agent_dirs
from awe.api.schemas import AgentSummary
from awe.config.loader import find_agent, load_all_agents

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=list[AgentSummary])
async def list_agents(
    agent_dirs: list[Path] = Depends(get_agent_dirs),
) -> list[AgentSummary]:
    """List all available agent definitions."""
    agents = load_all_agents(agent_dirs)
    return [
        AgentSummary(
            name=agent.name,
            role=agent.role,
            model_id=agent.model.id,
            capabilities_tags=agent.capabilities.tags,
        )
        for agent in agents.values()
    ]


@router.get("/{name}", response_model=AgentSummary)
async def get_agent(
    name: str,
    agent_dirs: list[Path] = Depends(get_agent_dirs),
) -> AgentSummary:
    """Get a single agent definition."""
    try:
        agent = find_agent(name, agent_dirs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    return AgentSummary(
        name=agent.name,
        role=agent.role,
        model_id=agent.model.id,
        capabilities_tags=agent.capabilities.tags,
    )
