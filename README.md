ansible-galaxy install -r requirements.yml
ansible-playbook deploy/main.yaml --tags docker -i deploy/inventory.yaml -u root -u root --private-key ~/.ssh/id_ed25519