#!/bin/bash

# Define the path to your .env file
ENV_FILE=".env"

# --- Create .env if it doesn't exist ---
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env file..."
    touch "$ENV_FILE"
    # Populate with default values
    echo "OLLAMA_API_BASE_URL=http://localhost:11434/api" >> "$ENV_FILE"
    echo "DATABASE_URL=sqlite:///./sql_app.db" >> "$ENV_FILE"
    echo "ALGORITHM=HS256" >> "$ENV_FILE"
    echo "ACCESS_TOKEN_EXPIRE_MINUTES=30" >> "$ENV_FILE"
fi

# --- Check for SECRET_KEY and generate if missing ---
# The `grep -q` command quietly checks if the string exists
if ! grep -q "SECRET_KEY=" "$ENV_FILE"; then
    echo "SECRET_KEY not found. Generating a new one..."
    # Generate a secure 32-byte hex key and add it to the .env file
    NEW_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
    echo "SECRET_KEY=$NEW_KEY" >> "$ENV_FILE"
    echo "New SECRET_KEY added to .env file."
else
    echo "SECRET_KEY already exists in .env file."
fi

# --- (Rest of setup script for checking Ollama, pulling models, etc.) ---
echo "Setup checks complete - Initiating TP 🧻 🧑‍💻👩‍💻👨‍💻!"
#!/bin/bash

# --- 1. Check for Ollama ---
echo "Checking for Ollama installation..."
if ! command -v ollama &> /dev/null
then
    echo "Ollama could not be found."
    read -p "Would you like to download it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        # Add commands to download Ollama for user's OS
        # Example for macOS:
        # curl -L https://ollama.com/download/ollama-darwin-amd64 -o ollama && chmod +x ollama && sudo mv ollama /usr/local/bin/
        echo "Please follow the official Ollama installation instructions for your OS."
    fi
else
    echo "Ollama is installed."
    # Optional: Check for updates
    # ollama pull ollama/ollama
fi

# --- 2. Set Up Project Directories ---
# Find the user's home directory to locate the .ollama folder
OLLAMA_DIR="$HOME/.ollama"
MODELS_DIR="$OLLAMA_DIR/models"
DASHBOARD_DIR="$OLLAMA_DIR/dashboard" # Your project's home

echo "Setting up project directories in $DASHBOARD_DIR..."
# Create the dashboard directory if it doesn't exist
mkdir -p "$DASHBOARD_DIR"
# Logic to move your project files into this directory would go here

# --- 3. Download a Base Model ---
echo "Checking for a base model..."
# A simple way to check is to see if a specific model manifest exists
if [ ! -f "$MODELS_DIR/manifests/registry.ollama.ai/library/llama3/latest" ]; then
    echo "No base model found. Pulling llama3..."
    ollama pull llama3
else
    echo "Base model (llama3) already present."
fi


# --- 4. Dynamically Update File Paths and Create Tool Registry ---
echo "Scanning for models and updating tool registry..."
# This is a great place to use a Python script for more complex JSON manipulation
python update_registry.py

echo "Setup complete! You can now start the dashboard."

