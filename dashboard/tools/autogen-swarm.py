#!/usr/bin/env python3
import sys
import json
import requests
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class MessageType(Enum):
    TASK = "task"
    RESPONSE = "response"
    QUESTION = "question"
    TERMINATION = "termination"

@dataclass
class Message:
    id: str
    sender: str
    recipient: str
    content: str
    message_type: MessageType
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AutoGenAgent:
    id: str
    name: str
    role: str
    model: str
    system_message: str
    capabilities: List[str]
    max_consecutive_auto_reply: int = 3
    human_input_mode: str = "NEVER"  # NEVER, TERMINATE, ALWAYS

class AutoGenSwarm:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.agents = {}
        self.conversation_history = []
        self.current_round = 0
        self.max_rounds = 10
        
    def create_agent(self, agent_config: Dict[str, Any]) -> AutoGenAgent:
        """Creates an AutoGen agent with specific capabilities"""
        agent = AutoGenAgent(
            id=agent_config.get("id", str(uuid.uuid4())),
            name=agent_config.get("name", "Agent"),
            role=agent_config.get("role", "assistant"),
            model=agent_config.get("model", "llama2"),
            system_message=agent_config.get("system_message", "You are a helpful AI assistant."),
            capabilities=agent_config.get("capabilities", []),
            max_consecutive_auto_reply=agent_config.get("max_consecutive_auto_reply", 3),
            human_input_mode=agent_config.get("human_input_mode", "NEVER")
        )
        self.agents[agent.id] = agent
        return agent
    
    def initiate_conversation(self, initiator_id: str, recipient_id: str, message: str) -> Dict[str, Any]:
        """Initiates a conversation between two agents"""
        if initiator_id not in self.agents or recipient_id not in self.agents:
            return {"error": "One or both agents not found"}
        
        # Create initial message
        initial_message = Message(
            id=str(uuid.uuid4()),
            sender=initiator_id,
            recipient=recipient_id,
            content=message,
            message_type=MessageType.TASK,
            timestamp=self._get_timestamp()
        )
        
        self.conversation_history.append(initial_message)
        
        # Start conversation loop
        return self._conversation_loop(initial_message)
    
    def multi_agent_conversation(self, conversation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Manages a multi-agent conversation with multiple participants"""
        participants = conversation_config.get("participants", [])
        initial_message = conversation_config.get("initial_message", "")
        max_rounds = conversation_config.get("max_rounds", self.max_rounds)
        
        if len(participants) < 2:
            return {"error": "At least 2 participants required"}
        
        conversation_result = {
            "conversation_id": str(uuid.uuid4()),
            "participants": participants,
            "rounds": [],
            "final_consensus": None,
            "conversation_metrics": {}
        }
        
        current_speaker = participants[0]
        current_message = initial_message
        
        for round_num in range(max_rounds):
            round_result = {
                "round": round_num + 1,
                "speaker": current_speaker,
                "message": current_message,
                "responses": []
            }
            
            # Get responses from other participants
            for participant in participants:
                if participant != current_speaker:
                    response = self._generate_agent_response(participant, current_message, self.conversation_history)
                    round_result["responses"].append({
                        "agent": participant,
                        "response": response
                    })
            
            conversation_result["rounds"].append(round_result)
            
            # Check for termination conditions
            if self._should_terminate_conversation(round_result):
                break
            
            # Select next speaker and message
            next_speaker, next_message = self._select_next_speaker(participants, round_result)
            current_speaker = next_speaker
            current_message = next_message
        
        # Generate final consensus
        conversation_result["final_consensus"] = self._generate_consensus(conversation_result["rounds"])
        conversation_result["conversation_metrics"] = self._calculate_conversation_metrics(conversation_result)
        
        return conversation_result
    
    def _conversation_loop(self, initial_message: Message) -> Dict[str, Any]:
        """Handles the conversation loop between two agents"""
        conversation_result = {
            "conversation_id": str(uuid.uuid4()),
            "messages": [asdict(initial_message)],
            "rounds": 0,
            "termination_reason": None,
            "final_result": None
        }
        
        current_message = initial_message
        
        while self.current_round < self.max_rounds:
            self.current_round += 1
            
            # Generate response from recipient
            response = self._generate_agent_response(
                current_message.recipient, 
                current_message.content, 
                self.conversation_history
            )
            
            # Create response message
            response_message = Message(
                id=str(uuid.uuid4()),
                sender=current_message.recipient,
                recipient=current_message.sender,
                content=response.get("response", ""),
                message_type=MessageType.RESPONSE,
                timestamp=self._get_timestamp(),
                metadata={"model_used": response.get("model")}
            )
            
            self.conversation_history.append(response_message)
            conversation_result["messages"].append(asdict(response_message))
            
            # Check termination conditions
            if self._should_terminate(response_message.content):
                conversation_result["termination_reason"] = "Natural termination"
                break
            
            # Switch roles for next iteration
            current_message = Message(
                id=str(uuid.uuid4()),
                sender=response_message.sender,
                recipient=response_message.recipient,
                content=response_message.content,
                message_type=MessageType.TASK,
                timestamp=self._get_timestamp()
            )
        
        conversation_result["rounds"] = self.current_round
        conversation_result["final_result"] = self._extract_final_result(conversation_result["messages"])
        
        return conversation_result
    
    def _generate_agent_response(self, agent_id: str, message: str, context: List[Message]) -> Dict[str, Any]:
        """Generates a response from a specific agent"""
        if agent_id not in self.agents:
            return {"error": f"Agent {agent_id} not found"}
        
        agent = self.agents[agent_id]
        
        # Build context from conversation history
        context_str = self._build_context_string(context, agent_id)
        
        # Create agent-specific prompt
        prompt = f"""
        {agent.system_message}
        
        Role: {agent.role}
        Capabilities: {', '.join(agent.capabilities)}
        
        Conversation Context:
        {context_str}
        
        Current Message: {message}
        
        Please respond according to your role and capabilities. Be concise but thorough.
        If you believe the conversation should end, include "TERMINATE" in your response.
        """
        
        return self._call_ollama(prompt, agent.model)
    
    def _build_context_string(self, context: List[Message], current_agent_id: str) -> str:
        """Builds a context string from conversation history"""
        context_lines = []
        for msg in context[-5:]:  # Last 5 messages for context
            role = "You" if msg.sender == current_agent_id else f"Agent {msg.sender}"
            context_lines.append(f"{role}: {msg.content}")
        return "\n".join(context_lines)
    
    def _should_terminate(self, message: str) -> bool:
        """Checks if conversation should terminate"""
        termination_keywords = ["TERMINATE", "FINISHED", "COMPLETE", "END CONVERSATION"]
        return any(keyword in message.upper() for keyword in termination_keywords)
    
    def _should_terminate_conversation(self, round_result: Dict[str, Any]) -> bool:
        """Checks if multi-agent conversation should terminate"""
        responses = round_result.get("responses", [])
        
        # Check if any agent wants to terminate
        for response in responses:
            if self._should_terminate(response.get("response", {}).get("response", "")):
                return True
        
        # Check for consensus
        if len(responses) >= 2:
            # Simple consensus check - if responses are similar, consider it consensus
            return self._check_consensus(responses)
        
        return False
    
    def _check_consensus(self, responses: List[Dict[str, Any]]) -> bool:
        """Checks if there's consensus among agent responses"""
        # Simplified consensus check - in real implementation, this would be more sophisticated
        response_texts = [r.get("response", {}).get("response", "") for r in responses]
        
        # Check for common keywords or themes
        common_words = set()
        for text in response_texts:
            words = set(text.lower().split())
            if not common_words:
                common_words = words
            else:
                common_words = common_words.intersection(words)
        
        # If there are enough common words, consider it consensus
        return len(common_words) > 3
    
    def _select_next_speaker(self, participants: List[str], round_result: Dict[str, Any]) -> tuple:
        """Selects the next speaker and message for the conversation"""
        current_speaker = round_result["speaker"]
        responses = round_result["responses"]
        
        # Simple round-robin selection
        current_index = participants.index(current_speaker)
        next_index = (current_index + 1) % len(participants)
        next_speaker = participants[next_index]
        
        # Use the most relevant response as the next message
        if responses:
            next_message = responses[0]["response"].get("response", "Continue the discussion.")
        else:
            next_message = "Continue the discussion."
        
        return next_speaker, next_message
    
    def _generate_consensus(self, rounds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates a final consensus from conversation rounds"""
        all_responses = []
        for round_data in rounds:
            for response in round_data.get("responses", []):
                all_responses.append(response.get("response", {}).get("response", ""))
        
        # Create consensus prompt
        consensus_prompt = f"""
        Based on the following conversation responses, generate a final consensus:
        
        {chr(10).join(all_responses)}
        
        Provide a summary that captures the main agreements and key points.
        """
        
        consensus_result = self._call_ollama(consensus_prompt, "llama2")
        
        return {
            "consensus_text": consensus_result.get("response", ""),
            "confidence": 0.8,  # Placeholder
            "key_agreements": self._extract_key_points(all_responses)
        }
    
    def _extract_key_points(self, responses: List[str]) -> List[str]:
        """Extracts key points from responses"""
        # Simplified key point extraction
        key_points = []
        for response in responses:
            sentences = response.split('.')
            for sentence in sentences:
                if len(sentence.strip()) > 20 and any(word in sentence.lower() for word in ['important', 'key', 'main', 'crucial']):
                    key_points.append(sentence.strip())
        
        return key_points[:5]  # Return top 5 key points
    
    def _calculate_conversation_metrics(self, conversation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates metrics about the conversation"""
        rounds = conversation_result.get("rounds", [])
        participants = conversation_result.get("participants", [])
        
        total_responses = sum(len(round_data.get("responses", [])) for round_data in rounds)
        
        return {
            "total_rounds": len(rounds),
            "total_responses": total_responses,
            "participants_count": len(participants),
            "average_responses_per_round": total_responses / len(rounds) if rounds else 0,
            "conversation_efficiency": min(1.0, 10 / len(rounds)) if rounds else 0  # Efficiency decreases with more rounds
        }
    
    def _extract_final_result(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extracts the final result from conversation messages"""
        if not messages:
            return {"result": "No conversation occurred"}
        
        last_message = messages[-1]
        
        return {
            "final_message": last_message.get("content", ""),
            "final_speaker": last_message.get("sender", ""),
            "conversation_length": len(messages),
            "outcome": "completed" if len(messages) > 1 else "incomplete"
        }
    
    def _call_ollama(self, prompt: str, model: str) -> Dict[str, Any]:
        """Makes API call to Ollama"""
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
    
    def _get_timestamp(self) -> str:
        """Returns current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        
        conversation_config = input_data.get("conversation_config", {})
        agents_config = input_data.get("agents", [])
        max_rounds = input_data.get("max_rounds", 10)
        
        swarm = AutoGenSwarm()
        swarm.max_rounds = max_rounds
        
        # Create agents
        created_agents = []
        for agent_config in agents_config:
            agent = swarm.create_agent(agent_config)
            created_agents.append({
                "id": agent.id,
                "name": agent.name,
                "role": agent.role
            })
        
        # If no agents provided, create default agents
        if not agents_config:
            default_agents = [
                {
                    "id": "coordinator",
                    "name": "Coordinator",
                    "role": "project_manager",
                    "model": "llama2",
                    "system_message": "You are a project coordinator. Help organize tasks and facilitate communication.",
                    "capabilities": ["task_management", "communication", "planning"]
                },
                {
                    "id": "specialist",
                    "name": "Specialist",
                    "role": "domain_expert",
                    "model": "llama2",
                    "system_message": "You are a domain specialist. Provide expert knowledge and detailed analysis.",
                    "capabilities": ["analysis", "expertise", "problem_solving"]
                }
            ]
            
            for agent_config in default_agents:
                swarm.create_agent(agent_config)
            
            created_agents = [{"id": "coordinator", "name": "Coordinator", "role": "project_manager"},
                            {"id": "specialist", "name": "Specialist", "role": "domain_expert"}]
        
        # Execute conversation
        if conversation_config.get("type") == "multi_agent":
            result = swarm.multi_agent_conversation(conversation_config)
        else:
            # Default to two-agent conversation
            initiator = created_agents[0]["id"] if created_agents else "coordinator"
            recipient = created_agents[1]["id"] if len(created_agents) > 1 else "specialist"
            initial_message = conversation_config.get("initial_message", "Let's work together on this task.")
            
            result = swarm.initiate_conversation(initiator, recipient, initial_message)
        
        # Add metadata
        result["swarm_info"] = {
            "agents_created": created_agents,
            "max_rounds": max_rounds,
            "conversation_type": conversation_config.get("type", "two_agent")
        }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "tool": "autogen_swarm"
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main()