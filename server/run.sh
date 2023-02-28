#!/bin/bash

# example use:
# ../run.sh <ss|tor> <mount path> <PT_PORT|SS_PORT> <OR_PORT|SS_PASSWORD>
# ../run.sh 9090 abcd /home/paul.vines/mice/test/

MODE=$1
MOUNT=$2

echo Running start-${MODE}.sh
echo mount $MOUNT:/mount

if [ $MODE = "tor" ]; then
    echo PT_PORT = $3
    echo OR_PORT = $4
fi

if [ $MODE = "ss" ]; then
    echo SS_SERVER_PORT = $3
    echo SS_PASSWORD = $4
fi


if [ $MODE = "pt" ]; then
    echo SERVER_PORT = $3
fi

set -x

docker run -it \
    --rm \
    --name=mice-server \
    --env SS_SERVER_PORT=$3 \
    --env PT_PORT=$3 \
    --volume $MOUNT:/mount \
    --network=bridge -p $3:$3 mice-gathering-server start-${MODE}.sh
