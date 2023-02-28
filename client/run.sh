#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

# example use:
# ../run.sh <ss|tor> <mount path> <# sites to visit> <log prefix> <tor-bridge-file> <proxy IP> <ss-ip> <ss-password>
# ../run.sh ss /home/paul.vines/mice/test/ 5 test1 dummy 172.17.0.2 9090 abcd
# ../run.sh tor /home/paul.vines/mice/test/ 5 test1 bridges.json dummy dummy dummy

MODE=$1
MOUNT=$2
NUM_SITES=$3 # number of test sites to visit. TODO: terraform input, with default
SUFFIX=$4 # log file suffix to differentiate experiments. TODO: terraform input, with default

if [ $MODE = "ss" ]; then
    MODE_ARG="shadowsocks=libev"
fi
if [ $MODE = "tor" ]; then
    MODE_ARG="tor"
fi
if [ $MODE = "pt" ]; then
    MODE_ARG="pt"
fi


PREFIX=$4
TOR_BRIDGES_FILE=$5 # unused for now, set as aribtrary string
SS_HOST=$6  # Server IP.
SS_PORT=$7
SS_PASS=$8

echo experiment prefix: $PREFIX
echo mount $MOUNT:/home/browser/mount

# echo chmod -R 777 $MOUNT
# sudo chmod -R 777 $MOUNT

HOME_DIR="/home/browser"

set -x

docker run \
       -it \
       --rm \
       --name=mice-client \
       --user=browser \
       --volume $MOUNT:${HOME_DIR}/mount \
       mice-gathering-client \
       --$MODE_ARG \
       --server-host=$SS_HOST \
       --server-port=$SS_PORT \
       --ss-pass=$SS_PASS \
       --ss-method=aes-256-gcm \
       --socks-local-port=9050 \
       --ss-fast-open=true \
       --tor-bridges-file=$TOR_BRIDGES_FILE \
       "${HOME_DIR}/scripts/100_filtered.csv" $NUM_SITES ${HOME_DIR}/mount $PREFIX
