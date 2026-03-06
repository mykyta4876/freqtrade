# Freqtrade Runner Script
# This script sets up the environment and runs freqtrade without needing to install it

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
}

# Add current directory to PYTHONPATH
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"

# Run freqtrade with all passed arguments
python -m freqtrade $args
