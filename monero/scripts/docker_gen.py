import sys
import yaml
import argparse
# import logging
# import os

# log_directory = '/home/umbrel/umbrel/app-data/monero/data/log'
# os.makedirs(log_directory, exist_ok=True)

# log_file_path = os.path.join(log_directory, "docker_gen.log")

# # Configure logging
# logging.basicConfig(
#     level=logging.DEBUG,  # Set the log level to DEBUG to capture all types of log messages
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define the log message format
#     handlers=[
#         logging.FileHandler(log_file_path)  # Log to a file
#     ]
# )

# logger = logging.getLogger(__name__)

# Define the environment variables and volume to add/remove for BTCPay
btcpay_environment_variables = {
    "BTCPAY_XMR_DAEMON_URI": "http://${APP_MONERO_NODE_IP}:${APP_MONERO_RPC_PORT}",
    "BTCPAY_XMR_DAEMON_USERNAME": "${APP_MONERO_RPC_USER}",
    "BTCPAY_XMR_DAEMON_PASSWORD": "${APP_MONERO_RPC_PASS}",
    "BTCPAY_XMR_WALLET_DAEMON_URI": "http://${APP_MONERO_WALLET_IP}:${APP_MONERO_WALLET_PORT}",
    "BTCPAY_XMR_WALLET_DAEMON_WALLETDIR": "/wallet/xmr_wallet",
}

btcpay_volume_to_add = "${APP_MONERO_WALLET_DATA_DIR}:/wallet/xmr_wallet"

# Define the Monero wallet service
monero_wallet_service = {
    'restart': 'unless-stopped',
    'container_name': 'btcpayserver_monero_wallet',
    'image': 'btcpayserver/monero:0.18.3.3',
    'entrypoint': 'monero-wallet-rpc --daemon-login=${APP_MONERO_RPC_USER}:${APP_MONERO_RPC_PASS} --rpc-bind-ip=0.0.0.0 --disable-rpc-login --log-level=2 --confirm-external-bind --rpc-bind-port=18082 --non-interactive --trusted-daemon  --daemon-address=monero_monerod_1:18081 --wallet-dir=/wallet --tx-notify="/bin/sh ./scripts/notifier.sh  -X GET http://btcpay-server_web_1:3003/monerolikedaemoncallback/tx?cryptoCode=xmr&hash=%s"',
    'ports': [
        '${APP_MONERO_WALLET_PORT}:${APP_MONERO_WALLET_PORT}'
    ],
    'volumes': [
        '${APP_MONERO_WALLET_DATA_DIR}:/wallet'
    ],
    'depends_on': [
        'monerod'
    ],
    'user': '1000:1000',
    'networks': {
        'default': {
            'ipv4_address': '$APP_MONERO_WALLET_IP'
        }
    }
}

# Define the p2pool service
p2pool_service = {
    'restart': 'unless-stopped',
    'container_name': 'p2pool',
    'image': 'ghcr.io/sethforprivacy/p2pool:latest',
    'tty': True,
    'stdin_open': True,
    'volumes': [
        '${APP_DATA_DIR}/data/p2pool:/home/p2pool',
        '/dev/hugepages:/dev/hugepages:rw'
    ],
    'ports': [
        '3333:3333',
        '37889:37889'
    ],
    'command': '--wallet "${APP_MONERO_WALLET}" --host ${APP_MONERO_NODE_IP} --stratum "0.0.0.0:3333" --rpc-login "${APP_MONERO_RPC_USER}:${APP_MONERO_RPC_PASS}" --p2p "0.0.0.0:37889" --zmq-port "${APP_MONERO_ZMQ_PORT}" --addpeers "65.21.227.114:37889,node.sethforprivacy.com:37889" --rpc-port "${APP_MONERO_RPC_PORT}"  --light-mode  --loglevel "2" --mini',
    'networks': {
        'default': {
            'ipv4_address': '$APP_P2POOL_IP'
        }
    }
}

def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def save_yaml(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False)

def add_variables(service, environment_variables, volume_to_add):
    changes = False
    if 'environment' not in service:
        service['environment'] = {}
    service['environment'].update(environment_variables)

    if 'volumes' not in service:
        service['volumes'] = []
    if volume_to_add not in service['volumes']:
        service['volumes'].append(volume_to_add)
        changes = True

    return changes

def remove_variables(service, environment_variables, volume_to_add):
    changes = False
    if 'environment' in service:
        for key in environment_variables.keys():
            service['environment'].pop(key, None)

    if 'volumes' in service and volume_to_add in service['volumes']:
        service['volumes'].remove(volume_to_add)
        changes = True

    return changes

def update_monero_wallet_service(data, action):
    changes = False
    if action == 'add':
        if 'monerod_wallet' not in data['services']:
            data['services']['monerod_wallet'] = monero_wallet_service
            changes = True
    elif action == 'remove':
        if 'monerod_wallet' in data['services']:
            data['services'].pop('monerod_wallet', None)
            changes = True

    return changes

def update_p2pool_service(data, action):
    changes = False
    if action == 'add':
        if 'p2pool' not in data['services']:
            data['services']['p2pool'] = p2pool_service
            changes = True
    elif action == 'remove':
        if 'p2pool' in data['services']:
            data['services'].pop('p2pool', None)
            changes = True

    return changes

def main(action, service_type, compose_file):
    data = load_yaml(compose_file)
    changes = False

    if service_type == 'btcpay':
        if 'web' in data['services']:
            service = data['services']['web']
            if action == 'add':
                changes = add_variables(service, btcpay_environment_variables, btcpay_volume_to_add)
                service['environment']['BTCPAY_CHAINS'] = "btc,xmr"
            elif action == 'remove':
                changes = remove_variables(service, btcpay_environment_variables, btcpay_volume_to_add)
                service['environment']['BTCPAY_CHAINS'] = "btc"
        else:
            print("BTCPayserver service not found in docker-compose.yml")
            return
    elif service_type == 'p2pool':
        changes = update_p2pool_service(data, action)
    elif service_type == 'monero':
        changes = update_monero_wallet_service(data, action)
    else:
        print("Invalid service type. Use 'btcpay', p2pool, or 'monero'.")
        return

    if changes:
        save_yaml(compose_file, data)
        print("docker-compose.yml updated successfully")
        return 1
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add or remove services in docker-compose.yml.')
    parser.add_argument('action', choices=['add', 'remove'], help='Action to perform: add or remove the service')
    parser.add_argument('service_type', choices=['btcpay', 'monero', 'p2pool'], help='Service type to update: btcpay, monero or p2pool')
    parser.add_argument('compose_file', help='Path to the docker-compose.yml file')
    args = parser.parse_args()

    result = main(args.action, args.service_type, args.compose_file)
    sys.exit(result)