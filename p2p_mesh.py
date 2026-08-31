#!/usr/bin/env python3
"""
Distributed AI Inference Engine (P2P Model Pooling)
---------------------------------------------------
A decentralized P2P mesh network that pools CPU/RAM resources to perform
distributed LLM inference.
Features:
  1. Model Manifest & Layer Descriptors
  2. Distributed Inference Router (AIPoolOrchestrator)
  3. Local Worker Wrapper for Tensor/Token processing
  4. Dynamic Failover & Context Resync

Author: AI Coding Agent (Senior Network Software Engineer Persona)
"""

import asyncio
import socket
import hashlib
import json
import uuid
import argparse
import time
import logging
import math
import multiprocessing
from typing import Dict, List, Optional, Any, Set

try:
    import psutil
except ImportError:
    print("ERROR: psutil library is required for resource load balancing.")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("P2P-AI-Inference")

# ==========================================
# 1. MODEL MANIFEST & DESCRIPTORS
# ==========================================
class ModelManifest:
    """Registers quantized models and descriptors for pipeline splitting."""
    def __init__(self, name: str, architecture: str, total_layers: int, context_window: int, required_ram_mb: int):
        self.name = name
        self.architecture = architecture
        self.total_layers = total_layers
        self.context_window = context_window
        self.required_ram_mb = required_ram_mb
        self.id = hashlib.md5(name.encode()).hexdigest()

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "architecture": self.architecture,
            "total_layers": self.total_layers, "context_window": self.context_window,
            "required_ram_mb": self.required_ram_mb
        }

# Dummy model registry
AVAILABLE_MODELS = {
    "llama3-8b-gguf": ModelManifest("llama3-8b-gguf", "llama", 32, 8192, 4500)
}

# ==========================================
# 3. LOCAL WORKER WRAPPER
# ==========================================
class LocalInferenceWorker:
    """PocketPal-style lightweight local inference loop."""
    @staticmethod
    async def process_tensor_payload(session_id: str, prompt_chunk: str, layer_start: int, layer_end: int):
        """Simulates processing a specific block of layers for a given token context."""
        logger.debug(f"[Worker] Processing layers {layer_start}-{layer_end} for session {session_id[:8]}...")
        # Simulate computational delay (tensor multiplication, attention, etc.)
        compute_time = 0.5 + (len(prompt_chunk) * 0.01)
        await asyncio.sleep(compute_time)
        
        # Simulate generated token fragment based on the input chunk
        token_fragment = f" [tokenized_output_from_{prompt_chunk.strip()[:10]}] "
        return token_fragment

# ==========================================
# 2. DISTRIBUTED INFERENCE ROUTER
# ==========================================
class AIPoolOrchestrator:
    """Routes prompts, manages KV states, delegates chunks, and handles failovers."""
    def __init__(self, node):
        self.node = node
        self.active_sessions: Dict[str, dict] = {}

    def _select_peers_for_layers(self, manifest: ModelManifest, num_chunks: int) -> List[str]:
        """Selects optimal peers based on available RAM and CPU load."""
        active_peers = [
            pid for pid, p in self.node.peers.items() 
            if p.get("writer") and (time.time() - p["last_seen"] < 10)
        ]
        
        # Sort by best availability (low CPU, high RAM)
        active_peers.sort(key=lambda pid: (self.node.peers[pid].get("cpu", 100.0), -self.node.peers[pid].get("ram", 0)))
        
        if not active_peers:
            return []
            
        # Distribute chunks across top available peers (round-robin)
        selected = []
        for i in range(num_chunks):
            selected.append(active_peers[i % len(active_peers)])
        return selected

    async def generate_distributed(self, prompt: str, model_id: str):
        """Splits prompt context and delegates generation across mesh."""
        manifest = AVAILABLE_MODELS.get(model_id)
        if not manifest:
            logger.error(f"Model {model_id} not registered.")
            return

        session_id = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
        self.active_sessions[session_id] = {"prompt": prompt, "fragments": {}, "status": "processing"}
        
        # Split prompt into semantic chunks (simulating context window sharding)
        words = prompt.split()
        chunk_size = max(1, len(words) // 3) # Example: split into up to 3 chunks
        chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        
        target_peers = self._select_peers_for_layers(manifest, len(chunks))
        if not target_peers:
            logger.warning("No peers available for AI pooling. Running locally...")
            res = await LocalInferenceWorker.process_tensor_payload(session_id, prompt, 0, manifest.total_layers)
            logger.info(f"Local Inference Result: {res}")
            return res

        logger.info(f"Orchestrating AI generation across {len(set(target_peers))} peers for session {session_id[:8]}")
        
        tasks = []
        for i, chunk in enumerate(chunks):
            peer_id = target_peers[i]
            tasks.append(self._dispatch_with_failover(session_id, i, chunk, peer_id, manifest))
            
        results = await asyncio.gather(*tasks)
        final_output = "".join(filter(None, results))
        
        logger.info(f"Final Assembled Output: {final_output}")
        del self.active_sessions[session_id]
        return final_output

    async def _dispatch_with_failover(self, session_id: str, chunk_index: int, chunk_data: str, target_peer: str, manifest: ModelManifest, retry_count=0):
        """4. FAILOVER & RESYNC: Handles dispatching and re-routing if node drops."""
        if retry_count > 3:
            logger.error(f"Max retries exceeded for session {session_id[:8]} chunk {chunk_index}. Context lost.")
            return "[ERR_CONTEXT_LOST]"
            
        try:
            writer = self.node.peers[target_peer]["writer"]
            
            # Setup a Future to wait for the specific response
            future_id = f"{session_id}_{chunk_index}"
            loop = asyncio.get_running_loop()
            self.node.pending_inference_responses[future_id] = loop.create_future()
            
            msg = {
                "type": "ai_inference_req",
                "session_id": session_id,
                "future_id": future_id,
                "chunk_index": chunk_index,
                "chunk_data": chunk_data,
                "layer_start": 0,
                "layer_end": manifest.total_layers,
                "origin": self.node.node_id
            }
            writer.write((json.dumps(msg) + "\n").encode('utf-8'))
            await writer.drain()
            logger.info(f"Delegated inference chunk {chunk_index} to {target_peer[:8]}")
            
            # Wait for response with timeout for failover
            result = await asyncio.wait_for(self.node.pending_inference_responses[future_id], timeout=15.0)
            return result
            
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"Peer {target_peer[:8]} dropped or timed out (Err: {e}). Rerouting context block {chunk_index}...")
            # Cleanup broken future
            if future_id in self.node.pending_inference_responses:
                del self.node.pending_inference_responses[future_id]
            
            # Re-select a new peer (excluding the failed one if possible)
            available = self._select_peers_for_layers(manifest, 2)
            new_target = available[0] if available else self.node.node_id
            
            if new_target == self.node.node_id:
                logger.info("Fallback to local worker execution...")
                return await LocalInferenceWorker.process_tensor_payload(session_id, chunk_data, 0, manifest.total_layers)
            
            return await self._dispatch_with_failover(session_id, chunk_index, chunk_data, new_target, manifest, retry_count + 1)


# ==========================================
# CORE NODE (Updated for AI Inference)
# ==========================================
class HeartbeatProtocol(asyncio.DatagramProtocol):
    def __init__(self, node): self.node = node
    def datagram_received(self, data: bytes, addr):
        try:
            msg = json.loads(data.decode('utf-8'))
            if msg.get("type") == "heartbeat":
                asyncio.create_task(self.node.handle_heartbeat(msg, addr))
        except: pass

class P2PNode:
    def __init__(self, host: str, tcp_port: int, udp_port: int):
        self.host, self.tcp_port, self.udp_port = host, tcp_port, udp_port
        self.node_id = hashlib.sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()
        self.peers: Dict[str, Dict[str, Any]] = {}
        
        self.pending_inference_responses: Dict[str, asyncio.Future] = {}
        self.ai_orchestrator = AIPoolOrchestrator(self)
        self.running = False
        logger.info(f"Initialized AI Inference Node [{self.node_id[:8]}]")

    async def start(self):
        self.running = True
        server = await asyncio.start_server(self._handle_tcp_client, self.host, self.tcp_port)
        loop = asyncio.get_running_loop()
        await loop.create_datagram_endpoint(lambda: HeartbeatProtocol(self), local_addr=('0.0.0.0', self.udp_port), allow_broadcast=True)
        asyncio.create_task(self.broadcast_heartbeat())
        async with server: await server.serve_forever()

    async def broadcast_heartbeat(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setblocking(False)
        loop = asyncio.get_running_loop()
        while self.running:
            try:
                msg = json.dumps({
                    "type": "heartbeat", "node_id": self.node_id, "tcp_port": self.tcp_port,
                    "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().available
                }).encode('utf-8')
                await loop.sock_sendto(sock, msg, ('255.255.255.255', self.udp_port))
            except: pass
            await asyncio.sleep(3)

    async def handle_heartbeat(self, message: dict, addr: tuple):
        peer_id = message.get("node_id")
        if peer_id == self.node_id: return
        if peer_id not in self.peers or not self.peers[peer_id].get("writer"):
            await self.connect_to_peer(addr[0], message.get("tcp_port"), peer_id)
        if peer_id in self.peers:
            self.peers[peer_id].update({"last_seen": time.time(), "cpu": message.get("cpu", 100.0), "ram": message.get("ram", 0)})

    async def connect_to_peer(self, host: str, port: int, peer_id: str):
        try:
            reader, writer = await asyncio.open_connection(host, port)
            self.peers[peer_id] = {"host": host, "port": port, "writer": writer, "last_seen": time.time(), "cpu": 100.0, "ram": 0}
            msg = {"type": "handshake", "node_id": self.node_id, "host": self.host, "tcp_port": self.tcp_port}
            writer.write((json.dumps(msg) + "\n").encode('utf-8'))
            await writer.drain()
            asyncio.create_task(self._handle_tcp_client(reader, writer))
        except: pass

    async def _handle_tcp_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while self.running:
                data = await reader.readline()
                if not data: break
                await self.process_message(json.loads(data.decode('utf-8')), writer)
        except: pass

    async def process_message(self, msg: dict, writer: asyncio.StreamWriter):
        msg_type = msg.get("type")
        if msg_type == "handshake":
            peer_id = msg.get("node_id")
            if peer_id and peer_id not in self.peers:
                await self.connect_to_peer(msg.get("host"), msg.get("tcp_port"), peer_id)
                
        elif msg_type == "ai_inference_req":
            # Process prompt chunk locally
            future_id = msg.get("future_id")
            origin = msg.get("origin")
            logger.info(f"Received inference request {future_id} from {origin[:8]}")
            
            async def run_local_worker():
                res = await LocalInferenceWorker.process_tensor_payload(
                    msg.get("session_id"), msg.get("chunk_data"), msg.get("layer_start"), msg.get("layer_end")
                )
                resp = {"type": "ai_inference_res", "future_id": future_id, "result": res}
                writer.write((json.dumps(resp) + "\n").encode('utf-8'))
                await writer.drain()
            asyncio.create_task(run_local_worker())
            
        elif msg_type == "ai_inference_res":
            future_id = msg.get("future_id")
            if future_id in self.pending_inference_responses:
                future = self.pending_inference_responses.pop(future_id)
                if not future.done():
                    future.set_result(msg.get("result"))

async def async_main(args):
    node = P2PNode(host=args.host, tcp_port=args.tcp_port, udp_port=args.udp_port)
    server_task = asyncio.create_task(node.start())
    
    if args.seed:
        for seed in args.seed:
            try: h, p = seed.split(':'); await node.connect_to_peer(h, int(p), "seed")
            except: pass
            
    await asyncio.sleep(2)
    logger.info("\n--- DISTRIBUTED AI INFERENCE ENGINE READY ---")
    logger.info("Type an AI prompt to shard its context across the network.")
    
    while True:
        try:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "Prompt > ")
            if cmd.lower() == 'quit': break
            if cmd:
                await node.ai_orchestrator.generate_distributed(cmd, "llama3-8b-gguf")
        except EOFError: break
        except KeyboardInterrupt: break
            
    node.running = False
    server_task.cancel()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--tcp-port", type=int, default=8000)
    parser.add_argument("--udp-port", type=int, default=9999)
    parser.add_argument("--seed", type=str, action="append")
    try: asyncio.run(async_main(parser.parse_args()))
    except KeyboardInterrupt: pass
