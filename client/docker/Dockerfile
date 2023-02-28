FROM debian:stable-slim
# FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -yy \
        python3 \
        python3-pip \
        shadowsocks-libev \
        wget \
        unzip \
        xvfb \
        tcpdump

RUN pip3 install \
        selenium==4.4.3 \
        webdriver-manager \
        argparse \
        stem \
        pyvirtualdisplay \
        packaging

# Install chrome and chromedriver.
# Some useful notes on the chromedriver: https://sites.google.com/a/chromium.org/chromedriver/downloads/version-selection
WORKDIR /tmp/
RUN CHROME_VERSION="104.0.5112" && \
    wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}.101-1_amd64.deb && \
    wget https://chromedriver.storage.googleapis.com/${CHROME_VERSION}.79/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver && \
    dpkg -i google-chrome-stable_${CHROME_VERSION}.101-1_amd64.deb; \
    apt-get --fix-broken install -y && \
    dpkg -i google-chrome-stable_${CHROME_VERSION}.101-1_amd64.deb && \
    rm -rf *

RUN apt-get update && \
    apt-get install -yy \
        tor \
        obfs4proxy \
        python3-pip \
        git \
        net-tools \
        curl \
        procps \
        netcat

# Install the ooni probe CLI, a tool for measuring internet censorship: https://ooni.org/install/
RUN apt-key adv --verbose --keyserver hkp://keyserver.ubuntu.com --recv-keys 'B5A08F01796E7F521861B449372D1FF271F2DD50' && \
    echo "deb http://deb.ooni.org/ unstable main" | tee /etc/apt/sources.list.d/ooniprobe.list && \
    apt-get update && \
    apt-get install ooniprobe-cli -yy

RUN pip3 install aiosocks

# RUN wget https://go.dev/dl/go1.18.4.linux-amd64.tar.gz && \
#     tar -C /usr/local/ -xzf go1.18.4.linux-amd64.tar.gz

# ENV PATH="/usr/local/go/bin:$PATH"
# ENV GOPATH="/usr/local/go/"

RUN useradd browser
WORKDIR /home/browser
RUN chown -R browser:browser /home/browser
USER browser
# RUN git clone https://github.com/OperatorFoundation/shapeshifter-dispatcher.git && \
#     cd shapeshifter-dispatcher && \
#     go get && \
#     go install


COPY ptproxy/ ./ptproxy
COPY scripts ./scripts
COPY content/* ./scripts/

USER root
# USER browser

# Various cleanup to try to slim down the image size.
RUN rm -rf /var/cache/* && \
    rm -rf /tmp/* && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python3", "/home/browser/scripts/run_ss.py"]
# ENTRYPOINT bash
