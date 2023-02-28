#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

cd "$(dirname "$0")"

docker_build_args=("--pull" "--progress=plain" "--platform=linux/amd64")

# If Docker experimental features are enabled, then squash the output image.
if [[ "$(docker version -f '{{.Server.Experimental}}')" == "true" ]]; then
    docker_build_args+=("--squash")
else
    echo "WARNING: Docker experimental features are not enabled. Image will not be squashed"
fi

docker build "${docker_build_args[@]}" client/docker/ -t mice-gathering-client

docker build "${docker_build_args[@]}" server/docker/ -t mice-gathering-server


docker tag mice-gathering-client jaxbysaloosh/tester
docker tag mice-gathering-server jaxbysaloosh/webapp
docker push jaxbysaloosh/tester
docker push jaxbysaloosh/webapp