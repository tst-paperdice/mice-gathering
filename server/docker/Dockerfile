# FROM mice-server-shadowsocks:latest
# FROM ubuntu:latest
FROM debian:stable-slim

RUN apt-get update && \
    apt-get install -y tcpdump \
            shadowsocks-libev

# ENV SS_SERVER_PORT 9999
# ENV SS_PASSWORD 1234

WORKDIR /root

# Install dependencies to add Tor's repository.
RUN apt-get update && apt-get install -y \
                              curl \
                              gpg \
                              gpg-agent \
                              ca-certificates \
                              libcap2-bin \
                              --no-install-recommends

# See: <https://2019.www.torproject.org/docs/debian.html.en>
# RUN curl https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --import
# RUN gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | apt-key add -

# RUN printf "deb https://deb.torproject.org/torproject.org bullseye main\n" >> /etc/apt/sources.list.d/tor.list

# Install remaining dependencies.
RUN apt-get update && apt-get install -y \
                              tor \
                              tor-geoipdb \
                              obfs4proxy \
                              python3-pip \
                              git \
                              wget \
                              net-tools \
                              netcat \
                              procps

RUN pip3 install aiosocks

# RUN git clone https://github.com/gumblex/ptproxy.git

# RUN sed -i "s/async(/ensure_future(/g" ptproxy/ptproxy.py

# RUN wget https://go.dev/dl/go1.18.4.linux-amd64.tar.gz && \
#     tar -C /usr/local/ -xzf go1.18.4.linux-amd64.tar.gz

# ENV PATH="/usr/local/go/bin:$PATH"
# ENV GOPATH="/usr/local/go/"

# WORKDIR /root
# RUN git clone https://github.com/OperatorFoundation/shapeshifter-dispatcher.git && \
#     cd shapeshifter-dispatcher && \
#     go get && \
#     go install


# RUN printf "deb http://deb.debian.org/debian bullseye-backports main\n" >> /etc/apt/sources.list.d/backports.list
# RUN apt-get update && apt-get install -y \
#                               obfs4proxy \
#                               golang-1.18 \
#                               -t bullseye-backports


# # Install dependencies to add Tor's repository.
# RUN apt-get update && apt-get install -y \
#     curl \
#         gpg \
#             gpg-agent \
#                 ca-certificates \
#                     libcap2-bin \
#                         --no-install-recommends

# # See: <https://2019.www.torproject.org/docs/debian.html.en>
# RUN curl https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --import
# RUN gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | apt-key add -

# # Install remaining dependencies.
# RUN apt-get update && apt-get install -y \
#                               tor \
#                               tor-geoipdb

# RUN apt-get update -o Dir::Etc::sourceparts="-"  && apt-get install -y \
#     obfs4proxy \
#         --no-install-recommends -t bionic-backports

# # Allow obfs4proxy to bind to ports < 1024.
# RUN setcap cap_net_bind_service=+ep /usr/bin/obfs4proxy

# Our torrc is generated at run-time by the script start-tor.sh.

# RUN rm /etc/tor/torrc

# RUN chown root /var/lib/tor

# RUN mkdir /var/lib/tor/keys/
# COPY content/bridge-keys /var/lib/tor/keys/
# RUN chown -R root /var/lib/tor/keys/

# COPY content/pt_state /var/lib/tor/pt_state
# RUN chown -R root /var/lib/tor/pt_state/

COPY ptproxy/ ./ptproxy
COPY scripts/ ./scripts
RUN mkdir /mount
WORKDIR /root/scripts

ENV PATH="/root/scripts:${PATH}"
# run with
# -e SS_SERVER_PORT=<VALUE> -e SS_PASSWORD=<value>
CMD bash
# ENTRYPOINT bash
# CMD /root/scripts/run_ss.sh

# CMD [ "/root/scripts/start-tor.sh" ]
