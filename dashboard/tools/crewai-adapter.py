#!/usr/bin/env python3
"""
CrewAI adapter for Ollama - uses the actual CrewAI library
"""
import sys
import json
import os

def main():
    try:
        # Import CrewAI components
        from crewai import Agent, Task, Crew
        from crewai.llm import LLM
        
        input_data = json.load(sys.stdin)
        task_description = input_data.get("task", "")
        agents_config = input_data.get("agents", [])
        model = input_data.get("model", "llama2")
        
        # Configure Ollama LLM
        ollama_llm = LLM(
            model=f"ollama/{model}",
            base_url="http://localhost:11434"
        )
        
        # Create agents
        agents = []
        for i, agent_config in enumerate(agents_config):
            role = agent_config.get("role", f"Agent {i+1}")
            goal = agent_config.get("goal", f"Complete tasks related to {role}")
            backstory = agent_config.get("backstory", f"You are an expert {role}")
            
            agent = Agent(
                role=role,
                goal=goal,
                backstory=backstory,
                llm=ollama_llm,
                verbose=True
            )
            agents.append(agent)
        
        # Create default agents if none provided
        if not agents:
            researcher = Agent(
                role="Researcher",
                goal="Gather comprehensive information",
                backstory="You are a thorough researcher with expertise in information gathering",
                llm=ollama_llm
            )
            
            writer = Agent(
                role="Writer",
                goal="Create clear and engaging content",
                backstory="You are a skilled writer who can synthesize information into compelling content",
                llm=ollama_llm
            )
            
            agents = [researcher, writer]
        
        # Create task
        task = Task(
            description=task_description,
            agent=agents[0],  # Assign to first agent
            expected_output="A comprehensive response to the task"
        )
        
        # Create crew
        crew = Crew(
            agents=agents,
            tasks=[task],
            verbose=True
        )
        
        # Execute
        result = crew.kickoff()
        
        print(json.dumps({
            "success": True,
            "task": task_description,
            "agents_used": len(agents),
            "result": str(result),
            "crew_info": {
                "total_agents": len(agents),
                "model_used": model,
                "framework": "CrewAI"
            }
        }))
        
    except ImportError as e:
        print(json.dumps({
            "success": False,
            "error": f"CrewAI not available: {str(e)}",
            "fallback": "Use simple-crew.py instead",
            "tool": "crewai_adapter"
        }))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "tool": "crewai_adapter"
        }))

if __name__ == "__main__":
    main()