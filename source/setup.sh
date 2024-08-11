apt-get install python3 -y
apt-get install python3-pip -y
apt-get install build-essential

pip3 install --upgrade pip

# For some damn reason Pip has a bug that causes the pyproject.toml not to work if pip is below 24
# Great work python foundation. Pyproject.toml has only been out for 8 years and is the recommended
# packaging method
pip3 install -r /autograder/source/requirements.txt
