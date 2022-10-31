if [ "$1" == "venv" ]; then
    source ./.venv/Scripts/activate
else
    python3 app.py
fi