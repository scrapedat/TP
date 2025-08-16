import os
import json

# Define the paths based on the user's home directory
home_dir = os.path.expanduser("~")
models_dir = os.path.join(home_dir, ".ollama", "models", "manifests", "registry.ollama.ai", "library")
dashboard_dir = os.path.join(home_dir, ".ollama", "dashboard")
registry_path = os.path.join(dashboard_dir, "tool_registry.json")

def scan_models_and_update_registry():
    """
    Scans the Ollama models directory, finds associated tools in the dashboard,
    and creates a JSON registry mapping models to their tools with absolute paths.
    """
    installed_models = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
    
    model_tool_registry = {}

    print(f"Found models: {installed_models}")

    for model_name in installed_models:
        # Assumes your tool files are stored in a 'tools' directory
        # within your dashboard project, organized by model name.
        # e.g., .ollama/dashboard/tools/llama3/calculator.py
        
        tool_directory = os.path.join(dashboard_dir, "tools", model_name)
        
        if os.path.exists(tool_directory):
            tools_for_model = []
            for tool_file in os.listdir(tool_directory):
                # We want the full, absolute path for the AI to use
                full_path = os.path.abspath(os.path.join(tool_directory, tool_file))
                tools_for_model.append({
                    "tool_name": os.path.splitext(tool_file)[0],
                    "path": full_path,
                    "type": os.path.splitext(tool_file)[1] # .py, .js, etc.
                })
            
            model_tool_registry[model_name] = tools_for_model
    
    # Write the updated registry to a JSON file
    with open(registry_path, 'w') as f:
        json.dump(model_tool_registry, f, indent=4)
        
    print(f"Tool registry updated successfully at {registry_path}")

if __name__ == "__main__":
    scan_models_and_update_registry()

