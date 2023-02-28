#!/usr/bin/env python


def generate_docker_run_command(
    host_type: str,
    protocol: str,
    *,
    shadowsocks_password: str,
    shadowsocks_port: int,
    num_sites_to_visit: int = None,
    server_ip_address: str = None,
    output_log_dir: str = None,
    endpoints_script_file_path: str = None
) -> str:

    if not output_log_dir:
        output_log_dir = "/etc/test_logs/"

    # num_runs = 1
    # num_runs = 2
    num_runs = 10

    # publish_arg = ""
    # for index in range(num_runs):
    #     port = shadowsocks_port + index
    #     print(f"port = {port}")
    #     publish_arg += f"--publish {port}:{port} "
    # print(publish_arg)
    publish_arg = f"--publish {shadowsocks_port}:{shadowsocks_port}"
    

    endpoints_play_time = 15.0

    if host_type == "server":
        docker_image: str = "jaxbysaloosh/webapp"
        if protocol == "shadowsocks":
            script_name = "start-ss.sh"
            docker_run_command = f"docker run \
                -d \
                --name=server \
                --env SS_SERVER_PORT={shadowsocks_port} \
                --env SS_PASSWORD={shadowsocks_password} \
                --volume {output_log_dir}:/root/mount \
                --network=bridge \
                --publish {shadowsocks_port}:{shadowsocks_port} \
                {docker_image} \
                {script_name}"
        elif protocol == "obfs":
            script_name = "start-pt.sh"
            docker_run_command = f"docker run \
                -d \
                --name=server \
                --env SS_SERVER_PORT={shadowsocks_port} \
                --env SS_PASSWORD={shadowsocks_password} \
                --volume {output_log_dir}:/root/mount \
                --network=bridge \
                --publish {shadowsocks_port}:{shadowsocks_port} \
                {docker_image} \
                {script_name}"
        elif protocol == "endpoints":
            docker_run_command = f"docker run \
                            -d \
                            --name=server \
                            --cap-add=NET_ADMIN \
                            --cap-add=NET_RAW \
                            {publish_arg} \
                            --env PAYLOAD_PATH={endpoints_script_file_path} \
                            --env CLIENT_HOST=1.1.1.1 \
                            --env CLIENT_PORT=12345 \
                            --env SERVER_HOST=1.1.1.1 \
                            --env SERVER_PORT={shadowsocks_port} \
                            --env PLAY_TIME={endpoints_play_time} \
                            --env CAPTURE_PATH=/logging/full_capture.pcap \
                            --env EVENT_PATH=/logging/events.txt \
                            --env LOG_DIR=/logging/ \
                            --env NUM_RUNS={num_runs} \
                            --volume {output_log_dir}:/logging/ \
                            jaxbysaloosh/endpoint-webapp"
        else:
            raise Exception(f"invalid protocol: {protocol}")

    elif host_type == "client":
        websites_csv_file = "100_filtered.csv"
        docker_home_dir = "/home/browser"
        docker_image = "jaxbysaloosh/tester"
        experiment_log_suffix = "test"
        if protocol == "shadowsocks":
            protocol_flag = "--shadowsocks=libev"
            docker_run_command = f"sudo docker run \
                -d \
                --volume {output_log_dir}:{docker_home_dir}/mount \
                {docker_image} \
                {protocol_flag} \
                --server-host={server_ip_address} \
                --server-port={shadowsocks_port} \
                --ss-pass={shadowsocks_password} \
                --ss-method=aes-256-gcm \
                --socks-local-port=9050 \
                --ss-fast-open=true \
                --name=client \
                {docker_home_dir}/scripts/{websites_csv_file} {num_sites_to_visit} {docker_home_dir}/mount {experiment_log_suffix}"
        elif protocol == "obfs":
            protocol_flag = "--pt"
            docker_run_command = f"sudo docker run \
                -d \
                --volume {output_log_dir}:{docker_home_dir}/mount \
                {docker_image} \
                {protocol_flag} \
                --server-host={server_ip_address} \
                --server-port={shadowsocks_port} \
                --ss-pass={shadowsocks_password} \
                --ss-method=aes-256-gcm \
                --socks-local-port=9050 \
                --ss-fast-open=true \
                --name=client \
                {docker_home_dir}/scripts/{websites_csv_file} {num_sites_to_visit} {docker_home_dir}/mount {experiment_log_suffix}"
        elif protocol == "endpoints":
            docker_run_command = f"sudo docker run \
                -d \
                -p 12345:12345 \
                --env PAYLOAD_PATH={endpoints_script_file_path} \
                --env CLIENT_HOST=1.1.1.1 \
                --env CLIENT_PORT=12345 \
                --env SERVER_HOST={server_ip_address} \
                --env SERVER_PORT={shadowsocks_port} \
                --env PLAY_TIME={endpoints_play_time} \
                --env CAPTURE_PATH=/logging/full_capture.pcap \
                --env EVENT_PATH=/logging/events.txt \
                --env LOG_DIR=/logging/ \
                --env NUM_RUNS={num_runs} \
                --name=client \
                --volume {output_log_dir}:/logging/ \
                jaxbysaloosh/endpoint-tester"
        else:
            raise Exception(f"invalid protocol: {protocol}")
    else:
        raise Exception(f"invalid host type: {host_type}")

    return docker_run_command
