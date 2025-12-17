	#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Setup complete."