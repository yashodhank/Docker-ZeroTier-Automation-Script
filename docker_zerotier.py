import os
import subprocess
import argparse
import json
import sys

# ANSI escape sequences for cool output
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
ENDC = "\033[0m"

DOCKER_CONTAINER_NAME = "zerotier"  # Update if your ZeroTier container has a different name
DEFAULT_ZT_PORT = 9993  # ZeroTier default port for binding

def print_step(step_name, step_desc):
    print(f"{BLUE}[{step_name}]{ENDC} {step_desc}")

def print_success(msg):
    print(f"{GREEN}[SUCCESS]{ENDC} {msg}")

def print_error(msg):
    print(f"{RED}[ERROR]{ENDC} {msg}")

def print_info(msg):
    print(f"{YELLOW}[INFO]{ENDC} {msg}")

def run_command(command, dry_run=False, capture_output=False):
    """Executes the given command and returns output."""
    if dry_run:
        print_info(f"Dry-run command: {command}")
        return ""
    else:
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return result.stdout.strip()
            else:
                subprocess.run(command, shell=True, check=True)
                print_success(f"Executed: {command}")
                return ""
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to execute: {command}. Error: {e}")
            return None  # Return None to allow further attempts

def check_zt_port_in_use():
    """Check if ZeroTier is listening on the default port (9993)."""
    print_info(f"Checking if port {DEFAULT_ZT_PORT} is in use...")
    output = run_command(f"sudo lsof -i :{DEFAULT_ZT_PORT}", capture_output=True)
    if output:
        print_success(f"Port {DEFAULT_ZT_PORT} is in use, indicating ZeroTier might be running.")
        return True
    else:
        print_error(f"Port {DEFAULT_ZT_PORT} is not in use.")
        return False

def check_zt_running_on_host():
    """Check if ZeroTier is running on the host system using systemctl."""
    print_info("Checking if ZeroTier is running on the host...")
    zt_host_status = run_command("systemctl is-active zerotier-one", capture_output=True)
    
    if zt_host_status == "active":
        print_success("ZeroTier is running on the host.")
        return True
    else:
        print_error("ZeroTier is not running on the host.")
        return False

def check_zt_cli_installed():
    """Check if zerotier-cli is installed and accessible on the host."""
    print_info("Checking if zerotier-cli is installed on the host...")
    cli_check = run_command("command -v zerotier-cli", capture_output=True)
    if cli_check:
        print_success("zerotier-cli is installed.")
        return True
    else:
        print_error("zerotier-cli is not installed or not in the system PATH.")
        return False

def check_zt_in_docker():
    """Check if ZeroTier is running inside a Docker container."""
    print_info("Checking if ZeroTier is running inside a Docker container...")
    zt_container_id = run_command(f"docker ps -q -f name={DOCKER_CONTAINER_NAME}", capture_output=True)
    
    if zt_container_id:
        print_success(f"ZeroTier is running inside the Docker container: {DOCKER_CONTAINER_NAME}")
        return True
    else:
        print_error("ZeroTier is not running inside the Docker container.")
        return False

def detect_zt_environment(zt_network_id):
    """Determine if ZeroTier is running on the host or inside Docker, based on the port usage and CLI availability."""
    
    # Step 1: Check if the ZeroTier port is in use
    if check_zt_port_in_use():
        
        # Step 2a: Check if ZeroTier is running on the host and if zerotier-cli is available
        if check_zt_running_on_host() and check_zt_cli_installed():
            return "host"
        
        # Step 2b: If not on the host, check for ZeroTier in Docker
        if check_zt_in_docker():
            return "docker"
        
        # If neither host nor Docker has ZeroTier properly set up
        print_error("ZeroTier is not fully configured on the host or Docker, even though the port is in use.")
        sys.exit(1)
    
    # If the ZeroTier port is not in use, nothing is running
    print_error("ZeroTier does not seem to be running on this system (host or Docker).")
    sys.exit(1)

def zt_exec(command, env, dry_run=False, capture_output=False):
    """Executes ZeroTier commands either on the host or in a Docker container based on the environment."""
    if env == "docker":
        full_command = f"docker exec {DOCKER_CONTAINER_NAME} zerotier-cli {command}"
    else:
        full_command = f"zerotier-cli {command}"

    return run_command(full_command, dry_run=dry_run, capture_output=capture_output)

def verify_zt_network_membership(zt_network_id, env):
    """Check if the current node is already part of the ZeroTier network."""
    print_info(f"Verifying if the node is already joined to the network {zt_network_id}...")

    zt_status_json = zt_exec("listnetworks -j", env, capture_output=True)
    
    if zt_status_json:
        zt_status = json.loads(zt_status_json)
        for network in zt_status:
            if zt_network_id == network['nwid'] and network['status'] == "OK":
                print_success(f"Node is already a member of the network {zt_network_id}.")
                return True
    print_info(f"Node is not a member of the network {zt_network_id}, joining now.")
    return False

def check_zt_network_id():
    """Ensure ZeroTier network ID is provided by user input."""
    zt_network_id = input(f"{YELLOW}[INPUT REQUIRED]{ENDC} Please enter the ZeroTier network ID to join: ")
    if not zt_network_id:
        print_error("ZeroTier network ID is required to proceed!")
        sys.exit(1)
    return zt_network_id

def enable_ip_forwarding(dry_run):
    """Enables IP forwarding on the host."""
    print_step("1", "Enabling IP forwarding...")
    run_command("sudo sysctl -w net.ipv4.ip_forward=1", dry_run)
    run_command("sudo bash -c 'echo net.ipv4.ip_forward=1 >> /etc/sysctl.conf'", dry_run)
    run_command("sudo sysctl -p", dry_run)

def join_zt_network(zt_network_id, env, dry_run):
    """Join the ZeroTier network if the node is not already a member."""
    if not verify_zt_network_membership(zt_network_id, env):
        print_step("3", f"Joining ZeroTier network {zt_network_id}...")
        join_cmd = f"join {zt_network_id}"
        zt_exec(join_cmd, env, dry_run)

def detect_docker_networks():
    """Detect Docker networks dynamically."""
    print_info("Detecting Docker networks...")
    docker_networks = run_command("docker network inspect $(docker network ls -q)", capture_output=True)
    
    # Parse Docker networks as JSON
    networks = json.loads(docker_networks)
    docker_network_ranges = []
    
    for net in networks:
        # Skip Docker default networks like 'host' and 'none'
        if net['Name'] in ['host', 'none']:
            print_info(f"Skipping Docker network '{net['Name']}' as it has no valid IPAM configuration.")
            continue
        
        # Safely check if 'IPAM' and 'Config' are present and not None
        ipam_config = net.get("IPAM", {}).get("Config", [])
        if ipam_config and isinstance(ipam_config, list) and len(ipam_config) > 0:
            subnet = ipam_config[0].get("Subnet")
            if subnet:
                docker_network_ranges.append(subnet)
                print_success(f"Detected Docker network: {subnet}")
        else:
            print_error(f"Network '{net.get('Name', 'Unnamed')}' has no valid IPAM configuration.")
    
    if not docker_network_ranges:
        print_error("No valid Docker networks found! Ensure Docker is running and containers are connected to networks.")
        sys.exit(1)

    return docker_network_ranges

def main():
    parser = argparse.ArgumentParser(description="Automate Docker-ZeroTier configuration.")
    parser.add_argument('--dry-run', action='store_true', help="Show commands without executing them")
    args = parser.parse_args()

    dry_run = args.dry_run

    print(f"{GREEN}==== Docker-ZeroTier Configuration Automation ===={ENDC}")

    # Step 1: Get ZeroTier network ID from user input
    zt_network_id = check_zt_network_id()

    # Step 2: Detect if ZeroTier is running on the host or in Docker
    env = detect_zt_environment(zt_network_id)

    # Step 3: Enable IP forwarding (only on the host)
    if env == "host":
        enable_ip_forwarding(dry_run)

    # Step 4: Join the ZeroTier network (if not already joined)
    join_zt_network(zt_network_id, env, dry_run)

    # Step 5: Detect Docker networks (if needed for routing)
    detect_docker_networks()

    print_success("All tasks completed successfully! Your Docker containers or host are now accessible over the ZeroTier network.")

if __name__ == '__main__':
    main()
