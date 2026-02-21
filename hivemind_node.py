"""
╔══════════════════════════════════════════════════════════════════╗
║         HiveMind Autonomous Node — Universal P2P Worker          ║
║         (Universal Local LLM + P2P Gossip Swarm Engine)          ║
╠══════════════════════════════════════════════════════════════════╣
║ Philosophy: Ping Alpha once for Identity/Wallet, then operate    ║
║ 100% autonomously on the P2P Mesh Network.                       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import os
import sys

try:
    import websockets
    import aiohttp
except ImportError:
    print("❌ Missing dependencies. Run: pip install -r requirements.txt")
    sys.exit(1)

# Central Ledger for Identity & Tokenomics
DEFAULT_ALPHA_SERVER = "ws://127.0.0.1:8000/alpha" 
CONFIG_FILE = "hivemind_wallet.json"

class UniversalLLM:
    """Auto-detects and connects to any local AI model running on the host machine."""
    def __init__(self):
        self.backends = [
            {"name": "LM Studio / vLLM", "url": "http://127.0.0.1:1234/v1/chat/completions", "type": "openai"},
            {"name": "Ollama", "url": "http://127.0.0.1:11434/api/generate", "type": "ollama"},
            {"name": "Llama.cpp", "url": "http://127.0.0.1:8080/v1/chat/completions", "type": "openai"}
        ]
        self.active_backend = None

    async def detect_backend(self):
        print("🔍 Scanning for local AI engines (Ollama, LM Studio, etc.)...")
        async with aiohttp.ClientSession() as session:
            for backend in self.backends:
                try:
                    url = backend["url"].replace("/v1/chat/completions", "/v1/models").replace("/api/generate", "/")
                    async with session.get(url, timeout=2) as resp:
                        if resp.status == 200:
                            self.active_backend = backend
                            print(f"✅ Success! Connected to local {backend['name']} engine.")
                            return True
                except:
                    continue
        print("❌ No local AI engine found. Please start Ollama or LM Studio.")
        return False

    async def generate(self, prompt: str) -> str:
        if not self.active_backend: return "Error: Engine offline."
        url, b_type = self.active_backend["url"], self.active_backend["type"]
        
        try:
            async with aiohttp.ClientSession() as session:
                if b_type == "openai":
                    payload = {"messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
                    async with session.post(url, json=payload) as resp:
                        return (await resp.json())["choices"][0]["message"]["content"]
                elif b_type == "ollama":
                    payload = {"model": "llama3.2", "prompt": prompt, "stream": False}
                    async with session.post(url, json=payload) as resp:
                        return (await resp.json()).get("response", "")
        except Exception as e:
            return f"// Task Execution Error: {str(e)}"

class HiveMindNode:
    def __init__(self):
        self.node_id = None
        self.role = None
        self.p2p_port = 0
        self.alpha_url = os.environ.get("HIVEMIND_SERVER", DEFAULT_ALPHA_SERVER)
        self.llm = UniversalLLM()

    async def start(self):
        print("🌟 Booting HiveMind Autonomous Swarm Node...\n")
        if not await self.llm.detect_backend(): return
        await self._init_identity()
        await self._start_p2p_mesh()

    async def _init_identity(self):
        """Pings the Alpha server ONLY on first boot to create a wallet and get a role."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.node_id, self.role = config.get("node_id"), config.get("role")
                print(f"🔓 Wallet loaded. ID: {self.node_id} | Assigned Role: [{self.role}]")
                return

        print("📡 Connecting to Central Alpha Ledger for Genesis Sync...")
        try:
            async with websockets.connect(self.alpha_url) as ws:
                self.node_id = (json.loads(await ws.recv())).get("node_id")
                
                await ws.send(json.dumps({"action": "REQUEST_ROLE_ASSIGNMENT"}))
                self.role = (json.loads(await ws.recv())).get("assigned_role", "general_compute")

                with open(CONFIG_FILE, "w") as f:
                    json.dump({"node_id": self.node_id, "role": self.role}, f)
                
                print(f"🎉 Genesis Sync Complete! Alpha connection severed.")
        except Exception as e:
            print(f"❌ Could not reach Alpha Ledger: {e}")
            sys.exit(1)

    async def _start_p2p_mesh(self):
        """Starts the local P2P server to listen for decentralized gossip tasks."""
        server = await asyncio.start_server(self._handle_p2p_connection, '0.0.0.0', 0)
        self.p2p_port = server.sockets[0].getsockname()[1]
        print(f"🌐 [P2P MESH] Node floating in decentralized mesh on port {self.p2p_port}")
        print(f"🎧 Listening for swarm gossip and micro-tasks...\n")
        await server.serve_forever()

    async def _handle_p2p_connection(self, reader, writer):
        try:
            data = await reader.readline()
            if not data: return
            msg = json.loads(data.decode())
            
            if msg.get("action") == "GOSSIP_TASK_BROADCAST":
                needed_role = msg.get("required_role")
                if needed_role in [self.role, "any", "general_compute"]:
                    print(f"⚡ [P2P] Received task matching role [{self.role}]. Engaging GPU...")
                    
                    result = await self.llm.generate(msg.get("prompt"))
                    
                    writer.write(json.dumps({
                        "action": "TASK_COMPLETED", 
                        "result": result, 
                        "worker_id": self.node_id
                    }).encode() + b'\n')
                    await writer.drain()
                    print("💰 Task Delivered directly to client! Awaiting IQ Token credit.")
        except Exception: pass
        finally:
            writer.close()

if __name__ == "__main__":
    asyncio.run(HiveMindNode().start())
  
