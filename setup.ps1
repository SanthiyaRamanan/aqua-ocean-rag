Set-Location $PSScriptRoot
python -m pip install --user -r requirements.txt
Start-Process "http://127.0.0.1:5000"
python app.py
