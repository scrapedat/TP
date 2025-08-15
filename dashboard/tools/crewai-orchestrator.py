#!/usr/bin/env python3
import sys
import json
import requests
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AgentRole(Enum):
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"

@dataclass
class Agent:
    id: str
    role: AgentRole
    model: str
    specialization: str
    tools: List[str]
    backstory: str

class CrewAIOrchestrator:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.agents = {}
        self.task_history = []
        
    def create_agent(self, agent_config: Dict[str, Any]) -> Agent:
        """Creates a specialized agent with specific role and capabilities"""
        agent = Agent(
            id=agent_config.get("id", f"agent_{len(self.agents)}"),
            role=AgentRole(agent_config.get("role", "researcher")),
            model=agent_config.get("model", "llama2"),
            specialization=agent_config.get("specialization", "general"),
            tools=agent_config.get("tools", []),
            backstory=agent_config.get("backstory", "")
        )
        self.agents[agent.id] = agent
        return agent
    
    def delegate_task(self, task: str, agent_id: str) -> Dict[str, Any]:
        """Delegates a specific task to an agent"""
        if agent_id not in self.agents:
            return {"error": f"Agent {agent_id} not found"}
        
        agent = self.agents[agent_id]
        
        # Create role-specific prompt
        role_prompt = self._create_role_prompt(agent, task)
        
        # Execute task with Ollama
        result = self._execute_with_ollama(role_prompt, agent.model)
        
        # Log task execution
        self.task_history.append({
            "task": task,
            "agent_id": agent_id,
            "role": agent.role.value,
            "result": result,
            "timestamp": self._get_timestamp()
        })
        
        return result
    
    def collaborative_workflow(self, main_task: str, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a collaborative workflow across multiple agents"""
        workflow_results = {
            "main_task": main_task,
            "workflow_steps": [],
            "final_result": None,
            "collaboration_metrics": {}
        }
        
        steps = workflow_config.get("steps", [])
        
        for step in steps:
            step_name = step.get("name", "unnamed_step")
            agent_id = step.get("agent_id")
            subtask = step.get("task", "")
            dependencies = step.get("dependencies", [])
            
            # Check if dependencies are met
            if not self._check_dependencies(dependencies, workflow_results["workflow_steps"]):
                workflow_results["workflow_steps"].append({
                    "step": step_name,
                    "status": "failed",
                    "error": "Dependencies not met"
                })
                continue
            
            # Execute step
            step_result = self.delegate_task(subtask, agent_id)
            
            workflow_results["workflow_steps"].append({
                "step": step_name,
                "agent_id": agent_id,
                "task": subtask,
                "result": step_result,
                "status": "completed" if step_result.get("success") else "failed"
            })
        
        # Synthesize final result
        workflow_results["final_result"] = self._synthesize_results(workflow_results["workflow_steps"])
        workflow_results["collaboration_metrics"] = self._calculate_collaboration_metrics(workflow_results["workflow_steps"])
        
        return workflow_results
    
    def _create_role_prompt(self, agent: Agent, task: str) -> str:
        """Creates a role-specific prompt for the agent"""
        role_instructions = {
            AgentRole.RESEARCHER: "You are a thorough researcher. Gather comprehensive information and provide detailed analysis.",
            AgentRole.ANALYST: "You are a data analyst. Analyze information critically and provide insights with supporting evidence.",
            AgentRole.WRITER: "You are a skilled writer. Create clear, engaging, and well-structured content.",
            AgentRole.REVIEWER: "You are a quality reviewer. Evaluate work critically and provide constructive feedback.",
            AgentRole.COORDINATOR: "You are a project coordinator. Organize tasks and ensure smooth workflow execution."
        }
        
        prompt = f"""
        {role_instructions.get(agent.role, "You are a helpful AI assistant.")}
        
        Specialization: {agent.specialization}
        Available tools: {', '.join(agent.tools)}
        Backstory: {agent.backstory}
        
        Task: {task}
        
        Please complete this task according to your role and specialization.
        Provide a detailed response with your reasoning and any recommendations.
        """
        
        return prompt
    
    def _execute_with_ollama(self, prompt: str, model: str) -> Dict[str, Any]:
        """Executes prompt with Ollama model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama API error: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
    
    def _check_dependencies(self, dependencies: List[str], completed_steps: List[Dict]) -> bool:
        """Checks if step dependencies are satisfied"""
        completed_step_names = [step.get("step") for step in completed_steps if step.get("status") == "completed"]
        return all(dep in completed_step_names for dep in dependencies)
    
    def _synthesize_results(self, workflow_steps: List[Dict]) -> Dict[str, Any]:
        """Synthesizes results from all workflow steps"""
        successful_steps = [step for step in workflow_steps if step.get("status") == "completed"]
        
        synthesis = {
            "total_steps": len(workflow_steps),
            "successful_steps": len(successful_steps),
            "success_rate": len(successful_steps) / len(workflow_steps) if workflow_steps else 0,
            "key_insights": [],
            "recommendations": []
        }
        
        # Extract key insights from successful steps
        for step in successful_steps:
            result = step.get("result", {})
            if result.get("success"):
                response = result.get("response", "")
                # Simple extraction of insights (in real implementation, this would be more sophisticated)
                if "insight" in response.lower() or "conclusion" in response.lower():
                    synthesis["key_insights"].append({
                        "from_step": step.get("step"),
                        "agent": step.get("agent_id"),
                        "insight": response[:200] + "..." if len(response) > 200 else response
                    })
        
        return synthesis
    
    def _calculate_collaboration_metrics(self, workflow_steps: List[Dict]) -> Dict[str, Any]:
        """Calculates metrics about the collaboration"""
        agents_involved = set(step.get("agent_id") for step in workflow_steps)
        
        return {
            "agents_involved": len(agents_involved),
            "total_interactions": len(workflow_steps),
            "success_rate": len([s for s in workflow_steps if s.get("status") == "completed"]) / len(workflow_steps),
            "average_response_quality": 0.85  # Placeholder - would calculate based on actual metrics
        }
    
    def _get_timestamp(self) -> str:
        """Returns current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        
        task = input_data.get("task", "")
        agents_config = input_data.get("agents", [])
        tools = input_data.get("tools", [])
        process = input_data.get("process", "sequential")
        
        if not task:
            raise ValueError("Task parameter is required")
        
        orchestrator = CrewAIOrchestrator()
        
        # Create agents
        created_agents = []
        for agent_config in agents_config:
            agent = orchestrator.create_agent(agent_config)
            created_agents.append({
                "id": agent.id,
                "role": agent.role.value,
                "specialization": agent.specialization
            })
        
        # If no specific workflow provided, create a default collaborative workflow
        if not agents_config:
            # Create default agents
            default_agents = [
                {"id": "researcher", "role": "researcher", "model": "llama2", "specialization": "information_gathering"},
                {"id": "analyst", "role": "analyst", "model": "llama2", "specialization": "data_analysis"},
                {"id": "writer", "role": "writer", "model": "llama2", "specialization": "content_creation"}
            ]
            
            for agent_config in default_agents:
                orchestrator.create_agent(agent_config)
            
            # Create default workflow
            workflow_config = {
                "steps": [
                    {"name": "research", "agent_id": "researcher", "task": f"Research information about: {task}"},
                    {"name": "analysis", "agent_id": "analyst", "task": f"Analyze the research findings for: {task}", "dependencies": ["research"]},
                    {"name": "synthesis", "agent_id": "writer", "task": f"Create a comprehensive summary for: {task}", "dependencies": ["research", "analysis"]}
                ]
            }
            
            result = orchestrator.collaborative_workflow(task, workflow_config)
        else:
            # Execute with provided configuration
            workflow_config = {
                "steps": [
                    {"name": "main_task", "agent_id": agents_config[0].get("id", "agent_0"), "task": task}
                ]
            }
            result = orchestrator.collaborative_workflow(task, workflow_config)
        
        # Add metadata
        result["orchestrator_info"] = {
            "agents_created": created_agents,
            "process_type": process,
            "tools_available": tools
        }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "tool": "crewai_orchestrator"
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main()