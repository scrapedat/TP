#!/usr/bin/env python3
"""
Simplified CrewAI-style multi-agent orchestrator using Ollama
"""
import sys
import json
from ollama_client import get_client

def create_agent_prompt(role, task, context=""):
    """Create role-specific prompts"""
    role_prompts = {
        "researcher": f"You are a thorough researcher. Research and gather information about: {task}",
        "analyst": f"You are a data analyst. Analyze the following information: {context}\nTask: {task}",
        "writer": f"You are a skilled writer. Create content based on: {context}\nTask: {task}",
        "reviewer": f"You are a quality reviewer. Review and improve: {context}\nTask: {task}"
    }
    return role_prompts.get(role, f"Complete this task: {task}")

def main():
    try:
        input_data = json.load(sys.stdin)
        task = input_data.get("task", "")
        agents = input_data.get("agents", [{"role": "researcher"}, {"role": "writer"}])
        model = input_data.get("model", "llama2")
        
        client = get_client()
        results = []
        context = ""
        
        for i, agent in enumerate(agents):
            role = agent.get("role", "assistant")
            prompt = create_agent_prompt(role, task, context)
            
            result = client.generate(model, prompt)
            
            if result.get("success"):
                agent_result = {
                    "agent": role,
                    "step": i + 1,
                    "response": result["response"],
                    "success": True
                }
                results.append(agent_result)
                context += f"\n{role} output: {result['response'][:200]}..."
            else:
                results.append({
                    "agent": role,
                    "step": i + 1,
                    "error": result.get("error"),
                    "success": False
                })
        
        print(json.dumps({
            "task": task,
            "agents_used": len(agents),
            "results": results,
            "final_output": results[-1]["response"] if results and results[-1].get("success") else "Task incomplete"
        }))
        
    except Exception as e:
        print(json.dumps({"error": str(e), "tool": "simple_crew"}))

if __name__ == "__main__":
    main()