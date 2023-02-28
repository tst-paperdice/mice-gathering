#!/usr/bin/env bash

echo "running $0"

echo "{ \
    \"server\":\"0.0.0.0\", \
    \"server_port\":${SS_SERVER_PORT}, \
    \"password\":\"${SS_PASSWORD}\", \
    \"method\":\"aes-256-gcm\", \
    \"fast_open\":true, \
    \"nameserver\":\"8.8.8.8\", \
    \"mode\":\"tcp_and_udp\"
}" > /etc/shadowsocks-libev/config.json

cat /etc/shadowsocks-libev/config.json

# tcpdump -i eth0 -w /mount/$(date +"%Y-%M-%d-%H:%M:%S").pcap &

ss-server -c /etc/shadowsocks-libev/config.json 

# echo "{ \
#     \"server\":\"0.0.0.0\", \
#     \"server_port\":${SS_SERVER_PORT}, \
#     \"local_port\":1080, \
#     \"password\":\"${SS_PASSWORD}\", \
#     \"method\":\"aes-256-cfb\", \
#     \"timeout\":120 \
# }" > /etc/shadowsocks-go/config.json

# cat /etc/shadowsocks-go/config.json

# shadowsocks-server -c /etc/shadowsocks-go/config.json
