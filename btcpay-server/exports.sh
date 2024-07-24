
# If monero docker image is running on the same host as btcpay server, we can use the btcpay altcoin image
# Check if Monero Docker container is running
MONERO_CONTAINER_NAME="monero_monerod_1" # Adjust this to your Monero container name
MONERO_CONTAINER_RUNNING=$(docker ps --filter "name=$MONERO_CONTAINER_NAME" --format "{{.Names}}")
# Also check if monero docker container exists
MONERO_CONTAINER_EXISTS=$(docker ps -a --filter "name=$MONERO_CONTAINER_NAME" --format "{{.Names}}")
if [ ! -z "$MONERO_CONTAINER_RUNNING" ]; then
    # grab the username and password from the .env file for the monero daemon - may not be necessary
    MONERO_ENV_FILE="${APP_MONERO_DATA_DIR}/.env"
    source $MONERO_ENV_FILE
    #Now we need to update the docker-compose file to use the btcpay altcoin image and 
    export BTCPAY_IMAGE="btcpayserver/btcpayserver:1.13.1-altcoins"
    export APP_BTCPAY_CHAINS="btc,xmr"
    #Set the following variables within the btcpayserver container
    BTCPAY_XMR_DAEMON_URI = "http://${APP_MONERO_NODE_IP}:${APP_MONERO_RPC_PORT}"
    BTCPAY_XMR_DAEMON_USERNAME = "${APP_MONERO_RPC_USER}"
    BTCPAY_XMR_DAEMON_PASSWORD = "${APP_MONERO_RPC_PASS}"
    BTCPAY_XMR_WALLET_DAEMON_URI = "http://${APP_MONERO_WALLET_IP}:${APP_MONERO_WALLET_PORT}"
    BTCPAY_XMR_WALLET_DAEMON_WALLETDIR =${APP_MONERO_WALLET_DATA_DIR}

    # Add access to the monero wallet
    #  volumes:
    #   - "xmr_wallet:/root/xmr_wallet"

else
    # Check if we need to update the image to use the original btcpay image
    export BTCPAY_IMAGE="btcpayserver/btcpayserver:1.13.1@sha256:ee432e652e129d82a76e4de8ff28e90eb5476d01fcb008e3678991c52f5084e9"
    export APP_BTCPAY_CHAINS="btc"
fi