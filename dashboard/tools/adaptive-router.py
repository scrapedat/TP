#!/usr/bin/env python3
import sys
import json
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import statistics

class TaskType(Enum):
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    CREATIVE_WRITING = "creative_writing"
    QUESTION_ANSWERING = "question_answering"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    REASONING = "reasoning"

@dataclass
class ModelMetrics:
    model_name: str
    response_time: float
    accuracy_score: float
    resource_usage: float
    success_rate: float
    specialization_score: Dict[str, float]
    last_updated: str

@dataclass
class TaskCharacteristics:
    task_type: TaskType
    complexity_level: int  # 1-10
    input_length: int
    expected_output_length: int
    domain: str
    priority: int  # 1-5

class AdaptiveModelRouter:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_pool = {}
        self.performance_history = {}
        self.routing_decisions = []
        self.load_balancer = {}
        
    def register_model(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Registers a model in the pool with initial metrics"""
        model_name = model_config.get("name", "unknown")
        
        metrics = ModelMetrics(
            model_name=model_name,
            response_time=model_config.get("baseline_response_time", 1.0),
            accuracy_score=model_config.get("baseline_accuracy", 0.7),
            resource_usage=model_config.get("resource_usage", 0.5),
            success_rate=model_config.get("success_rate", 0.9),
            specialization_score=model_config.get("specializations", {}),
            last_updated=self._get_timestamp()
        )
        
        self.model_pool[model_name] = metrics
        self.load_balancer[model_name] = 0  # Current load
        
        return {
            "model_registered": model_name,
            "initial_metrics": {
                "response_time": metrics.response_time,
                "accuracy_score": metrics.accuracy_score,
                "specializations": list(metrics.specialization_score.keys())
            }
        }
    
    def route_task(self, task: str, task_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Routes a task to the most suitable model"""
        if not self.model_pool:
            return {"error": "No models available in pool"}
        
        # Analyze task characteristics
        task_chars = self._analyze_task_characteristics(task, task_metadata)
        
        # Select best model
        selected_model = self._select_optimal_model(task_chars)
        
        if not selected_model:
            return {"error": "No suitable model found"}
        
        # Execute task
        start_time = time.time()
        execution_result = self._execute_task(task, selected_model, task_chars)
        execution_time = time.time() - start_time
        
        # Update metrics
        self._update_model_metrics(selected_model, execution_result, execution_time, task_chars)
        
        # Log routing decision
        routing_decision = {
            "task_id": self._generate_task_id(task),
            "selected_model": selected_model,
            "task_type": task_chars.task_type.value,
            "execution_time": execution_time,
            "success": execution_result.get("success", False),
            "timestamp": self._get_timestamp()
        }
        self.routing_decisions.append(routing_decision)
        
        return {
            "routing_decision": routing_decision,
            "execution_result": execution_result,
            "model_selection_reasoning": self._explain_model_selection(selected_model, task_chars),
            "performance_prediction": self._predict_performance(selected_model, task_chars)
        }
    
    def dynamic_load_balancing(self) -> Dict[str, Any]:
        """Performs dynamic load balancing across models"""
        load_balance_result = {
            "current_loads": dict(self.load_balancer),
            "rebalancing_actions": [],
            "load_distribution": {},
            "recommendations": []
        }
        
        if not self.model_pool:
            return load_balance_result
        
        # Calculate load distribution
        total_load = sum(self.load_balancer.values())
        for model, load in self.load_balancer.items():
            load_balance_result["load_distribution"][model] = {
                "absolute_load": load,
                "relative_load": load / total_load if total_load > 0 else 0,
                "capacity_utilization": min(1.0, load / 100)  # Assuming max capacity of 100
            }
        
        # Identify overloaded and underloaded models
        avg_load = total_load / len(self.model_pool) if self.model_pool else 0
        overloaded = []
        underloaded = []
        
        for model, load in self.load_balancer.items():
            if load > avg_load * 1.5:
                overloaded.append(model)
            elif load < avg_load * 0.5:
                underloaded.append(model)
        
        # Generate rebalancing actions
        for overloaded_model in overloaded:
            if underloaded:
                target_model = underloaded[0]
                action = {
                    "action": "redirect_traffic",
                    "from_model": overloaded_model,
                    "to_model": target_model,
                    "percentage": 25
                }
                load_balance_result["rebalancing_actions"].append(action)
        
        # Generate recommendations
        if overloaded:
            load_balance_result["recommendations"].append(
                f"Consider scaling up models: {', '.join(overloaded)}"
            )
        
        if len(underloaded) > len(overloaded):
            load_balance_result["recommendations"].append(
                "Some models are underutilized. Consider consolidating workload."
            )
        
        return load_balance_result
    
    def performance_monitoring(self) -> Dict[str, Any]:
        """Monitors and reports on model performance"""
        monitoring_result = {
            "model_performance": {},
            "performance_trends": {},
            "alerts": [],
            "optimization_suggestions": []
        }
        
        for model_name, metrics in self.model_pool.items():
            # Current performance snapshot
            monitoring_result["model_performance"][model_name] = {
                "response_time": metrics.response_time,
                "accuracy_score": metrics.accuracy_score,
                "success_rate": metrics.success_rate,
                "resource_usage": metrics.resource_usage,
                "current_load": self.load_balancer.get(model_name, 0),
                "specializations": metrics.specialization_score
            }
            
            # Performance trends (simplified)
            if model_name in self.performance_history:
                history = self.performance_history[model_name]
                if len(history) > 1:
                    recent_times = [h["response_time"] for h in history[-5:]]
                    trend = "improving" if recent_times[-1] < recent_times[0] else "degrading"
                    monitoring_result["performance_trends"][model_name] = {
                        "response_time_trend": trend,
                        "average_response_time": statistics.mean(recent_times),
                        "response_time_variance": statistics.variance(recent_times) if len(recent_times) > 1 else 0
                    }
            
            # Generate alerts
            if metrics.response_time > 5.0:
                monitoring_result["alerts"].append({
                    "type": "high_response_time",
                    "model": model_name,
                    "value": metrics.response_time,
                    "threshold": 5.0
                })
            
            if metrics.success_rate < 0.8:
                monitoring_result["alerts"].append({
                    "type": "low_success_rate",
                    "model": model_name,
                    "value": metrics.success_rate,
                    "threshold": 0.8
                })
        
        # Generate optimization suggestions
        if monitoring_result["alerts"]:
            monitoring_result["optimization_suggestions"].append(
                "Consider retraining or replacing models with performance issues"
            )
        
        # Check for load imbalance
        loads = list(self.load_balancer.values())
        if loads and max(loads) > 2 * statistics.mean(loads):
            monitoring_result["optimization_suggestions"].append(
                "Load imbalance detected. Consider redistributing tasks."
            )
        
        return monitoring_result
    
    def _analyze_task_characteristics(self, task: str, metadata: Dict[str, Any]) -> TaskCharacteristics:
        """Analyzes task to determine its characteristics"""
        # Determine task type
        task_type = self._classify_task_type(task, metadata)
        
        # Calculate complexity (simplified heuristic)
        complexity = min(10, max(1, len(task.split()) // 10 + 1))
        
        # Estimate input/output lengths
        input_length = len(task)
        expected_output_length = metadata.get("expected_output_length", input_length // 2)
        
        return TaskCharacteristics(
            task_type=task_type,
            complexity_level=complexity,
            input_length=input_length,
            expected_output_length=expected_output_length,
            domain=metadata.get("domain", "general"),
            priority=metadata.get("priority", 3)
        )
    
    def _classify_task_type(self, task: str, metadata: Dict[str, Any]) -> TaskType:
        """Classifies the task type based on content and metadata"""
        task_lower = task.lower()
        
        # Check metadata first
        if "task_type" in metadata:
            try:
                return TaskType(metadata["task_type"])
            except ValueError:
                pass
        
        # Heuristic classification
        if any(keyword in task_lower for keyword in ["write code", "function", "class", "import", "def "]):
            return TaskType.CODE_GENERATION
        elif any(keyword in task_lower for keyword in ["analyze", "examine", "evaluate", "assess"]):
            return TaskType.ANALYSIS
        elif any(keyword in task_lower for keyword in ["write", "create story", "poem", "creative"]):
            return TaskType.CREATIVE_WRITING
        elif any(keyword in task_lower for keyword in ["summarize", "summary", "brief"]):
            return TaskType.SUMMARIZATION
        elif any(keyword in task_lower for keyword in ["translate", "translation"]):
            return TaskType.TRANSLATION
        elif any(keyword in task_lower for keyword in ["why", "how", "explain", "reason"]):
            return TaskType.REASONING
        elif "?" in task:
            return TaskType.QUESTION_ANSWERING
        else:
            return TaskType.TEXT_GENERATION
    
    def _select_optimal_model(self, task_chars: TaskCharacteristics) -> Optional[str]:
        """Selects the optimal model for the given task characteristics"""
        if not self.model_pool:
            return None
        
        model_scores = {}
        
        for model_name, metrics in self.model_pool.items():
            score = 0.0
            
            # Base performance score
            score += metrics.accuracy_score * 0.3
            score += (1.0 / max(0.1, metrics.response_time)) * 0.2
            score += metrics.success_rate * 0.2
            
            # Specialization bonus
            task_type_str = task_chars.task_type.value
            if task_type_str in metrics.specialization_score:
                score += metrics.specialization_score[task_type_str] * 0.2
            
            # Load balancing factor
            current_load = self.load_balancer.get(model_name, 0)
            load_penalty = min(0.1, current_load / 100)  # Max 10% penalty
            score -= load_penalty
            
            # Priority adjustment
            if task_chars.priority >= 4:  # High priority
                score += 0.1
            
            model_scores[model_name] = score
        
        # Select model with highest score
        best_model = max(model_scores.keys(), key=lambda k: model_scores[k])
        return best_model
    
    def _execute_task(self, task: str, model_name: str, task_chars: TaskCharacteristics) -> Dict[str, Any]:
        """Executes the task on the selected model"""
        # Update load balancer
        self.load_balancer[model_name] = self.load_balancer.get(model_name, 0) + 1
        
        try:
            # Create task-specific prompt
            prompt = self._create_optimized_prompt(task, task_chars)
            
            # Call Ollama
            result = self._call_ollama(prompt, model_name)
            
            return result
            
        finally:
            # Decrease load
            self.load_balancer[model_name] = max(0, self.load_balancer.get(model_name, 0) - 1)
    
    def _create_optimized_prompt(self, task: str, task_chars: TaskCharacteristics) -> str:
        """Creates an optimized prompt based on task characteristics"""
        base_prompt = task
        
        # Add task-specific instructions
        if task_chars.task_type == TaskType.CODE_GENERATION:
            base_prompt = f"Generate clean, well-commented code for: {task}"
        elif task_chars.task_type == TaskType.ANALYSIS:
            base_prompt = f"Provide a thorough analysis of: {task}"
        elif task_chars.task_type == TaskType.CREATIVE_WRITING:
            base_prompt = f"Write creatively about: {task}"
        elif task_chars.task_type == TaskType.SUMMARIZATION:
            base_prompt = f"Provide a concise summary of: {task}"
        
        # Add complexity guidance
        if task_chars.complexity_level > 7:
            base_prompt += "\n\nThis is a complex task. Please provide a detailed, step-by-step response."
        elif task_chars.complexity_level < 4:
            base_prompt += "\n\nPlease provide a clear, concise response."
        
        return base_prompt
    
    def _update_model_metrics(self, model_name: str, result: Dict[str, Any], execution_time: float, task_chars: TaskCharacteristics):
        """Updates model metrics based on execution results"""
        if model_name not in self.model_pool:
            return
        
        metrics = self.model_pool[model_name]
        
        # Update response time (exponential moving average)
        alpha = 0.3  # Learning rate
        metrics.response_time = alpha * execution_time + (1 - alpha) * metrics.response_time
        
        # Update success rate
        success = 1.0 if result.get("success", False) else 0.0
        metrics.success_rate = alpha * success + (1 - alpha) * metrics.success_rate
        
        # Update specialization scores
        task_type_str = task_chars.task_type.value
        if task_type_str not in metrics.specialization_score:
            metrics.specialization_score[task_type_str] = 0.5
        
        # Improve specialization score if successful
        if success:
            current_score = metrics.specialization_score[task_type_str]
            metrics.specialization_score[task_type_str] = min(1.0, current_score + 0.1)
        
        metrics.last_updated = self._get_timestamp()
        
        # Add to performance history
        if model_name not in self.performance_history:
            self.performance_history[model_name] = []
        
        self.performance_history[model_name].append({
            "timestamp": self._get_timestamp(),
            "response_time": execution_time,
            "success": success,
            "task_type": task_type_str
        })
        
        # Keep only last 100 records
        if len(self.performance_history[model_name]) > 100:
            self.performance_history[model_name] = self.performance_history[model_name][-100:]
    
    def _explain_model_selection(self, selected_model: str, task_chars: TaskCharacteristics) -> Dict[str, Any]:
        """Explains why a particular model was selected"""
        if selected_model not in self.model_pool:
            return {"error": "Model not found"}
        
        metrics = self.model_pool[selected_model]
        
        return {
            "selected_model": selected_model,
            "selection_factors": {
                "accuracy_score": metrics.accuracy_score,
                "response_time": metrics.response_time,
                "success_rate": metrics.success_rate,
                "specialization_match": metrics.specialization_score.get(task_chars.task_type.value, 0.0),
                "current_load": self.load_balancer.get(selected_model, 0)
            },
            "task_characteristics": {
                "type": task_chars.task_type.value,
                "complexity": task_chars.complexity_level,
                "domain": task_chars.domain,
                "priority": task_chars.priority
            }
        }
    
    def _predict_performance(self, model_name: str, task_chars: TaskCharacteristics) -> Dict[str, Any]:
        """Predicts performance for the selected model and task"""
        if model_name not in self.model_pool:
            return {"error": "Model not found"}
        
        metrics = self.model_pool[model_name]
        
        # Base predictions on current metrics
        predicted_response_time = metrics.response_time
        predicted_success_rate = metrics.success_rate
        
        # Adjust based on task characteristics
        if task_chars.complexity_level > 7:
            predicted_response_time *= 1.5
            predicted_success_rate *= 0.9
        elif task_chars.complexity_level < 4:
            predicted_response_time *= 0.8
            predicted_success_rate *= 1.05
        
        # Adjust based on specialization
        task_type_str = task_chars.task_type.value
        if task_type_str in metrics.specialization_score:
            specialization = metrics.specialization_score[task_type_str]
            predicted_success_rate *= (0.8 + 0.4 * specialization)  # 0.8 to 1.2 multiplier
        
        return {
            "predicted_response_time": min(10.0, predicted_response_time),
            "predicted_success_rate": min(1.0, predicted_success_rate),
            "confidence_level": 0.7  # Placeholder confidence
        }
    
    def _generate_task_id(self, task: str) -> str:
        """Generates a unique task ID"""
        import hashlib
        return hashlib.md5(f"{task}{time.time()}".encode()).hexdigest()[:8]
    
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
        
        task_type = input_data.get("task_type", "text_generation")
        performance_metrics = input_data.get("performance_metrics", {})
        model_pool = input_data.get("model_pool", [])
        task = input_data.get("task", "Process this request")
        
        router = AdaptiveModelRouter()
        
        # Register models
        registered_models = []
        if model_pool:
            for model_config in model_pool:
                registration_result = router.register_model(model_config)
                registered_models.append(registration_result)
        else:
            # Register default models
            default_models = [
                {
                    "name": "llama2",
                    "baseline_response_time": 2.0,
                    "baseline_accuracy": 0.8,
                    "specializations": {"text_generation": 0.9, "question_answering": 0.8}
                },
                {
                    "name": "codellama",
                    "baseline_response_time": 2.5,
                    "baseline_accuracy": 0.85,
                    "specializations": {"code_generation": 0.95, "analysis": 0.7}
                },
                {
                    "name": "mistral",
                    "baseline_response_time": 1.8,
                    "baseline_accuracy": 0.82,
                    "specializations": {"creative_writing": 0.9, "reasoning": 0.85}
                }
            ]
            
            for model_config in default_models:
                registration_result = router.register_model(model_config)
                registered_models.append(registration_result)
        
        # Route task
        task_metadata = {
            "task_type": task_type,
            "domain": input_data.get("domain", "general"),
            "priority": input_data.get("priority", 3),
            "expected_output_length": input_data.get("expected_output_length", 100)
        }
        
        routing_result = router.route_task(task, task_metadata)
        
        # Get performance monitoring
        monitoring_result = router.performance_monitoring()
        
        # Get load balancing status
        load_balance_result = router.dynamic_load_balancing()
        
        # Combine results
        result = {
            "model_registration": registered_models,
            "task_routing": routing_result,
            "performance_monitoring": monitoring_result,
            "load_balancing": load_balance_result,
            "router_metrics": {
                "total_models": len(router.model_pool),
                "total_routing_decisions": len(router.routing_decisions),
                "average_load": sum(router.load_balancer.values()) / len(router.load_balancer) if router.load_balancer else 0
            }
        }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "tool": "adaptive_model_router"
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main()