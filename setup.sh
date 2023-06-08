echo -e "Creating new virtual environment aliklemencic_proj1..."

python3 -m venv aliklemencic_proj1

echo -e "Installing Requirements..."

source aliklemencic_proj1/bin/activate
pip3 install -r requirements.txt

echo -e "Setup is complete."
