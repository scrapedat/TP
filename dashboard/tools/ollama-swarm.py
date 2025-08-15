#!/usr/bin/env python3
import sys
import json
import requests
import asyncio
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import threading
import time

class ConsensusMethod(Enum):
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_AVERAGE = "weighted_average"
    BYZANTINE_FAULT_TOLERANT = "byzantine_fault_tolerant"
    PROOF_OF_STAKE = "proof_of_stake"

@dataclass
class SwarmNode:
    id: str
    model: str
    specialization: str
    reputation_score: float
    processing_power: int
    knowledge_domains: List[str]
    last_active: str

@dataclass
class KnowledgeItem:
    id: str
    content: str
    source_node: str
    confidence: float
    timestamp: str
    validation_count: int

class OllamaSwarmIntelligence:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.nodes = {}
        self.knowledge_pool = {}
        self.consensus_history = []
        self.synchronization_lock = threading.Lock()
        
    def initialize_swarm(self, swarm_config: Dict[str, Any]) -> Dict[str, Any]:
        """Initializes the swarm with multiple nodes"""
        swarm_size = swarm_config.get("swarm_size", 3)
        node_configs = swarm_config.get("nodes", [])
        
        # Create nodes
        for i in range(swarm_size):
            if i < len(node_configs):
                config = node_configs[i]
            else:
                config = self._generate_default_node_config(i)
            
            node = SwarmNode(
                id=config.get("id", f"node_{i}"),
                model=config.get("model", "llama2"),
                specialization=config.get("specialization", "general"),
                reputation_score=config.get("reputation_score", 1.0),
                processing_power=config.get("processing_power", 100),
                knowledge_domains=config.get("knowledge_domains", ["general"]),
                last_active=self._get_timestamp()
            )
            
            self.nodes[node.id] = node
        
        return {
            "swarm_initialized": True,
            "node_count": len(self.nodes),
            "nodes": [{"id": node.id, "specialization": node.specialization} for node in self.nodes.values()]
        }
    
    def distributed_processing(self, task: str, consensus_method: str = "majority_vote") -> Dict[str, Any]:
        """Processes a task across the swarm using distributed intelligence"""
        if not self.nodes:
            return {"error": "No nodes available in swarm"}
        
        processing_result = {
            "task": task,
            "consensus_method": consensus_method,
            "node_responses": [],
            "consensus_result": None,
            "confidence_score": 0.0,
            "processing_metrics": {}
        }
        
        # Distribute task to all nodes
        node_responses = []
        for node_id, node in self.nodes.items():
            response = self._process_task_on_node(task, node)
            node_responses.append({
                "node_id": node_id,
                "specialization": node.specialization,
                "response": response,
                "processing_time": response.get("processing_time", 0),
                "confidence": response.get("confidence", 0.5)
            })
        
        processing_result["node_responses"] = node_responses
        
        # Apply consensus mechanism
        consensus_result = self._apply_consensus(node_responses, ConsensusMethod(consensus_method))
        processing_result["consensus_result"] = consensus_result
        
        # Update knowledge pool
        self._update_knowledge_pool(task, consensus_result, node_responses)
        
        # Calculate metrics
        processing_result["processing_metrics"] = self._calculate_processing_metrics(node_responses)
        
        return processing_result
    
    def knowledge_synchronization(self) -> Dict[str, Any]:
        """Synchronizes knowledge across all nodes in the swarm"""
        with self.synchronization_lock:
            sync_result = {
                "synchronization_started": self._get_timestamp(),
                "knowledge_items_synced": 0,
                "conflicts_resolved": 0,
                "sync_metrics": {}
            }
            
            # Collect knowledge from all nodes
            all_knowledge = []
            for node_id, node in self.nodes.items():
                node_knowledge = self._extract_node_knowledge(node_id)
                all_knowledge.extend(node_knowledge)
            
            # Resolve conflicts and merge knowledge
            merged_knowledge = self._merge_knowledge_items(all_knowledge)
            
            # Distribute merged knowledge back to nodes
            for node_id in self.nodes.keys():
                self._distribute_knowledge_to_node(node_id, merged_knowledge)
            
            sync_result["knowledge_items_synced"] = len(merged_knowledge)
            sync_result["sync_metrics"] = {
                "total_nodes": len(self.nodes),
                "knowledge_pool_size": len(self.knowledge_pool),
                "average_node_knowledge": len(merged_knowledge) / len(self.nodes) if self.nodes else 0
            }
            
            return sync_result
    
    def fault_tolerance_check(self) -> Dict[str, Any]:
        """Checks and maintains fault tolerance in the swarm"""
        fault_check = {
            "healthy_nodes": 0,
            "faulty_nodes": 0,
            "network_health": 0.0,
            "redundancy_level": 0.0,
            "recommendations": []
        }
        
        healthy_nodes = []
        faulty_nodes = []
        
        for node_id, node in self.nodes.items():
            if self._check_node_health(node):
                healthy_nodes.append(node_id)
            else:
                faulty_nodes.append(node_id)
        
        fault_check["healthy_nodes"] = len(healthy_nodes)
        fault_check["faulty_nodes"] = len(faulty_nodes)
        fault_check["network_health"] = len(healthy_nodes) / len(self.nodes) if self.nodes else 0
        
        # Calculate redundancy level
        specializations = {}
        for node in self.nodes.values():
            spec = node.specialization
            specializations[spec] = specializations.get(spec, 0) + 1
        
        min_redundancy = min(specializations.values()) if specializations else 0
        fault_check["redundancy_level"] = min_redundancy / len(self.nodes) if self.nodes else 0
        
        # Generate recommendations
        if fault_check["network_health"] < 0.8:
            fault_check["recommendations"].append("Consider adding more nodes to improve network health")
        
        if fault_check["redundancy_level"] < 0.3:
            fault_check["recommendations"].append("Increase specialization redundancy for better fault tolerance")
        
        return fault_check
    
    def _process_task_on_node(self, task: str, node: SwarmNode) -> Dict[str, Any]:
        """Processes a task on a specific node"""
        start_time = time.time()
        
        # Create node-specific prompt
        prompt = f"""
        Node Specialization: {node.specialization}
        Knowledge Domains: {', '.join(node.knowledge_domains)}
        Reputation Score: {node.reputation_score}
        
        Task: {task}
        
        Process this task according to your specialization and provide:
        1. Your analysis
        2. Confidence level (0-1)
        3. Any relevant insights from your knowledge domain
        
        Be specific and detailed in your response.
        """
        
        # Call Ollama for this node
        ollama_response = self._call_ollama(prompt, node.model)
        
        processing_time = time.time() - start_time
        
        # Extract confidence from response (simplified)
        confidence = self._extract_confidence(ollama_response.get("response", ""))
        
        return {
            "success": ollama_response.get("success", False),
            "response": ollama_response.get("response", ""),
            "confidence": confidence,
            "processing_time": processing_time,
            "node_specialization": node.specialization
        }
    
    def _apply_consensus(self, node_responses: List[Dict[str, Any]], method: ConsensusMethod) -> Dict[str, Any]:
        """Applies the specified consensus mechanism"""
        if method == ConsensusMethod.MAJORITY_VOTE:
            return self._majority_vote_consensus(node_responses)
        elif method == ConsensusMethod.WEIGHTED_AVERAGE:
            return self._weighted_average_consensus(node_responses)
        elif method == ConsensusMethod.BYZANTINE_FAULT_TOLERANT:
            return self._byzantine_fault_tolerant_consensus(node_responses)
        elif method == ConsensusMethod.PROOF_OF_STAKE:
            return self._proof_of_stake_consensus(node_responses)
        else:
            return self._majority_vote_consensus(node_responses)
    
    def _majority_vote_consensus(self, node_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Implements majority vote consensus"""
        # Simplified majority vote based on response similarity
        responses = [r["response"]["response"] for r in node_responses if r["response"].get("success")]
        
        if not responses:
            return {"consensus": "No valid responses", "confidence": 0.0}
        
        # Find most common response pattern (simplified)
        response_counts = {}
        for response in responses:
            key_words = set(response.lower().split()[:10])  # First 10 words as key
            key = " ".join(sorted(key_words))
            response_counts[key] = response_counts.get(key, 0) + 1
        
        if response_counts:
            majority_key = max(response_counts.keys(), key=lambda k: response_counts[k])
            majority_count = response_counts[majority_key]
            confidence = majority_count / len(responses)
            
            # Find the actual response that matches the majority
            for response in responses:
                key_words = set(response.lower().split()[:10])
                key = " ".join(sorted(key_words))
                if key == majority_key:
                    return {
                        "consensus": response,
                        "confidence": confidence,
                        "voting_results": response_counts
                    }
        
        return {"consensus": responses[0], "confidence": 1.0 / len(responses)}
    
    def _weighted_average_consensus(self, node_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Implements weighted average consensus based on node reputation"""
        total_weight = 0
        weighted_responses = []
        
        for response in node_responses:
            if response["response"].get("success"):
                node_id = response["node_id"]
                node = self.nodes[node_id]
                weight = node.reputation_score * response["response"]["confidence"]
                
                weighted_responses.append({
                    "response": response["response"]["response"],
                    "weight": weight
                })
                total_weight += weight
        
        if not weighted_responses:
            return {"consensus": "No valid responses", "confidence": 0.0}
        
        # Create weighted consensus (simplified - just use highest weighted response)
        best_response = max(weighted_responses, key=lambda x: x["weight"])
        
        return {
            "consensus": best_response["response"],
            "confidence": best_response["weight"] / total_weight if total_weight > 0 else 0,
            "weighting_method": "reputation_confidence"
        }
    
    def _byzantine_fault_tolerant_consensus(self, node_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Implements Byzantine Fault Tolerant consensus"""
        # Simplified BFT - requires 2/3 agreement
        valid_responses = [r for r in node_responses if r["response"].get("success")]
        
        if len(valid_responses) < 3:
            return {"consensus": "Insufficient nodes for BFT", "confidence": 0.0}
        
        required_agreement = (2 * len(valid_responses)) // 3 + 1
        
        # Group similar responses
        response_groups = {}
        for response in valid_responses:
            response_text = response["response"]["response"]
            # Simple similarity grouping based on first few words
            key = " ".join(response_text.split()[:5])
            
            if key not in response_groups:
                response_groups[key] = []
            response_groups[key].append(response)
        
        # Find group with sufficient agreement
        for key, group in response_groups.items():
            if len(group) >= required_agreement:
                return {
                    "consensus": group[0]["response"]["response"],
                    "confidence": len(group) / len(valid_responses),
                    "agreement_threshold": required_agreement,
                    "actual_agreement": len(group)
                }
        
        return {"consensus": "No Byzantine consensus reached", "confidence": 0.0}
    
    def _proof_of_stake_consensus(self, node_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Implements Proof of Stake consensus based on node reputation"""
        # Stake is based on reputation score and processing power
        stakes = {}
        total_stake = 0
        
        for response in node_responses:
            if response["response"].get("success"):
                node_id = response["node_id"]
                node = self.nodes[node_id]
                stake = node.reputation_score * node.processing_power
                stakes[node_id] = {
                    "stake": stake,
                    "response": response["response"]["response"]
                }
                total_stake += stake
        
        if not stakes:
            return {"consensus": "No valid stakes", "confidence": 0.0}
        
        # Select response based on stake weight
        highest_stake_node = max(stakes.keys(), key=lambda x: stakes[x]["stake"])
        
        return {
            "consensus": stakes[highest_stake_node]["response"],
            "confidence": stakes[highest_stake_node]["stake"] / total_stake,
            "selected_node": highest_stake_node,
            "stake_distribution": {k: v["stake"] for k, v in stakes.items()}
        }
    
    def _update_knowledge_pool(self, task: str, consensus_result: Dict[str, Any], node_responses: List[Dict[str, Any]]):
        """Updates the shared knowledge pool"""
        knowledge_id = hashlib.md5(task.encode()).hexdigest()
        
        knowledge_item = KnowledgeItem(
            id=knowledge_id,
            content=consensus_result.get("consensus", ""),
            source_node="swarm_consensus",
            confidence=consensus_result.get("confidence", 0.0),
            timestamp=self._get_timestamp(),
            validation_count=len([r for r in node_responses if r["response"].get("success")])
        )
        
        self.knowledge_pool[knowledge_id] = knowledge_item
    
    def _extract_node_knowledge(self, node_id: str) -> List[KnowledgeItem]:
        """Extracts knowledge items from a specific node"""
        # Simplified - return subset of knowledge pool
        return [item for item in self.knowledge_pool.values() if item.source_node == node_id]
    
    def _merge_knowledge_items(self, knowledge_items: List[KnowledgeItem]) -> List[KnowledgeItem]:
        """Merges knowledge items resolving conflicts"""
        # Simplified merging - remove duplicates and keep highest confidence
        merged = {}
        
        for item in knowledge_items:
            if item.id not in merged or item.confidence > merged[item.id].confidence:
                merged[item.id] = item
        
        return list(merged.values())
    
    def _distribute_knowledge_to_node(self, node_id: str, knowledge_items: List[KnowledgeItem]):
        """Distributes knowledge to a specific node"""
        # In a real implementation, this would update the node's local knowledge base
        pass
    
    def _check_node_health(self, node: SwarmNode) -> bool:
        """Checks if a node is healthy"""
        # Simplified health check - in real implementation would ping the node
        return node.reputation_score > 0.5
    
    def _extract_confidence(self, response: str) -> float:
        """Extracts confidence level from response text"""
        # Simplified confidence extraction
        confidence_keywords = {
            "certain": 0.9, "confident": 0.8, "likely": 0.7, "possible": 0.6,
            "uncertain": 0.4, "unlikely": 0.3, "doubtful": 0.2
        }
        
        response_lower = response.lower()
        for keyword, confidence in confidence_keywords.items():
            if keyword in response_lower:
                return confidence
        
        return 0.5  # Default confidence
    
    def _calculate_processing_metrics(self, node_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates processing metrics"""
        successful_responses = [r for r in node_responses if r["response"].get("success")]
        
        if not successful_responses:
            return {"error": "No successful responses"}
        
        processing_times = [r["processing_time"] for r in successful_responses]
        confidences = [r["confidence"] for r in successful_responses]
        
        return {
            "total_nodes": len(node_responses),
            "successful_nodes": len(successful_responses),
            "success_rate": len(successful_responses) / len(node_responses),
            "average_processing_time": sum(processing_times) / len(processing_times),
            "average_confidence": sum(confidences) / len(confidences),
            "min_processing_time": min(processing_times),
            "max_processing_time": max(processing_times)
        }
    
    def _generate_default_node_config(self, index: int) -> Dict[str, Any]:
        """Generates default configuration for a node"""
        specializations = ["general", "analysis", "creative", "technical", "research"]
        models = ["llama2", "mistral", "codellama"]
        
        return {
            "id": f"node_{index}",
            "model": models[index % len(models)],
            "specialization": specializations[index % len(specializations)],
            "reputation_score": 1.0,
            "processing_power": 100,
            "knowledge_domains": [specializations[index % len(specializations)]]
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
        
        swarm_size = input_data.get("swarm_size", 3)
        consensus_method = input_data.get("consensus_method", "majority_vote")
        knowledge_sharing = input_data.get("knowledge_sharing", True)
        task = input_data.get("task", "Process this information collaboratively")
        
        swarm = OllamaSwarmIntelligence()
        
        # Initialize swarm
        swarm_config = {
            "swarm_size": swarm_size,
            "nodes": input_data.get("nodes", [])
        }
        
        init_result = swarm.initialize_swarm(swarm_config)
        
        # Process task with distributed intelligence
        processing_result = swarm.distributed_processing(task, consensus_method)
        
        # Perform knowledge synchronization if enabled
        sync_result = None
        if knowledge_sharing:
            sync_result = swarm.knowledge_synchronization()
        
        # Check fault tolerance
        fault_check = swarm.fault_tolerance_check()
        
        # Combine results
        result = {
            "swarm_initialization": init_result,
            "distributed_processing": processing_result,
            "knowledge_synchronization": sync_result,
            "fault_tolerance": fault_check,
            "swarm_metrics": {
                "total_nodes": len(swarm.nodes),
                "knowledge_pool_size": len(swarm.knowledge_pool),
                "consensus_method": consensus_method
            }
        }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "tool": "ollama_swarm_intelligence"
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main()