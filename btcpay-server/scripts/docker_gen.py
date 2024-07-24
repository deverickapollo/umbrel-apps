import sys

import yaml

# Define the environment variables and volume to add/remove
environment_variables = {
    "BTCPAY_XMR_DAEMON_URI": "http://${APP_MONERO_NODE_IP}:${APP_MONERO_RPC_PORT}",
    "BTCPAY_XMR_DAEMON_USERNAME": "${APP_MONERO_RPC_USER}",
    "BTCPAY_XMR_DAEMON_PASSWORD": "${APP_MONERO_RPC_PASS}",
    "BTCPAY_XMR_WALLET_DAEMON_URI": "http://${APP_MONERO_WALLET_IP}:${APP_MONERO_WALLET_PORT}",
    "BTCPAY_XMR_WALLET_DAEMON_WALLETDIR": "${APP_MONERO_WALLET_DATA_DIR}",
}

VOLUME_TO_ADD = "xmr_wallet:/root/xmr_wallet"

def add_variables(service):
    if 'environment' not in service:
        service['environment'] = {}
    service['environment'].update(environment_variables)

    if 'volumes' not in service:
        service['volumes'] = []
    if VOLUME_TO_ADD not in service['volumes']:
        service['volumes'].append(VOLUME_TO_ADD)

def remove_variables(service):
    if 'environment' in service:
        for key in environment_variables.keys():
            if key in service['environment']:
                del service['environment'][key]

    if 'volumes' in service:
        if VOLUME_TO_ADD in service['volumes']:
            service['volumes'].remove(VOLUME_TO_ADD)

def main(action):
    # Load the docker-compose.yml file
    with open('docker-compose.yml', 'r', encoding='utf-8') as file:
        docker_compose = yaml.safe_load(file)

    # Check if the btcpayserver service exists
    if 'web' in docker_compose['services']:
        service = docker_compose['services']['web']
        if action == 'add':
            add_variables(service)
        elif action == 'remove':
            remove_variables(service)
        else:
            print("Invalid action. Use 'add' or 'remove'.")
            return

        # Save the modified docker-compose.yml file
        with open('docker-compose.yml', 'w', encoding='utf-8') as file:
            yaml.dump(docker_compose, file, default_flow_style=False)

        print("docker-compose.yml updated successfully")
    else:
        print("BTCPayserver service not found in docker-compose.yml")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python docker_gen.py <add|remove>")
    else:
        action = sys.argv[1]
        main(action)