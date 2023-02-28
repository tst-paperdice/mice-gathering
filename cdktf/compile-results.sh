#!/usr/bin/env bash

set -ex

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

TF_STATE_FILE_PATH="${SCRIPT_DIR}/terraform.mice_gathering_infra.tfstate"

create_results_full_path_name() {
    RESULTS_ROOT_DIR="results"
    while : ; do
        timestamp=$(date '+%Y_%m_%d-%H.%M.%S')
        results_path_name="${RESULTS_ROOT_DIR}/${timestamp}"
        if [ ! -d "$results_path_name" ]; then
            break
        fi
    done
    CLIENT_HOST_SERVICE=$(jq -r .outputs.client_hosting_service.value ${TF_STATE_FILE_PATH})
    SERVER_HOST_SERVICE=$(jq -r .outputs.server_hosting_service.value ${TF_STATE_FILE_PATH})
    PROTOCOL=$(jq -r .outputs.protocol.value ${TF_STATE_FILE_PATH})
    REGION=$(jq -r .outputs.client_region.value ${TF_STATE_FILE_PATH})
    echo "${results_path_name}-${SERVER_HOST_SERVICE}-server-${CLIENT_HOST_SERVICE}_client_${REGION}_${PROTOCOL}"
}

RESULTS_DIR=$(create_results_full_path_name)

mkdir ${RESULTS_DIR}


CLIENT_IP=$(jq -r .outputs.client_public_ip.value ${TF_STATE_FILE_PATH})
SERVER_IP=$(jq -r .outputs.server_public_ip.value ${TF_STATE_FILE_PATH})

cp ${TF_STATE_FILE_PATH} ${RESULTS_DIR}
cdktf outputs --output ${RESULTS_DIR}

# TODO: kill docker containers and tcpdump on remote hosts

SSH_ARGS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
DOCKER_STOP_COMMAND="docker stop "'$(docker ps -a -q)'" || true"
CLIENT_USER_NAME="root"

CLIENT_HOST_SERVICE=$(jq -r .outputs.client_hosting_service.value ${TF_STATE_FILE_PATH})
if [ "$CLIENT_HOST_SERVICE" == "AWS" ]; then
    CLIENT_USER_NAME="ubuntu"
fi
# DIGITAL_OCEAN_KEY_OPTION=""
DIGITAL_OCEAN_KEY_OPTION="-i ~/.ssh/id_rsa_digital_ocean"
ssh ${SSH_ARGS} ${DIGITAL_OCEAN_KEY_OPTION} root@${SERVER_IP} ${DOCKER_STOP_COMMAND}
ssh ${SSH_ARGS} ${CLIENT_USER_NAME}@${CLIENT_IP} ${DOCKER_STOP_COMMAND}

KILL_TCPDUMP_COMMAND="sudo kill \$(ps aux | grep tcpdump | awk 'NR==1 {print \$2}')"
ssh ${SSH_ARGS} ${DIGITAL_OCEAN_KEY_OPTION} root@${SERVER_IP} ${KILL_TCPDUMP_COMMAND}
ssh ${SSH_ARGS} ${CLIENT_USER_NAME}@${CLIENT_IP} ${KILL_TCPDUMP_COMMAND}

### Copy PCAPs and logs

SCP_ARGS="${SSH_ARGS} -r"

# Copy client stuff
scp ${SCP_ARGS} -r ${CLIENT_USER_NAME}@${CLIENT_IP}:/etc/test_logs ${RESULTS_DIR}/client_test_logs
ssh ${SSH_ARGS} ${CLIENT_USER_NAME}@${CLIENT_IP} sudo sudo docker logs client &> ${RESULTS_DIR}/client_test_logs/docker-logs.txt

# Copy server stuff
# TODO: need a generic way to handle keys across hosting services. Can this be grabbed from a CDKTF file?
# TODO: the log location is configurable
# TODO: should this all just be part of some frontend written in Python?
scp ${SCP_ARGS} -r ${DIGITAL_OCEAN_KEY_OPTION} root@${SERVER_IP}:/etc/test_logs ${RESULTS_DIR}/server_test_logs
ssh ${SSH_ARGS} ${DIGITAL_OCEAN_KEY_OPTION} root@${SERVER_IP} sudo docker logs server &> ${RESULTS_DIR}/server_test_logs/docker-logs.txt




# TODO: zip up the directory (optional?)
tar cvzf ${RESULTS_DIR}.tar.gz ${RESULTS_DIR}

# TODO: shutdown the infra (should probably be done by the frontend, whatever that will be. Python?)
