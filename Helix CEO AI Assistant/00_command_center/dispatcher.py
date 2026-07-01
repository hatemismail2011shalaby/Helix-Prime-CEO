"""
Dispatcher module for routing tasks to appropriate agents based on capabilities.
"""

from typing import Dict, List, Any, Optional

def select_agent(task: str, registry: Dict[str, Dict[str, Any]]) -> Optional[str]:
    active_agents = get_active_agents(registry)
    if not active_agents:
        return None
    
    task_keywords = set(task.lower().split())
    for agent_name in active_agents:
        agent = registry[agent_name]
        capabilities = agent.get("capabilities", [])
        capability_keywords = set(capability.lower() for capability in capabilities)
        if capability_keywords & task_keywords:
            return agent_name
    return active_agents[0]

def get_active_agents(registry: Dict[str, Dict[str, Any]]) -> List[str]:
    return [agent_name for agent_name, agent in registry.items() if agent.get("status") == "active"]