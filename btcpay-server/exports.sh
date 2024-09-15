if [ "${MONERO_BTCPAY_ENABLED}" = "true" ]; then
    export BTCPAY_IMAGE="btcpayserver/btcpayserver:1.13.1-altcoins"
    export APP_BTCPAY_CHAINS="btc,xmr"
else
    export BTCPAY_IMAGE="btcpayserver/btcpayserver:1.13.1@sha256:ee432e652e129d82a76e4de8ff28e90eb5476d01fcb008e3678991c52f5084e9"
    export APP_BTCPAY_CHAINS="btc"
fi
