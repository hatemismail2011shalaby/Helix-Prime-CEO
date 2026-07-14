"""
Shared Memory Manager for Helix Agents
Handles all memory operations including:
- Shared memory (accessible to all agents)
- Agent-specific accomplishments
- Context tracking
- Strategic memory (SAMI only)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

class MemoryManager:
    """Central memory management for all agents"""
    
    def __init__(self, memory_dir: Optional[Path] = None):
        if memory_dir is None:
            # Default to Helix Prime CEO memory
            memory_dir = Path(__file__).parent.parent / "06_memory"
        
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.shared_memory_file = self.memory_dir / "memory.json"
        self.agent_accomplishments_file = self.memory_dir / "agent_accomplishments.json"
        self.sami_strategic_file = self.memory_dir / "sami_strategic_memory.json"
        self.agent_context_file = self.memory_dir / "agent_context.json"
    
    # ========== SHARED MEMORY ==========
    
    def get_shared_memory(self) -> Dict[str, Any]:
        """Load shared memory accessible to all agents"""
        try:
            if self.shared_memory_file.exists():
                with open(self.shared_memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
            print(f"⚠️  Error loading shared memory: {exc}")
        
        return self._init_shared_memory()
    
    def _init_shared_memory(self) -> Dict[str, Any]:
        """Initialize shared memory structure"""
        return {
            "sessions": [],
            "total_interactions": 0,
            "last_active": datetime.now().isoformat(),
            "active_context": None,
            "agents_active": ["SAMI", "WILI", "PHILI", "SUBY"],
            "shared_knowledge": {}
        }
    
    def save_shared_memory(self, memory: Dict[str, Any]) -> bool:
        """Save shared memory"""
        try:
            with open(self.shared_memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory, f, indent=2, ensure_ascii=False)
            return True
        except OSError as exc:
            print(f"❌ Error saving shared memory: {exc}")
            return False
    
    def log_session(self, agent_name: str, prompt: str, response: str) -> bool:
        """Log agent interaction to shared memory"""
        try:
            memory = self.get_shared_memory()
            memory["sessions"].append({
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "prompt": prompt,
                "response": response[:500]  # Store first 500 chars
            })
            memory["total_interactions"] += 1
            memory["last_active"] = datetime.now().isoformat()
            
            return self.save_shared_memory(memory)
        except (KeyError, TypeError, ValueError, OSError) as exc:
            print(f"❌ Error logging session: {exc}")
            return False
    
    # ========== AGENT ACCOMPLISHMENTS ==========
    
    def get_agent_accomplishments(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get accomplishments by agent"""
        try:
            if self.agent_accomplishments_file.exists():
                with open(self.agent_accomplishments_file, 'r', encoding='utf-8') as f:
                    accomplishments = json.load(f)
                
                if agent_name and agent_name in accomplishments:
                    return accomplishments[agent_name]
                
                return accomplishments
        except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
            print(f"⚠️  Error loading accomplishments: {exc}")
        
        return {}
    
    def add_accomplishment(self, agent_name: str, accomplishment: str, details: Optional[Dict] = None) -> bool:
        """Add an accomplishment for an agent"""
        try:
            accomplishments = self.get_agent_accomplishments()
            
            if agent_name not in accomplishments:
                accomplishments[agent_name] = {
                    "total": 0,
                    "items": []
                }
            
            accomplishments[agent_name]["items"].append({
                "timestamp": datetime.now().isoformat(),
                "accomplishment": accomplishment,
                "details": details or {}
            })
            accomplishments[agent_name]["total"] = len(accomplishments[agent_name]["items"])
            
            with open(self.agent_accomplishments_file, 'w', encoding='utf-8') as f:
                json.dump(accomplishments, f, indent=2, ensure_ascii=False)
            
            return True
        except (OSError, TypeError, ValueError) as exc:
            print(f"❌ Error adding accomplishment: {exc}")
            return False
    
    def get_accomplishments_summary(self, agent_name: str) -> str:
        """Get formatted summary of agent's accomplishments"""
        accomplishments = self.get_agent_accomplishments(agent_name)
        
        if not accomplishments or not accomplishments.get("items"):
            return f"No accomplishments recorded for {agent_name} yet."
        
        summary = f"📊 {agent_name}'s Accomplishments ({accomplishments['total']} total):\n"
        for i, item in enumerate(accomplishments["items"][-10:], 1):  # Last 10
            timestamp = item.get("timestamp", "").split("T")[0]
            summary += f"{i}. {item['accomplishment']} ({timestamp})\n"
        
        return summary
    
    # ========== SAMI STRATEGIC MEMORY ==========
    
    def get_sami_strategy(self) -> Dict[str, Any]:
        """Get SAMI's strategic memory"""
        try:
            if self.sami_strategic_file.exists():
                with open(self.sami_strategic_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
            print(f"⚠️  Error loading SAMI strategy: {exc}")
        
        return self._init_sami_strategy()
    
    def _init_sami_strategy(self) -> Dict[str, Any]:
        """Initialize SAMI's strategic memory"""
        return {
            "directives": [],
            "agent_assignments": {},
            "priorities": [],
            "decisions": [],
            "next_steps": []
        }
    
    def save_sami_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Save SAMI's strategic memory"""
        try:
            with open(self.sami_strategic_file, 'w', encoding='utf-8') as f:
                json.dump(strategy, f, indent=2, ensure_ascii=False)
            return True
        except OSError as exc:
            print(f"❌ Error saving SAMI strategy: {exc}")
            return False
    
    def add_directive(self, directive: str, agents: List[str], priority: str = "medium") -> bool:
        """Add a directive to SAMI's strategic memory"""
        try:
            strategy = self.get_sami_strategy()
            strategy["directives"].append({
                "timestamp": datetime.now().isoformat(),
                "directive": directive,
                "assigned_agents": agents,
                "priority": priority,
                "status": "active"
            })
            return self.save_sami_strategy(strategy)
        except (KeyError, TypeError, ValueError, OSError) as exc:
            print(f"❌ Error adding directive: {exc}")
            return False
    
    # ========== AGENT CONTEXT ==========
    
    def get_agent_context(self) -> Dict[str, Any]:
        """Get current agent context"""
        try:
            if self.agent_context_file.exists():
                with open(self.agent_context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
            print(f"⚠️  Error loading agent context: {exc}")
        
        return {
            "current_agent": None,
            "conversation_history": [],
            "active_tasks": [],
            "last_switch": None
        }
    
    def set_current_agent(self, agent_name: str) -> bool:
        """Set the current active agent"""
        try:
            context = self.get_agent_context()
            context["current_agent"] = agent_name
            context["last_switch"] = datetime.now().isoformat()
            
            with open(self.agent_context_file, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2, ensure_ascii=False)
            
            return True
        except (OSError, TypeError, ValueError) as exc:
            print(f"❌ Error setting current agent: {exc}")
            return False
    
    def add_conversation_entry(self, agent_name: str, message: str) -> bool:
        """Add to conversation history"""
        try:
            context = self.get_agent_context()
            context["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "message": message[:1000]
            })
            # Keep only last 100 entries
            context["conversation_history"] = context["conversation_history"][-100:]
            
            with open(self.agent_context_file, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2, ensure_ascii=False)
            
            return True
        except (OSError, TypeError, ValueError) as exc:
            print(f"❌ Error adding conversation entry: {exc}")
            return False
    
    # ========== CONTEXT RETRIEVAL ==========
    
    def get_all_agent_summaries(self) -> str:
        """Get summary of all agents' recent work"""
        summaries = "📋 All Agents Summary:\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        accomplishments = self.get_agent_accomplishments()
        
        for agent_name in ["SAMI", "WILI", "PHILI", "SUBY"]:
            if agent_name in accomplishments:
                items = accomplishments[agent_name].get("items", [])
                if items:
                    latest = items[-1]
                    summaries += f"✓ {agent_name}: {latest['accomplishment']}\n"
                else:
                    summaries += f"○ {agent_name}: No recent activity\n"
            else:
                summaries += f"○ {agent_name}: No activity tracked\n"
        
        return summaries
    
    def get_agent_work_summary(self, agent_name: str) -> str:
        """Get recent work summary for an agent from conversation context"""
        context = self.get_agent_context()
        
        # Get recent messages from this agent
        agent_messages = [
            e["message"] for e in context.get("conversation_history", [])
            if e.get("agent") == agent_name
        ]
        
        if not agent_messages:
            return f"No recent work from {agent_name} in current session."
        
        summary = f"🔄 {agent_name}'s Recent Work:\n"
        for i, msg in enumerate(agent_messages[-5:], 1):  # Last 5 messages
            summary += f"{i}. {msg[:100]}...\n"
        
        return summary


# Convenience singleton instance
_memory_manager = None

def get_memory_manager(memory_dir: Optional[Path] = None) -> MemoryManager:
    """Get or create the memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(memory_dir)
        return _memory_manager

    if memory_dir is not None and _memory_manager.memory_dir != memory_dir.resolve():
        _memory_manager = MemoryManager(memory_dir)

    return _memory_manager
