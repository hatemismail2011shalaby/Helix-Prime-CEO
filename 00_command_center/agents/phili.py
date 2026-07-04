"""
PHILI - The Philosopher
Personal development coach who knows you deeply.
Tracks mental states, analyzes patterns, and facilitates self-development conversations.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
from pathlib import Path
from datetime import datetime
from model_backend import get_model_backend

class PHILIAgent:
    """PHILI: The Philosopher - Personal development and self-awareness coach"""
    
    def __init__(self):
        self.backend = get_model_backend()
        self.memory_dir = Path(__file__).parent.parent.parent / "Helix CEO AI Assistant" / "06_memory"
        self.phili_profile_file = self.memory_dir / "phili_personal_profile.json"
        self.mood_log_file = self.memory_dir / "phili_mood_log.json"
        self.rhythm_analysis_file = self.memory_dir / "phili_rhythm_patterns.json"
        self.research_cache_file = self.memory_dir / "phili_research_cache.json"
        
        # Ensure memory directory exists
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize profiles
        self.personal_profile = self._load_or_create("phili_personal_profile.json", {
            "name": "User",
            "music_preferences": [],
            "hobbies": [],
            "interests": [],
            "values": [],
            "goals": [],
            "fears": [],
            "strengths": [],
            "created_at": datetime.now().isoformat()
        })
        
        self.mood_log = self._load_or_create("phili_mood_log.json", [])
        self.rhythm_patterns = self._load_or_create("phili_rhythm_patterns.json", {
            "energy_cycles": [],
            "productivity_peaks": [],
            "mood_triggers": [],
            "patterns_identified": []
        })
        self.research_cache = self._load_or_create("phili_research_cache.json", {
            "papers_read": [],
            "key_insights": [],
            "actionable_takeaways": []
        })
    
    def _load_or_create(self, filename: str, default: dict | list) -> dict | list:
        """Load JSON file or create with defaults"""
        filepath = self.memory_dir / filename
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load {filename}: {e}")
        
        return default
    
    def _save_profile(self, profile_name: str, data: dict | list) -> None:
        """Save any profile to disk"""
        try:
            files = {
                "profile": self.phili_profile_file,
                "mood": self.mood_log_file,
                "rhythm": self.rhythm_analysis_file,
                "research": self.research_cache_file
            }
            
            filepath = files.get(profile_name)
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Failed to save {profile_name}: {e}")
    
    def execute_command(self, command: str, args: dict) -> str:
        """Main command dispatcher for PHILI"""
        
        if command == "profile":
            action = args.get("action", "view")
            return self.manage_profile(action, args)
        
        elif command == "check_mode":
            return self.check_psycho_mode(args.get("mood", ""), args.get("context", ""))
        
        elif command == "analyze_rhythm":
            return self.analyze_rhythm_patterns()
        
        elif command == "research":
            topic = args.get("topic", "self-development")
            return self.read_research(topic, args.get("query", ""))
        
        elif command == "reflect":
            question = args.get("question", "What matters most to you right now?")
            return self.reflection_session(question)
        
        elif command == "journal":
            entry = args.get("entry", "")
            return self.journal_entry(entry)
        
        elif command == "growth_plan":
            goal = args.get("goal", "")
            return self.create_growth_plan(goal)
        
        else:
            return f"❌ Unknown PHILI command: {command}. Try 'profile', 'check_mode', 'analyze_rhythm', 'research', 'reflect', 'journal', or 'growth_plan'."
    
    def manage_profile(self, action: str, args: dict) -> str:
        """Manage personal profile"""
        
        if action == "view":
            profile_summary = f"""
📋 Your Personal Profile:
━━━━━━━━━━━━━━━━━━━━━━━━
Name: {self.personal_profile.get('name', 'User')}

🎵 Music: {', '.join(self.personal_profile.get('music_preferences', [])) or 'Not set'}
🎯 Hobbies: {', '.join(self.personal_profile.get('hobbies', [])) or 'Not set'}
✨ Interests: {', '.join(self.personal_profile.get('interests', [])) or 'Not set'}
💪 Strengths: {', '.join(self.personal_profile.get('strengths', [])) or 'Not set'}
⚡ Values: {', '.join(self.personal_profile.get('values', [])) or 'Not set'}
🎲 Goals: {', '.join(self.personal_profile.get('goals', [])) or 'Not set'}
"""
            return profile_summary
        
        elif action == "update":
            field = args.get("field", "")
            value = args.get("value", "")
            
            if field not in self.personal_profile:
                return f"❌ Unknown field: {field}"
            
            # Handle list fields
            if isinstance(self.personal_profile[field], list):
                if args.get("mode") == "add":
                    self.personal_profile[field].append(value)
                    self._save_profile("profile", self.personal_profile)
                    return f"✓ Added '{value}' to {field}"
                elif args.get("mode") == "remove":
                    if value in self.personal_profile[field]:
                        self.personal_profile[field].remove(value)
                        self._save_profile("profile", self.personal_profile)
                        return f"✓ Removed '{value}' from {field}"
            else:
                self.personal_profile[field] = value
                self._save_profile("profile", self.personal_profile)
                return f"✓ Updated {field} to '{value}'"
            
            return "❌ Update failed"
        
        elif action == "insights":
            insights = self._generate_profile_insights()
            return insights
        
        return "❌ Unknown profile action"
    
    def _generate_profile_insights(self) -> str:
        """Generate AI insights about personal profile"""
        
        profile_str = json.dumps(self.personal_profile, indent=2)
        
        prompt = f"""Based on this personal profile, provide brief, insightful observations about the person's potential, growth opportunities, and personality patterns:

{profile_str}

Keep response to 3-4 sentences, focusing on:
1. Unique strengths/talents
2. Potential growth areas
3. How their interests align with their goals"""
        
        insights = self.backend.chat(prompt)
        
        return f"""💡 Profile Insights:
{insights}"""
    
    def check_psycho_mode(self, mood: str, context: str) -> str:
        """Track and analyze mental/psycho mode"""
        
        timestamp = datetime.now().isoformat()
        
        if not mood:
            return "❌ Please specify your current mood (e.g., 'energetic', 'focused', 'tired', 'stressed')"
        
        # Log mood entry
        mood_entry = {
            "timestamp": timestamp,
            "mood": mood,
            "context": context,
            "energy_level": args.get("energy", 5) if "args" in locals() else 5
        }
        
        self.mood_log.append(mood_entry)
        self._save_profile("mood", self.mood_log)
        
        # Generate mood analysis
        recent_moods = [m["mood"] for m in self.mood_log[-10:]]
        
        prompt = f"""The user just reported their mood as: {mood}
Context: {context}

Recent mood history (last 10 entries): {recent_moods}

Provide:
1. Brief acknowledgment of their current state
2. One insight about mood patterns if visible
3. One actionable suggestion for the next 2 hours

Keep it concise and encouraging."""
        
        analysis = self.backend.chat(prompt)
        
        return f"""🧠 Psycho-Emotional Check-in:
━━━━━━━━━━━━━━━━━━━━━━━━
Mood Logged: {mood}
Time: {timestamp}

{analysis}"""
    
    def analyze_rhythm_patterns(self) -> str:
        """Analyze personal rhythm and energy patterns"""
        
        if len(self.mood_log) < 5:
            return "⏳ Need more mood data to analyze patterns. Use 'check_mode' command to log moods regularly."
        
        # Extract patterns
        moods = [m["mood"] for m in self.mood_log[-30:]]
        mood_counts = {}
        for mood in moods:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        most_common = max(mood_counts, key=mood_counts.get) if mood_counts else "unknown"
        
        # Generate rhythm analysis
        prompt = f"""Analyze these mood/energy patterns and provide insights:

Mood history (recent entries): {moods}
Most common state: {most_common}

Identify:
1. Energy peaks (when most productive/positive)
2. Low periods (when more tired/stressed)
3. Triggers or patterns
4. Rhythm insights (daily cycles, weekly patterns)

Format as bullet points."""
        
        analysis = self.backend.chat(prompt)
        
        # Update rhythm patterns
        self.rhythm_patterns["patterns_identified"].append({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "most_common_mood": most_common
        })
        self._save_profile("rhythm", self.rhythm_patterns)
        
        return f"""🔄 Rhythm & Pattern Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━
{analysis}

📊 Most Common State: {most_common}
📝 Data Points: {len(moods)} entries analyzed"""
    
    def read_research(self, topic: str, query: str) -> str:
        """Read and synthesize research on self-development topics"""
        
        if not query:
            query = f"key findings on {topic} for personal development"
        
        # Generate research summary (simulated)
        prompt = f"""You are a research synthesis expert. Provide a comprehensive summary on:
Topic: {topic}
Specific Query: {query}

Include:
1. Key Research Findings (3-4 main points)
2. Scientific Evidence
3. Practical Applications
4. Recommended Resources
5. Action Items

Make it accessible but evidence-based."""
        
        research_summary = self.backend.chat(prompt)
        
        # Cache research
        research_entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "query": query,
            "summary": research_summary
        }
        
        self.research_cache["papers_read"].append(research_entry)
        
        # Extract key insights
        insight_prompt = f"""From this research summary, extract 3 key insights that apply to the person's self-development:

{research_summary}

Format as:
1. Insight 1 - Why it matters
2. Insight 2 - Why it matters
3. Insight 3 - Why it matters"""
        
        key_insights = self.backend.chat(insight_prompt)
        self.research_cache["key_insights"].append({
            "topic": topic,
            "insights": key_insights,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_profile("research", self.research_cache)
        
        return f"""📚 Research Summary: {topic}
━━━━━━━━━━━━━━━━━━━━━━━━
{research_summary}

💡 Key Insights for You:
{key_insights}"""
    
    def reflection_session(self, question: str) -> str:
        """Facilitate deep reflection conversation"""
        
        if not question:
            question = "What matters most to you right now, and why?"
        
        # Generate reflection prompt
        reflection_prompt = f"""You are a compassionate philosophical guide. Help the user reflect deeply on:

Question: {question}

Your approach:
1. Acknowledge the depth of the question
2. Ask 2 follow-up clarifying questions
3. Share a relevant perspective or insight
4. Suggest 1-2 practices for deeper exploration
5. Encourage journaling or meditation

Be warm, genuine, and non-judgmental."""
        
        reflection = self.backend.chat(reflection_prompt)
        
        # Log reflection session
        if not isinstance(self.mood_log, list):
            self.mood_log = []
        
        self.mood_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "reflection",
            "question": question,
            "session": reflection
        })
        self._save_profile("mood", self.mood_log)
        
        return f"""🧘 Reflection Session:
━━━━━━━━━━━━━━━━━━━━━━━━
Your Question: {question}

{reflection}"""
    
    def journal_entry(self, entry: str) -> str:
        """Process and reflect on journal entries"""
        
        if not entry:
            return "❌ Please provide your journal entry to reflect on."
        
        # Analyze journal entry
        analysis_prompt = f"""The user shared this journal entry:

"{entry}"

Provide:
1. Emotional themes detected
2. Underlying needs or desires
3. Potential growth opportunity
4. One reflection question to deepen understanding

Keep it brief and supportive."""
        
        analysis = self.backend.chat(analysis_prompt)
        
        # Store journal entry
        journal_entry_data = {
            "timestamp": datetime.now().isoformat(),
            "entry": entry,
            "analysis": analysis,
            "type": "journal"
        }
        
        self.mood_log.append(journal_entry_data)
        self._save_profile("mood", self.mood_log)
        
        return f"""📝 Journal Reflection:
━━━━━━━━━━━━━━━━━━━━━━━━
{analysis}

Your entry has been saved to your personal memory."""
    
    def create_growth_plan(self, goal: str) -> str:
        """Create personalized growth plan"""
        
        if not goal:
            return "❌ Please specify a goal for your growth plan."
        
        # Generate personalized plan
        profile_context = json.dumps(self.personal_profile, indent=2)
        
        plan_prompt = f"""Create a personalized growth plan for this person:

Goal: {goal}

Their Profile:
{profile_context}

Structure:
1. Vision Statement (why this goal matters)
2. 3 Milestone Stages (30/60/90 days)
3. Daily/Weekly Habits to Build
4. Potential Obstacles & Strategies
5. Success Metrics
6. Support Resources

Tailor it to their strengths and interests."""
        
        growth_plan = self.backend.chat(plan_prompt)
        
        # Store in profile
        if "goals" not in self.personal_profile:
            self.personal_profile["goals"] = []
        
        self.personal_profile["goals"].append({
            "goal": goal,
            "plan": growth_plan,
            "created": datetime.now().isoformat()
        })
        self._save_profile("profile", self.personal_profile)
        
        return f"""🚀 Your Growth Plan: {goal}
━━━━━━━━━━━━━━━━━━━━━━━━
{growth_plan}

This plan is saved in your personal profile."""


def run():
    """Main entry point for PHILI agent"""
    try:
        data = json.loads(sys.stdin.read())
        command = data.get("command", "profile")
        args = data.get("args", {})
        
        phili = PHILIAgent()
        response = phili.execute_command(command, args)
        print(response)
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON input: {e}")
    except Exception as e:
        print(f"❌ PHILI Error: {e}")


if __name__ == "__main__":
    run()
