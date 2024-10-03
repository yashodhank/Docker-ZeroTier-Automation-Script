# Docker-ZeroTier Automation Script

This script automates the configuration of Docker and ZeroTier networks to ensure that all Docker containers running on a host are accessible to other nodes on the ZeroTier network **without needing to run the ZeroTier client inside each container**. By managing ZeroTier at the host or Docker level, the script removes the complexity of configuring ZeroTier for each container while ensuring seamless communication across networks.

## Table of Contents

- [Introduction](#introduction)
- [What Problem Does This Script Solve?](#what-problem-does-this-script-solve)
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Scenarios and Examples](#scenarios-and-examples)
  - [Scenario 1: ZeroTier on Host](#scenario-1-zerotier-on-host)
  - [Scenario 2: ZeroTier Inside Docker](#scenario-2-zerotier-inside-docker)
  - [Scenario 3: ZeroTier Already Configured](#scenario-3-zerotier-already-configured)
- [Dry Run Mode](#dry-run-mode)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

The **Docker-ZeroTier Automation Script** is a powerful automation tool that simplifies network management for Docker containers and ZeroTier virtual networks. It handles the complex task of integrating Docker networks with ZeroTier without requiring the ZeroTier client to be installed and configured inside each individual container.

This script is ideal for scenarios where you need Docker containers running on a host to be accessible to other nodes on the ZeroTier network without running ZeroTier on each container. The host (or a dedicated ZeroTier container) is responsible for handling the ZeroTier connection, and all containers are routed through the ZeroTier network, making them accessible to other ZeroTier members.

## What Problem Does This Script Solve?

When managing multiple Docker containers, it's common to need them accessible to external networks, such as a ZeroTier virtual private network. However, running the ZeroTier client in each Docker container introduces unnecessary overhead and complexity. Additionally, it can be challenging to maintain configurations and ensure proper network communication between containers and other ZeroTier nodes.

This script **solves that problem** by managing ZeroTier at the host or container level, making **all Docker containers on the host accessible over the ZeroTier network without needing to install or configure ZeroTier on each container**.

### Benefits:
- **Simplified Management**: You only need to manage ZeroTier on the host or in a single container, which dramatically reduces configuration complexity.
- **Efficient Access**: All Docker containers on the host can communicate with others on the ZeroTier network without running additional clients inside each container.
- **Automated Setup**: The script automatically configures the environment to ensure that ZeroTier and Docker networks are integrated seamlessly.

## Features

- **ZeroTier Network Automation**: Automatically joins the ZeroTier network from either the host or a Docker container.
- **Single Client Setup**: You don't need to run the ZeroTier client inside every Docker container. The host handles the connection, and Docker networks are routed through it.
- **Idempotent and Safe for Multiple Runs**: The script checks the current configuration and only applies necessary changes. You can run it multiple times without worrying about redundant tasks.
- **Network Membership Validation**: Ensures that the host or container is part of the ZeroTier network and automatically joins if not already a member.
- **Flexible Execution with Dry Run Mode**: You can simulate changes using the `--dry-run` option to preview the commands without making any real changes.

## How It Works

The script automates several tasks to ensure that Docker containers are properly connected to the ZeroTier network:

1. **ZeroTier Port Check**: It checks if the ZeroTier client is running by detecting if the port `9993` is in use.
2. **Host or Docker Environment Detection**: Based on the port check, it determines whether ZeroTier is running on the host or inside a Docker container.
3. **ZeroTier Network Membership**: It checks if the host or container is already part of the specified ZeroTier network. If not, it joins the network automatically.
4. **Docker Network Configuration**: The script inspects all Docker networks and ensures they are routed correctly through the ZeroTier network for external accessibility.
5. **IP Forwarding (if needed)**: On the host, it enables IP forwarding to ensure proper routing between Docker networks and the ZeroTier network.

## Installation

To install and run this script, first clone this repository:

```bash
git clone https://github.com/yashodhank/Docker-ZeroTier-Automation-Script.git
cd Docker-ZeroTier-Automation-Script
```

## Usage

To run the script, simply execute the following command:

```bash
python3 docker_zerotier.py
```

You'll be prompted to enter your ZeroTier network ID, and the script will handle the rest.

### Command-line Arguments

- `--dry-run`: Runs the script in simulation mode, showing the commands that would be executed without making any changes.

Example:

```bash
python3 docker_zerotier.py --dry-run
```

This is useful for testing and ensuring the script will behave as expected before applying any changes.

## Scenarios and Examples

### Scenario 1: ZeroTier on Host

In this scenario, ZeroTier is installed on the host system. The script will:

1. Detect if the ZeroTier port is active.
2. Check if ZeroTier is running on the host using `systemctl`.
3. Ensure that `zerotier-cli` is installed.
4. Verify if the host is part of the specified ZeroTier network and join if necessary.
5. Inspect Docker networks and configure them to be accessible through the ZeroTier network.

### Scenario 2: ZeroTier Inside Docker

In this case, ZeroTier is running inside a Docker container. The script will:

1. Detect if the ZeroTier port is active.
2. Check if ZeroTier is running inside the Docker container.
3. Ensure the container is part of the ZeroTier network.
4. Detect Docker networks and configure them for seamless integration with the ZeroTier network.

Example output:

```
==== Docker-ZeroTier Configuration Automation ====
[INPUT REQUIRED] Please enter the ZeroTier network ID to join: ded3d5c970f96822
[INFO] Checking if port 9993 is in use...
[SUCCESS] Port 9993 is in use, indicating ZeroTier might be running.
[INFO] Checking if ZeroTier is running on the host...
[ERROR] ZeroTier is not running on the host.
[INFO] Checking if ZeroTier is running inside a Docker container...
[SUCCESS] ZeroTier is running inside the Docker container: zerotier
[INFO] Verifying if the node is already joined to the network ded3d5c970f96822...
[SUCCESS] Node is already a member of the network ded3d5c970f96822.
[INFO] Detecting Docker networks...
[SUCCESS] Detected Docker network: 172.31.255.0/29
...
```

### Scenario 3: ZeroTier Already Configured

In this scenario, the host or Docker container is already correctly configured for the ZeroTier network. The script will:

1. Check if the node is part of the specified ZeroTier network.
2. Skip redundant steps and confirm that the environment is already configured correctly.

## Dry Run Mode

The `--dry-run` flag allows you to simulate the script's behavior without making any changes. This is particularly useful when you want to verify the commands that will be executed.

```bash
python3 docker_zerotier.py --dry-run
```

Example output:

```
==== Docker-ZeroTier Configuration Automation ====
[INPUT REQUIRED] Please enter the ZeroTier network ID to join: ded3d5c970f96822
[INFO] Checking if port 9993 is in use...
[INFO] Dry-run command: sudo lsof -i :9993
[SUCCESS] Port 9993 is in use, indicating ZeroTier might be running.
...
```

## FAQ

### 1. What does this script do?
This script automates the configuration of ZeroTier and Docker networks, making sure Docker containers can communicate with other ZeroTier network members without needing to run the ZeroTier client inside each container.

### 2. Can I run this script multiple times?
Yes, the script is designed to be idempotent. It checks the current configuration and only applies necessary changes, so you can safely run it multiple times.

### 3. Do I need ZeroTier on every Docker container?
No! The script ensures that Docker containers are accessible over ZeroTier without needing to run the ZeroTier client inside each container. The host or a single container handles the ZeroTier connection.

### 4. How does the script handle network memberships?
The script checks if the host or Docker container is already a member of the specified ZeroTier network. If it is, it skips the join operation; otherwise, it joins the network automatically.

### 5. What does `--dry-run` do?
The `--dry-run` option allows you to see what the script will do without making any actual changes. It's a great way to test the script before applying changes.

## Contributing



Contributions are welcome! Feel free to fork this repository, create a new branch, and submit a pull request.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This script is designed to save you time and effort when configuring ZeroTier and Docker networks. Whether you're running a small-scale home lab or managing a large cloud infrastructure, this tool helps ensure that your containers are always connected and accessible over your ZeroTier network without unnecessary complexity.

Feel free to reach out with any questions or suggestions!
