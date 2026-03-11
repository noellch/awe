"""YAML configuration loader for pipelines and agent profiles."""

from __future__ import annotations

from pathlib import Path

import yaml

from awe.models.agent import AgentProfile
from awe.models.pipeline import Pipeline


def load_pipeline(path: Path) -> Pipeline:
    """Load a pipeline definition from a YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return Pipeline(**data)


def load_agent(path: Path) -> AgentProfile:
    """Load an agent profile from a YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return AgentProfile(**data)


def find_pipeline(name: str, search_dirs: list[Path]) -> Pipeline:
    """Find and load a pipeline by name from search directories."""
    for directory in search_dirs:
        for ext in (".yaml", ".yml"):
            path = directory / f"{name}{ext}"
            if path.exists():
                return load_pipeline(path)
    raise FileNotFoundError(
        f"Pipeline '{name}' not found in: {[str(d) for d in search_dirs]}"
    )


def find_agent(name: str, search_dirs: list[Path]) -> AgentProfile:
    """Find and load an agent profile by name from search directories."""
    for directory in search_dirs:
        for ext in (".yaml", ".yml"):
            path = directory / f"{name}{ext}"
            if path.exists():
                return load_agent(path)
    raise FileNotFoundError(
        f"Agent '{name}' not found in: {[str(d) for d in search_dirs]}"
    )


def load_all_agents(search_dirs: list[Path]) -> dict[str, AgentProfile]:
    """Load all agent profiles from search directories."""
    agents: dict[str, AgentProfile] = {}
    for directory in search_dirs:
        if not directory.exists():
            continue
        for path in directory.glob("*.yaml"):
            agent = load_agent(path)
            agents[agent.name] = agent
        for path in directory.glob("*.yml"):
            agent = load_agent(path)
            agents[agent.name] = agent
    return agents
