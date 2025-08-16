# Tool Development Guide

## Quick Reference

### Python Tool Template
```python
#!/usr/bin/env python3
"""
Template for Ollama TP Dashboard tools
"""
import sys
import json
import os

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Extract parameters
        param1 = input_data.get("param1", "default_value")
        param2 = input_data.get("param2", "")
        
        # Your tool logic here
        result = process_your_logic(param1, param2)
        
        # Always output JSON
        print(json.dumps({
            "success": True,
            "result": result,
            "tool": "your_tool_name",
            "metadata": {
                "execution_time": "...",
                "version": "1.0"
            }
        }))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "tool": "your_tool_name"
        }))

def process_your_logic(param1, param2):
    """Your main tool logic"""
    # Implementation here
    return {"processed": f"{param1} + {param2}"}

if __name__ == "__main__":
    main()
```

### Node.js Tool Template
```javascript
#!/usr/bin/env node
/**
 * Template for Ollama TP Dashboard Node.js tools
 */

const fs = require('fs');

function main() {
    try {
        // Read JSON input from stdin
        const input = fs.readFileSync(0, 'utf-8');
        const inputData = JSON.parse(input);
        
        // Extract parameters
        const param1 = inputData.param1 || 'default_value';
        const param2 = inputData.param2 || '';
        
        // Your tool logic here
        const result = processYourLogic(param1, param2);
        
        // Always output JSON
        console.log(JSON.stringify({
            success: true,
            result: result,
            tool: 'your_tool_name',
            metadata: {
                execution_time: Date.now(),
                version: '1.0'
            }
        }));
        
    } catch (error) {
        console.log(JSON.stringify({
            success: false,
            error: error.message,
            tool: 'your_tool_name'
        }));
    }
}

function processYourLogic(param1, param2) {
    // Your main tool logic
    return { processed: `${param1} + ${param2}` };
}

if (require.main === module) {
    main();
}
```

## Registry Entry Template
```json
{
  "id": "your_tool_unique_id",
  "name": "Your Tool Display Name",
  "description": "Clear description of what your tool does and when to use it",
  "script": "./tools/your_tool.py",
  "type": "python",
  "parameters": ["param1", "param2"],
  "features": ["feature1", "feature2"],
  "dependencies": ["ollama_client"],
  "category": "analysis",
  "tags": ["ai", "processing", "text"],
  "version": "1.0.0",
  "author": "Your Name",
  "documentation": "./docs/your_tool.md"
}
```

## Ollama Integration Examples

### Using Ollama Client
```python
#!/usr/bin/env python3
import sys
import json
import requests

def call_ollama(prompt, model="llama2"):
    """Call Ollama API"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json().get("response", "")
    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}")

def main():
    try:
        input_data = json.load(sys.stdin)
        
        text = input_data.get("text", "")
        model = input_data.get("model", "llama2")
        task = input_data.get("task", "summarize")
        
        # Create prompt based on task
        if task == "summarize":
            prompt = f"Please summarize the following text:\n\n{text}"
        elif task == "analyze":
            prompt = f"Please analyze the key themes in:\n\n{text}"
        else:
            prompt = f"Please process this text for {task}:\n\n{text}"
        
        # Call Ollama
        result = call_ollama(prompt, model)
        
        print(json.dumps({
            "success": True,
            "result": result,
            "tool": "ollama_text_processor",
            "model_used": model,
            "task": task
        }))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "tool": "ollama_text_processor"
        }))

if __name__ == "__main__":
    main()
```

### Multi-Model Consensus Tool
```python
#!/usr/bin/env python3
import sys
import json
import requests
from collections import Counter

def query_models(prompt, models=["llama2", "mistral", "codellama"]):
    """Query multiple models and return consensus"""
    responses = []
    
    for model in models:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                responses.append({"model": model, "response": result})
        except Exception as e:
            responses.append({"model": model, "error": str(e)})
    
    return responses

def main():
    try:
        input_data = json.load(sys.stdin)
        
        prompt = input_data.get("prompt", "")
        models = input_data.get("models", ["llama2", "mistral"])
        consensus_method = input_data.get("consensus_method", "majority")
        
        if not prompt:
            raise ValueError("Prompt is required")
        
        # Query all models
        responses = query_models(prompt, models)
        
        # Analyze responses
        successful_responses = [r for r in responses if "error" not in r]
        
        if not successful_responses:
            raise Exception("All models failed to respond")
        
        # Simple consensus logic
        if consensus_method == "majority":
            # For now, just return all responses
            consensus = {
                "method": "all_responses",
                "responses": successful_responses,
                "confidence": len(successful_responses) / len(models)
            }
        else:
            consensus = successful_responses[0]  # First successful response
        
        print(json.dumps({
            "success": True,
            "result": consensus,
            "tool": "multi_model_consensus",
            "models_queried": len(models),
            "successful_responses": len(successful_responses)
        }))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "tool": "multi_model_consensus"
        }))

if __name__ == "__main__":
    main()
```

## Advanced Patterns

### Tool Chaining Support
```python
def main():
    try:
        input_data = json.load(sys.stdin)
        
        # Support chaining by accepting previous tool output
        if "previous_result" in input_data:
            # This tool can work with output from another tool
            previous = input_data["previous_result"]
            text = previous.get("result", input_data.get("text", ""))
        else:
            text = input_data.get("text", "")
        
        # Your processing logic
        result = process_text(text)
        
        print(json.dumps({
            "success": True,
            "result": result,
            "tool": "chainable_tool",
            "chainable": True,  # Indicates this tool supports chaining
            "output_format": "text"  # Helps next tool know what to expect
        }))
        
    except Exception as e:
        # Error handling...
```

### Configuration-Driven Tools
```python
def load_tool_config():
    """Load tool-specific configuration"""
    config_path = "./config/tool_config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {
            "default_model": "llama2",
            "timeout": 30,
            "max_retries": 3
        }

def main():
    try:
        input_data = json.load(sys.stdin)
        config = load_tool_config()
        
        # Use configuration
        model = input_data.get("model", config["default_model"])
        timeout = config["timeout"]
        
        # Tool logic with config...
```

## Testing Your Tools

### Unit Testing Template
```python
#!/usr/bin/env python3
"""
Test your tool independently
"""
import json
import subprocess
import sys

def test_tool(tool_script, test_input, expected_fields=None):
    """Test a tool with given input"""
    try:
        # Run the tool
        proc = subprocess.Popen(
            ["python3", tool_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = proc.communicate(input=json.dumps(test_input))
        
        if proc.returncode != 0:
            print(f"Tool failed with error: {stderr}")
            return False
        
        # Parse output
        try:
            result = json.loads(stdout)
        except json.JSONDecodeError:
            print(f"Tool output is not valid JSON: {stdout}")
            return False
        
        # Check required fields
        required_fields = ["success", "tool"]
        if expected_fields:
            required_fields.extend(expected_fields)
        
        for field in required_fields:
            if field not in result:
                print(f"Missing required field: {field}")
                return False
        
        print(f"✓ Tool test passed: {result}")
        return True
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        return False

# Example test cases
test_cases = [
    {
        "name": "Basic functionality",
        "input": {"text": "Hello world", "param1": "test"},
        "expected": ["result"]
    },
    {
        "name": "Empty input handling",
        "input": {},
        "expected": ["result"]
    },
    {
        "name": "Error handling",
        "input": {"invalid": "data"},
        "expected": []  # Should handle gracefully
    }
]

if __name__ == "__main__":
    tool_script = sys.argv[1] if len(sys.argv) > 1 else "your_tool.py"
    
    print(f"Testing tool: {tool_script}")
    
    for test_case in test_cases:
        print(f"\nRunning test: {test_case['name']}")
        success = test_tool(
            tool_script, 
            test_case["input"], 
            test_case.get("expected")
        )
        if not success:
            print(f"❌ Test failed: {test_case['name']}")
            sys.exit(1)
    
    print("\n✅ All tests passed!")
```

## Best Practices

1. **Always handle errors gracefully**
2. **Use consistent JSON input/output format**
3. **Include metadata in responses**
4. **Make tools configurable when possible**
5. **Support tool chaining where appropriate**
6. **Test thoroughly with edge cases**
7. **Document parameters clearly**
8. **Follow naming conventions**
9. **Include version information**
10. **Make tools idempotent when possible**

## Deployment Checklist

- [ ] Tool script is executable
- [ ] JSON input/output protocol implemented
- [ ] Error handling included
- [ ] Registry entry is complete
- [ ] Dependencies are documented
- [ ] Tool has been tested independently
- [ ] Documentation is clear
- [ ] Performance is acceptable
- [ ] Security considerations addressed
- [ ] Tool follows naming conventions
