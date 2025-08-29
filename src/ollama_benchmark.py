#!/usr/bin/env python3
"""
Ollama Model Benchmarking Tool
==============================

Benchmarks token throughput and memory footprint for different Ollama models
to determine optimal primary/fallback order for the Next-Gen environment.
"""

import asyncio
import json
import logging
import requests
import time
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass
import statistics

@dataclass
class BenchmarkResult:
    """Results from model benchmarking"""
    model_name: str
    tokens_per_second: float
    memory_usage_mb: float
    response_time_avg: float
    response_time_std: float
    success_rate: float
    error_count: int
    total_requests: int

class OllamaBenchmark:
    """Benchmark tool for Ollama models"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.logger = logging.getLogger(__name__)
        
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            self.logger.error(f"Failed to get models: {e}")
            return []
    
    def generate_test_prompts(self) -> List[str]:
        """Generate test prompts of varying lengths"""
        return [
            # Short prompt (equipment identification)
            "Analyze this auction listing: '2010 Kenworth T800 Commercial Truck with hydraulic crane attachment.' Identify equipment type and estimated value.",
            
            # Medium prompt (detailed analysis)
            """Analyze this government auction listing for high-value equipment:
            Title: Construction Equipment Lot - Various Items
            Description: Multiple pieces of construction equipment including tracked vehicles, hydraulic systems, and specialized tools. Items show normal wear but operational. Buyer responsible for pickup.
            Location: Houston, TX
            
            Identify: 1) Equipment types 2) Potential hidden value 3) Market estimate 4) Risk factors""",
            
            # Long prompt (comprehensive analysis)
            """You are an expert equipment appraiser analyzing a government auction. Please provide a comprehensive analysis:

            AUCTION DETAILS:
            Title: Heavy Equipment and Vehicle Auction - City Surplus
            Description: Large lot including various construction and utility vehicles. Items include: tracked excavators with rubber undercarriage systems, commercial trucks (Kenworth, Peterbilt models), hydraulic lift equipment with boom attachments, specialized drilling equipment possibly including cone penetrometer systems, and miscellaneous tools and attachments. Equipment has been maintained by city crews but shows operational wear. All items sold as-is with no warranties. Successful bidders must coordinate pickup within 14 days.
            Location: Denver, CO
            Category: Heavy Equipment & Vehicles
            Starting Bid: $50,000
            
            ANALYSIS REQUIREMENTS:
            1. Identify all specific equipment types mentioned or implied
            2. Estimate fair market value for each category
            3. Assess profit potential considering auction dynamics
            4. Flag any specialized equipment that might be undervalued
            5. Consider location-specific market factors
            6. Provide bidding strategy recommendations
            7. Identify risks and due diligence requirements
            
            Please format your response as detailed JSON with all findings."""
        ]
    
    async def benchmark_model(self, model_name: str, num_requests: int = 10) -> BenchmarkResult:
        """Benchmark a specific model"""
        print(f"\n🔍 Benchmarking {model_name}...")
        
        test_prompts = self.generate_test_prompts()
        response_times = []
        token_counts = []
        errors = 0
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        for i in range(num_requests):
            prompt = test_prompts[i % len(test_prompts)]
            
            try:
                start_time = time.time()
                
                # Make request to Ollama
                response = requests.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.9
                        }
                    },
                    timeout=60
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    
                    # Estimate token count (rough approximation: 1 token ≈ 4 characters)
                    token_count = len(response_text) / 4
                    tokens_per_second = token_count / response_time if response_time > 0 else 0
                    
                    response_times.append(response_time)
                    token_counts.append(tokens_per_second)
                    
                    print(f"  Request {i+1}/{num_requests}: {response_time:.2f}s, {tokens_per_second:.1f} tok/s")
                else:
                    errors += 1
                    print(f"  Request {i+1}/{num_requests}: ERROR {response.status_code}")
                    
            except Exception as e:
                errors += 1
                print(f"  Request {i+1}/{num_requests}: EXCEPTION {str(e)[:50]}...")
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = final_memory - initial_memory
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            std_response_time = statistics.stdev(response_times) if len(response_times) > 1 else 0.0
            avg_tokens_per_sec = statistics.mean(token_counts) if token_counts else 0.0
        else:
            avg_response_time = 0.0
            std_response_time = 0.0
            avg_tokens_per_sec = 0.0
        
        success_rate = (num_requests - errors) / num_requests if num_requests > 0 else 0.0
        
        return BenchmarkResult(
            model_name=model_name,
            tokens_per_second=avg_tokens_per_sec,
            memory_usage_mb=memory_usage,
            response_time_avg=avg_response_time,
            response_time_std=std_response_time,
            success_rate=success_rate,
            error_count=errors,
            total_requests=num_requests
        )
    
    async def run_comprehensive_benchmark(self) -> Dict[str, BenchmarkResult]:
        """Run comprehensive benchmark on all available models"""
        models = self.get_available_models()
        
        if not models:
            print("❌ No models available for benchmarking")
            return {}
        
        print(f"🚀 Starting comprehensive benchmark on {len(models)} models")
        print("=" * 60)
        
        results = {}
        
        for model in models:
            try:
                result = await self.benchmark_model(model, num_requests=5)
                results[model] = result
                
                print(f"\n📊 Results for {model}:")
                print(f"   Tokens/sec: {result.tokens_per_second:.1f}")
                print(f"   Memory usage: {result.memory_usage_mb:.1f} MB")
                print(f"   Avg response time: {result.response_time_avg:.2f}s")
                print(f"   Success rate: {result.success_rate:.1%}")
                
            except Exception as e:
                print(f"❌ Failed to benchmark {model}: {e}")
        
        return results
    
    def analyze_results_and_create_queue(self, results: Dict[str, BenchmarkResult]) -> List[str]:
        """Analyze results and create optimal model queue"""
        if not results:
            return []
        
        print(f"\n🎯 Creating optimal model queue...")
        print("=" * 60)
        
        # Create scoring system
        scored_models = []
        
        for model_name, result in results.items():
            if result.success_rate == 0:
                continue
                
            # Scoring factors (higher is better)
            speed_score = min(result.tokens_per_second / 10, 10)  # Cap at 10
            reliability_score = result.success_rate * 10
            efficiency_score = max(0, 10 - (result.memory_usage_mb / 100))  # Penalize high memory
            responsiveness_score = max(0, 10 - result.response_time_avg)  # Penalize slow response
            
            total_score = (speed_score * 0.3 + 
                          reliability_score * 0.4 + 
                          efficiency_score * 0.2 + 
                          responsiveness_score * 0.1)
            
            scored_models.append({
                'model': model_name,
                'score': total_score,
                'tokens_per_second': result.tokens_per_second,
                'memory_mb': result.memory_usage_mb,
                'response_time': result.response_time_avg,
                'success_rate': result.success_rate
            })
            
            print(f"{model_name}:")
            print(f"  Speed: {speed_score:.1f}/10 ({result.tokens_per_second:.1f} tok/s)")
            print(f"  Reliability: {reliability_score:.1f}/10 ({result.success_rate:.1%})")
            print(f"  Efficiency: {efficiency_score:.1f}/10 ({result.memory_usage_mb:.1f} MB)")
            print(f"  Responsiveness: {responsiveness_score:.1f}/10 ({result.response_time_avg:.2f}s)")
            print(f"  TOTAL SCORE: {total_score:.1f}/10")
            print()
        
        # Sort by score (descending)
        scored_models.sort(key=lambda x: x['score'], reverse=True)
        
        # Create queue
        model_queue = [model['model'] for model in scored_models]
        
        print("🏆 OPTIMAL MODEL QUEUE (Primary → Fallback):")
        for i, model_info in enumerate(scored_models, 1):
            print(f"  {i}. {model_info['model']} (Score: {model_info['score']:.1f})")
        
        return model_queue

async def main():
    """Main benchmarking routine"""
    logging.basicConfig(level=logging.INFO)
    
    print("🔥 Ollama Model Benchmarking Tool")
    print("=" * 50)
    
    benchmark = OllamaBenchmark()
    
    # Check available models
    models = benchmark.get_available_models()
    if not models:
        print("❌ No models found. Make sure Ollama is running and models are installed.")
        return
    
    print(f"📋 Available models: {', '.join(models)}")
    
    # Run benchmark
    results = await benchmark.run_comprehensive_benchmark()
    
    if results:
        # Create optimal queue
        optimal_queue = benchmark.analyze_results_and_create_queue(results)
        
        # Save results
        benchmark_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': {name: {
                'tokens_per_second': r.tokens_per_second,
                'memory_usage_mb': r.memory_usage_mb,
                'response_time_avg': r.response_time_avg,
                'response_time_std': r.response_time_std,
                'success_rate': r.success_rate,
                'error_count': r.error_count,
                'total_requests': r.total_requests
            } for name, r in results.items()},
            'optimal_queue': optimal_queue
        }
        
        with open('ollama_benchmark_results.json', 'w') as f:
            json.dump(benchmark_data, f, indent=2)
        
        print(f"\n💾 Results saved to: ollama_benchmark_results.json")
        print(f"\n🎯 Recommended model queue for OllamaLocalAnalyzer:")
        print(f"   {optimal_queue}")
    
    else:
        print("❌ No benchmark results obtained")

if __name__ == "__main__":
    asyncio.run(main())
