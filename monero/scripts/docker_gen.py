import sys
import yaml
import argparse

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

def main(action, service_type, compose_file):
    data = load_yaml(compose_file)
    changes = False

    if service_type == 'btcpay':
        if 'web' in data['services']:
            service = data['services']['web']
            if action == 'add':
                changes = add_variables(service, btcpay_environment_variables, btcpay_volume_to_add)
            elif action == 'remove':
                changes = remove_variables(service, btcpay_environment_variables, btcpay_volume_to_add)
        else:
            print("BTCPayserver service not found in docker-compose.yml")
            return
    elif service_type == 'monero':
        changes = update_monero_wallet_service(data, action)
    else:
        print("Invalid service type. Use 'btcpay' or 'monero'.")
        return

    if changes:
        save_yaml(compose_file, data)
        print("docker-compose.yml updated successfully")
        return 1
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add or remove services in docker-compose.yml.')
    parser.add_argument('action', choices=['add', 'remove'], help='Action to perform: add or remove the service')
    parser.add_argument('service_type', choices=['btcpay', 'monero'], help='Service type to update: btcpay or monero')
    parser.add_argument('compose_file', help='Path to the docker-compose.yml file')
    args = parser.parse_args()

    result = main(args.action, args.service_type, args.compose_file)
    sys.exit(result)