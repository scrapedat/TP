#!/usr/bin/env python3
"""
Simplified swarm intelligence using multiple Ollama models
"""
import sys
import json
from ollama_client import get_client

def consensus_vote(responses):
    """Simple majority vote consensus"""
    if not responses:
        return {"consensus": "No responses", "confidence": 0.0}
    
    # Count similar responses (simplified by first 50 chars)
    response_counts = {}
    for resp in responses:
        key = resp[:50].lower().strip()
        response_counts[key] = response_counts.get(key, 0) + 1
    
    if response_counts:
        best_key = max(response_counts.keys(), key=lambda k: response_counts[k])
        best_count = response_counts[best_key]
        confidence = best_count / len(responses)
        
        # Find full response matching the best key
        for resp in responses:
            if resp[:50].lower().strip() == best_key:
                return {
                    "consensus": resp,
                    "confidence": confidence,
                    "votes": response_counts
                }
    
    return {"consensus": responses[0], "confidence": 1.0 / len(responses)}

def main():
    try:
        input_data = json.load(sys.stdin)
        task = input_data.get("task", "")
        swarm_size = input_data.get("swarm_size", 3)
        models = input_data.get("models", ["llama2", "mistral", "codellama"])
        consensus_method = input_data.get("consensus_method", "majority_vote")
        
        client = get_client()
        
        # Ensure we have enough models
        while len(models) < swarm_size:
            models.extend(models)
        models = models[:swarm_size]
        
        # Collect responses from swarm
        swarm_responses = []
        for i, model in enumerate(models):
            prompt = f"Node {i+1} specialization: {model}\nTask: {task}\nProvide your analysis and conclusion."
            
            result = client.generate(model, prompt)
            
            swarm_responses.append({
                "node_id": i + 1,
                "model": model,
                "success": result.get("success", False),
                "response": result.get("response", ""),
                "error": result.get("error")
            })
        
        # Apply consensus
        successful_responses = [r["response"] for r in swarm_responses if r["success"]]
        
        if consensus_method == "majority_vote":
            consensus_result = consensus_vote(successful_responses)
        else:
            # Default to first successful response
            consensus_result = {
                "consensus": successful_responses[0] if successful_responses else "No successful responses",
                "confidence": 1.0 if len(successful_responses) == 1 else 0.5
            }
        
        print(json.dumps({
            "task": task,
            "swarm_size": swarm_size,
            "consensus_method": consensus_method,
            "node_responses": swarm_responses,
            "consensus_result": consensus_result,
            "success_rate": len(successful_responses) / len(swarm_responses),
            "swarm_metrics": {
                "total_nodes": len(swarm_responses),
                "successful_nodes": len(successful_responses),
                "models_used": models
            }
        }))
        
    except Exception as e:
        print(json.dumps({"error": str(e), "tool": "simple_swarm"}))

if __name__ == "__main__":
    main()