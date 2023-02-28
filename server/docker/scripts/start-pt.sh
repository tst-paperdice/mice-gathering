#!/usr/bin/env bash

echo "running $0"

echo "{ \
    \"role\": \"server\", \
    \"state\": \".\", \
    \"local\": \"socks5\", \
    \"server\": \"0.0.0.0:${SS_SERVER_PORT}\",\
    \"ptexec\": \"obfs4proxy -logLevel=DEBUG -enableLogging=true\", \
    \"ptname\": \"obfs4\", \
    \"ptserveropt\": \"\", \
    \"ptproxy\": \"\" \
}" > /etc/ptserver.json

cat /etc/ptserver.json

# tcpdump -i eth0 -w /mount/$(date +"%Y-%M-%d-%H:%M:%S").pcap &

python3 /root/ptproxy/ptproxy.py /etc/ptserver.json

