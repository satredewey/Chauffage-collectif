python -m venv venv

call "venv/Scripts/activate.bat"

pip install -r "requirements.txt"

copy "default_commands/launch.bat" "launch.bat"

python.exe -m pip install --upgrade pip