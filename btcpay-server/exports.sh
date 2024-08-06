
# If monero docker image is running on the same host as btcpay server, we can use the btcpay altcoin image
# Check monero-config.json file to see if monero support is enabled
if [ ! -z "${APP_MONERO_DATA_DIR}" ]; then
    # grab the username and password from the .env file for the monero daemon - may not be necessary
#    MONERO_ENV_FILE="${APP_MONERO_DATA_DIR}/.env"
#    source $MONERO_ENV_FILE
    #Now we need to update the docker-compose file to use the btcpay altcoin image and 
    export BTCPAY_IMAGE="btcpayserver/btcpayserver:1.13.1-altcoins"
    export APP_BTCPAY_CHAINS="btc,xmr"

else
    # Check if we need to update the image to use the original btcpay image
    export BTCPAY_IMAGE="btcpayserver/btcpayserver:1.13.1@sha256:ee432e652e129d82a76e4de8ff28e90eb5476d01fcb008e3678991c52f5084e9"
    export APP_BTCPAY_CHAINS="btc"
fi