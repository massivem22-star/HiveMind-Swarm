# 🐝 HiveMind-Swarm: The Decentralized AI Network

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Phase: Testnet](https://img.shields.io/badge/Phase-Testnet_Live-success.svg)]()

> **Stop renting AI compute. Start owning the network.**

The decentralized P2P AI swarm agents. Leverage the swarm's intelligence and earn IQ Tokens.

HiveMind is a peer-to-peer (P2P) decentralized intelligence network. It connects thousands of consumer GPUs running local open-source LLMs (like Llama 3, Mistral, Qwen) into a massive, unified, and specialized AI swarm. 

This repository contains the **Autonomous Worker Node**. By running this node, you contribute your idle GPU power to the swarm, process micro-tasks via P2P gossip, and earn **IQ Tokens** (Currently in Free Testnet Phase).

## 🧠 How It Works (True Web3 Architecture)

Unlike centralized APIs, HiveMind does not route prompts or code through a central server.
1. **Genesis Sync:** On first run, your node pings the Alpha Server (The Ledger) to create a wallet and receive a specialized role (e.g., `python_coder`, `security_auditor`) based on network demand.
2. **Severing the Cord:** The node immediately disconnects from the central server.
3. **P2P Gossip:** Your node listens directly on the decentralized mesh network. When a user requests a massive project, it is decomposed into hundreds of micro-tasks. 
4. **Execution & Earning:** If a micro-task matches your assigned role, your local LLM executes it, sends the result directly to the user (P2P), and your wallet is credited with IQ Tokens.

## 🚀 Getting Started

### Prerequisites
You must have a local LLM runner installed and running. HiveMind automatically detects:
* **[Ollama](https://ollama.com/)** (Default port 11434)
* **[LM Studio](https://lmstudio.ai/)** (Default port 1234)
* **Llama.cpp / vLLM** (Default port 8080)

### Run the Node
```bash
pip install websockets aiohttp
python hivemind_node.py
