#!/bin/bash

# Check for a command that runs Python 3
for CMD in python3 python py; do
    $CMD -c "import sys; sys.exit(sys.version_info < (3,))" &>/dev/null
    if [ $? -eq 0 ]; then
        PYTHON_CMD=$CMD
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "This script requires Python 3, but it's not installed."
    exit 1
fi

# Create a virtual environment
$PYTHON_CMD -m venv ../virtual_environments_smell_like_updog --prompt="virtual environment"

# Activate the virtual environment
source virtual_environments_smell_like_updog/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create a directory for the models
mkdir -p models

# Set the Transformers cache directory
export TRANSFORMERS_CACHE=./models/transformers_cache

# Download the Transformers model
$PYTHON_CMD -c "from transformers import GPTNeoForCausalLM; GPTNeoForCausalLM.from_pretrained('EleutherAI/gpt-neo-1.3B')"

# Download the spaCy model
$PYTHON_CMD -m spacy download en_core_web_md
#In Terminal: python3 -m pip uninstall en_core_web_md

# Run your Python script
$PYTHON_CMD Legit/JobSearchWorkflow.py

# Deactivate the virtual environment
deactivate