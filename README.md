# server
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# local
ansible-galaxy install -r requirements.yml
ansible-playbook deploy/main.yaml --tags docker -i deploy/inventory.yaml -u root --private-key ~/.ssh/id_ed25519