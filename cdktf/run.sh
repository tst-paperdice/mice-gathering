#!/usr/bin/env bash

# Basic script to kick off multiple runs.
# WARNING: this is _very_ basic and does not cover many error/corner cases.

set -x

TF_STATE_FILE_PATH="terraform.mice_gathering_infra.tfstate"

for filename in $HOME/projects/mice/dev/mice-endpoints/docker/endpoint/scripts2-rnd2/*; do

  file_base_name="$(basename $filename)"
  export TF_VAR_endpoints_script_file_path="scripts2-rnd2/$file_base_name"

  cdktf destroy --auto-approve

  if ! cdktf deploy --auto-approve; then
    echo "deploy failed. trying again..."
    continue
  fi

  CLIENT_IP=$(jq -r .outputs.client_public_ip.value ${TF_STATE_FILE_PATH})

  while true; do
    LOG_OUTPUT=$(ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${CLIENT_IP} cat /etc/test_logs/client_log.log)
    if echo $LOG_OUTPUT | grep "SESSION FINISHED"; then
      echo "run completed. compiling results..."
      ./compile-results.sh 
      break
    fi

    DOCKER_LOG_OUTPUT=$(ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${CLIENT_IP} docker logs client 2>&1)
    if echo $DOCKER_LOG_OUTPUT | grep "Traceback"; then
      break
    fi

    echo "waiting for run to complete..."
    sleep 10
  done

done

cdktf destroy --auto-approve
