import os
import yaml
import argparse
import sys

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def save_yaml(file_path, data):
    with open(file_path, 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False)

def update_monero_wallet_service(compose_file, action):
    data = load_yaml(compose_file)

    # Define the Monero wallet service
    monero_wallet_service = {
        'restart': 'unless-stopped',
        'container_name': 'btcpayserver_monero_wallet',
        'image': 'btcpayserver/monero:0.18.3.3',
        'entrypoint': 'monero-wallet-rpc --daemon-login ${APP_MONERO_RPC_USER}:${APP_MONERO_RPC_PASS} --rpc-bind-ip=0.0.0.0 --disable-rpc-login --confirm-external-bind --rpc-bind-port=18082 --non-interactive --trusted-daemon  --daemon-address=monerod:18081 --wallet-dir=/wallet --tx-notify="/bin/sh ./scripts/notifier.sh  -X GET http://btcpay-server_web_1:3003/monerolikedaemoncallback/tx?cryptoCode=xmr&hash=%s"',
        'ports': [
            '${APP_MONERO_WALLET_PORT}:${APP_MONERO_WALLET_PORT}'
        ],
        'volumes': [
            '${APP_MONERO_WALLET_DATA_DIR}:/wallet'
        ],
        'depends_on': [
            'monerod'
        ],
        'networks': {
            'default': {
                'ipv4_address': '$APP_MONERO_WALLET_IP'
            }
        }
    }
    changes = True
    # Add or remove Monero wallet service based on the action argument
    if action == 'add':
        if 'monerod_wallet' not in data['services']:
            data['services']['monerod_wallet'] = monero_wallet_service
            changes = True
    elif action == 'remove':
        if 'monerod_wallet' in data['services']:
            data['services'].pop('monerod_wallet', None)
            changes = True

    save_yaml(compose_file, data)
    # if changes then we want to return 1 else 0
    if changes:
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description='Add or remove the Monero wallet service in docker-compose.yml.')
    parser.add_argument('action', choices=['add', 'remove'], help='Action to perform: add or remove the Monero wallet service')
    parser.add_argument('compose_file', help='Path to the docker-compose.yml file')
    args = parser.parse_args()

    return update_monero_wallet_service(args.compose_file, args.action)

if __name__ == '__main__':
    sys.exit(main())