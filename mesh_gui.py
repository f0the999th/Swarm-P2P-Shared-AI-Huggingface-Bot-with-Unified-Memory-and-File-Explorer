import asyncio
import json
import random
import hashlib
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="P2P Mesh AI GUI - Unified Memory")

# ==========================================
# ASYNCHRONOUS COMPUTE & UNIFIED MEMORY BACKEND
# ==========================================

PEER_IDS = ["node-alpha-01", "node-beta-99", "node-gamma-42", "node-delta-07", "node-omega-X"]
ROLES = ["Compute Node", "Storage Node", "Gateway Node"]

class MemoryToggle(BaseModel):
    level: str

class MemoryQuery(BaseModel):
    query: str
    level: str

class TeamCreate(BaseModel):
    name: str

class TeamJoin(BaseModel):
    hash_id: str

class ConnectorConfigReq(BaseModel):
    provider: str
    api_key: str
    hybrid_fallback: bool
    webhook_url: str

class WebhookTestReq(BaseModel):
    url: str

class IncomingWebhook(BaseModel):
    source: str
    context: str

class SeedPayload(BaseModel):
    filename: str
    content: str
    team_id: str = None

class MeshSimulator:
    def __init__(self):
        self.peers = []
        self.teams = {}
        self.webhook_queue = []
        self.explorer_files = {}
        for i, pid in enumerate(PEER_IDS):
            role = "Compute Node" if i == 0 else "Storage Node" if i == 1 else "Gateway Node" if i == 2 else random.choice(ROLES)
            ram = random.randint(8000, 24000) if role == "Compute Node" else random.randint(1000, 4000)
            shares_memory = random.choice([True, False]) if role != "Gateway Node" else True
            
            self.peers.append({
                "id": pid, 
                "role": role,
                "latency": random.randint(5, 150), 
                "up": random.uniform(5.0, 50.0), 
                "down": random.uniform(10.0, 100.0), 
                "ram": ram,
                "max_ram": ram,
                "shards": random.randint(10, 100),
                "shares_memory": shares_memory,
                "vector_count": random.randint(1000, 15000) if shares_memory else 0
            })
            
        self.active_generation = False
        self.local_participation_level = "Isolated"
        self.local_vector_index = random.randint(100, 500)

    def get_network_state(self):
        for p in self.peers:
            p["latency"] = max(2, p["latency"] + random.randint(-5, 5))
            if self.active_generation and p["role"] == "Compute Node":
                p["ram"] = max(100, p["ram"] - random.randint(50, 200))
            else:
                p["ram"] = min(p["max_ram"], p["ram"] + random.randint(50, 300))
            
            # Simulate DHT vector syncing if node shares memory
            if p["shares_memory"]:
                p["vector_count"] += random.randint(0, 5)
        
        # Grow local index slightly if participating/contributing
        if self.local_participation_level != "Isolated" and random.random() > 0.5:
            self.local_vector_index += 1

        active_memory_nodes = sum(1 for p in self.peers if p["shares_memory"])
        swarm_pool_size = sum(p["vector_count"] for p in self.peers) + (self.local_vector_index if self.local_participation_level != "Isolated" else 0)

        return {
            "type": "metrics",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "peers": self.peers,
            "system_cpu": random.randint(70, 98) if self.active_generation else random.randint(5, 15),
            "free_ram": sum(p["ram"] for p in self.peers),
            "local_vector_size": self.local_vector_index,
            "active_memory_nodes": active_memory_nodes,
            "swarm_pool_size": swarm_pool_size,
            "participation_level": self.local_participation_level
        }
        
    def mock_embed(self, text: str):
        """Simulates a localized CPU-bound vector embedding function."""
        h = hashlib.md5(text.encode()).hexdigest()
        return [round(random.uniform(-1.0, 1.0), 4) for _ in range(5)] # Mock 5-dim vector

    def toggle_memory(self, level: str):
        self.local_participation_level = level
        return {"status": "success", "level": self.local_participation_level}

    def query_memory(self, text: str, level: str):
        # Privacy guard: Validate level
        if level == "Isolated" or self.local_participation_level == "Isolated":
            return {"status": "blocked", "reason": "Absolute data sovereignty maintained. No DHT query executed."}
        
        # Local Embedding
        vector = self.mock_embed(text)
        self.local_vector_index += 1 # Indexing the query
        
        if level == "Contributor":
            return {"status": "contributed", "reason": f"Anonymized vector hashed and seeded to DHT. No external context retrieved."}
            
        # Participant - Full Query
        active_nodes = [p for p in self.peers if p["shares_memory"]]
        retrieved_chunks = random.randint(2, min(5, len(active_nodes))) if active_nodes else 0
        
        return {
            "status": "success",
            "retrieved": retrieved_chunks,
            "nodes_accessed": len(active_nodes),
            "vector_preview": str(vector[:2]) + "...",
            "context_injected": "Successfully mapped decentralized context."
        }

    async def execute_compute_task(self, payload: dict, websocket: WebSocket):
        prompt = payload.get("prompt", "")
        sys_prompt = payload.get("system_prompt", "None")
        temperature = payload.get("temperature", 0.7)
        memory_context = payload.get("memory_context", "")
        team_id = payload.get("team_id")
        is_federated = payload.get("is_federated", False)
        is_hybrid = payload.get("is_hybrid", False)
        api_key = payload.get("api_key", "")
        
        self.active_generation = True
        await asyncio.sleep(0.5)
        
        compute_nodes = [p["id"] for p in self.peers if p["role"] == "Compute Node"] or [self.peers[0]["id"]]
        
        webhook_context = ""
        if self.webhook_queue:
            webhook_context = "\\n".join(self.webhook_queue)
            self.webhook_queue.clear()

        dummy_response = (
            f"**Stateless Mesh Execution Started**\\n\\n"
            f"> Persona Constraints: `{sys_prompt[:30]}...` (Temp: {temperature})\\n"
        )
        if memory_context:
            dummy_response += f"> Memory Context: `{memory_context}`\\n"
        if webhook_context:
            dummy_response += f"> External App Webhook Data: `{webhook_context}`\\n"
            
        if is_hybrid and api_key:
            dummy_response += (
                f"\\n🚨 **HYBRID FALLBACK TRIGGERED** 🚨\\n"
                f"Complex task detected. Routing via proprietary adapter ({len(api_key)} chars key).\\n"
                f"Bypassing local mesh... Synthesizing via external LLM endpoint..."
            )
        elif is_federated and team_id and team_id in self.teams:
            dummy_response += f"\\nFederated Task Sharding Active for Team Swarm: `{team_id}`... Distributing compute across team peers...\\n"
            team_sockets = self.teams[team_id]["sockets"]
            for ws in team_sockets:
                if ws != websocket:
                    try:
                        await ws.send_json({"type": "team_event", "event": "Federated sharding active: prompt split among team members."})
                    except:
                        pass
        else:
            dummy_response += (
                f"\\nExecuting prompt tensors using the `{compute_nodes[0]}` node group. "
                f"The P2P network computes this dynamically without violating local client states. "
                f"Inference stream active..."
            )
        
        words = dummy_response.split(" ")
        for i, word in enumerate(words):
            assigned_peer = random.choice(compute_nodes)
            chunk_data = {
                "type": "token",
                "text": word + " ",
                "peer": assigned_peer,
                "is_final": i == len(words) - 1
            }
            try:
                await websocket.send_json(chunk_data)
            except WebSocketDisconnect:
                break
            await asyncio.sleep(random.uniform(0.01, 0.08))
                
        self.active_generation = False

simulator = MeshSimulator()

# ==========================================
# FASTAPI ROUTES
# ==========================================

@app.post("/api/memory/toggle")
async def toggle_memory(req: MemoryToggle):
    return simulator.toggle_memory(req.level)

@app.post("/api/memory/query")
async def query_memory(req: MemoryQuery):
    # Simulate network DHT search latency
    await asyncio.sleep(random.uniform(0.3, 0.8))
    return simulator.query_memory(req.query, req.level)

@app.post("/api/teams/create")
async def create_team(req: TeamCreate):
    team_id = hashlib.sha256(f"{req.name}-{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    simulator.teams[team_id] = {"name": req.name, "vault": {}, "sockets": []}
    return {"status": "success", "team_id": team_id, "name": req.name}

@app.post("/api/teams/join")
async def join_team(req: TeamJoin):
    if req.hash_id in simulator.teams:
        return {"status": "success", "team_id": req.hash_id, "name": simulator.teams[req.hash_id]["name"]}
    return {"status": "error", "message": "Invalid Team Hash ID"}

@app.post("/api/connectors/config")
async def config_connector(req: ConnectorConfigReq):
    return {"status": "success", "message": f"Adapter for {req.provider} configured securely."}

@app.post("/api/connectors/test-hook")
async def test_webhook(req: WebhookTestReq):
    await asyncio.sleep(0.5)
    return {"status": "success", "message": f"Webhook ping successful to {req.url}"}

@app.post("/api/webhooks/incoming")
async def incoming_webhook(req: IncomingWebhook):
    simulator.webhook_queue.append(f"[{req.source}] {req.context}")
    return {"status": "success", "message": "Context injected into active session memory."}

@app.post("/api/webhooks/outgoing")
async def outgoing_webhook(payload: dict):
    return {"status": "success", "dispatched_bytes": len(str(payload))}

class ExplorerSplitPayload(BaseModel):
    filename: str
    content: str
    team_id: str = None

@app.post("/api/explorer/split")
async def explorer_split(req: ExplorerSplitPayload):
    import hashlib
    from datetime import datetime
    file_id = hashlib.md5(f"{req.filename}-{datetime.now().timestamp()}".encode()).hexdigest()
    shard_count = max(1, len(req.content) // 1024)
    file_hash = hashlib.sha256(req.content.encode()).hexdigest()
    
    state = "Team-Shared" if req.team_id else "Swarm"
    
    blocks = []
    import random
    for i in range(shard_count):
        node = random.choice([p["id"] for p in simulator.peers])
        blocks.append({
            "id": i,
            "hash": hashlib.sha256(f"{file_hash}-{i}".encode()).hexdigest()[:12],
            "node": node,
            "status": "seeded" if random.random() > 0.1 else "pending"
        })
        
    simulator.explorer_files[file_id] = {
        "id": file_id,
        "name": req.filename,
        "size_kb": round(len(req.content) / 1024, 2),
        "shards": shard_count,
        "hash": file_hash[:16],
        "state": state,
        "blocks": blocks,
        "team_id": req.team_id,
        "is_pmem": req.filename.endswith(".pmem")
    }
    
    if req.team_id and req.team_id in simulator.teams:
        simulator.teams[req.team_id]["vault"][req.filename] = f"<archive:{shard_count} shards>"
        for ws in simulator.teams[req.team_id]["sockets"]:
            try:
                await ws.send_json({
                    "type": "pmem_sync",
                    "vault": simulator.teams[req.team_id]["vault"]
                })
            except:
                pass
                
    for p in simulator.peers:
        p["up"] += random.uniform(5.0, 20.0)
        p["down"] += random.uniform(5.0, 20.0)
        
    return {"status": "success", "file_id": file_id, "filename": req.filename, "shards": shard_count}

@app.get("/api/explorer/files")
async def get_explorer_files():
    # omit blocks for summary
    return [{"id": f["id"], "name": f["name"], "size_kb": f["size_kb"], "shards": f["shards"], "hash": f["hash"], "state": f["state"], "is_pmem": f.get("is_pmem", False)} for f in simulator.explorer_files.values()]

@app.get("/api/explorer/shards/{file_id}")
async def get_explorer_shards(file_id: str):
    if file_id in simulator.explorer_files:
        return simulator.explorer_files[file_id]["blocks"]
    return []

@app.post("/api/explorer/action")
async def explorer_action(payload: dict):
    file_id = payload.get("file_id")
    action = payload.get("action")
    if file_id in simulator.explorer_files:
        if action == "delete":
            del simulator.explorer_files[file_id]
        elif action == "toggle_seed":
            f = simulator.explorer_files[file_id]
            f["state"] = "Local" if f["state"] in ["Swarm", "Team-Shared"] else "Swarm"
        return {"status": "success"}
    return {"status": "error"}

@app.post("/api/explorer/split")
async def seed_file(req: SeedPayload):
    shard_count = max(1, len(req.content) // 1024)
    if req.team_id and req.team_id in simulator.teams:
        simulator.teams[req.team_id]["vault"][req.filename] = f"<archive:{shard_count} shards>"
        for ws in simulator.teams[req.team_id]["sockets"]:
            try:
                await ws.send_json({
                    "type": "pmem_sync",
                    "vault": simulator.teams[req.team_id]["vault"]
                })
            except:
                pass
    return {"status": "success", "filename": req.filename, "shards": shard_count}

@app.get("/")
async def get_dashboard():
    return HTMLResponse(HTML_CONTENT)

@app.websocket("/ws/team/{team_id}")
async def websocket_team_endpoint(websocket: WebSocket, team_id: str):
    await websocket.accept()
    if team_id not in simulator.teams:
        await websocket.close()
        return
    
    simulator.teams[team_id]["sockets"].append(websocket)
    try:
        for ws in simulator.teams[team_id]["sockets"]:
            if ws != websocket:
                await ws.send_json({"type": "team_event", "event": "New peer joined the team swarm."})
        
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            if payload.get("action") == "pmem_sync":
                key = payload.get("key")
                val = payload.get("value")
                simulator.teams[team_id]["vault"][key] = val
                for ws in simulator.teams[team_id]["sockets"]:
                    if ws != websocket:
                        await ws.send_json({
                            "type": "pmem_sync",
                            "vault": simulator.teams[team_id]["vault"]
                        })
    except WebSocketDisconnect:
        if websocket in simulator.teams[team_id]["sockets"]:
            simulator.teams[team_id]["sockets"].remove(websocket)

@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async def metrics_broadcaster():
        try:
            while True:
                data = simulator.get_network_state()
                await websocket.send_json(data)
                await asyncio.sleep(1.0)
        except WebSocketDisconnect:
            pass
    broadcaster_task = asyncio.create_task(metrics_broadcaster())
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            if payload.get("action") == "compute_task":
                await simulator.execute_compute_task(payload, websocket)
    except WebSocketDisconnect:
        broadcaster_task.cancel()


# ==========================================
# EMBEDDED FRONTEND (HTML + Tailwind + Alpine.js)
# ==========================================
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Memory & Persona Mesh</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #111827; }
        ::-webkit-scrollbar-thumb { background: #374151; border-radius: 4px; }
        
        .shard-grid { display: grid; grid-template-columns: repeat(20, 1fr); gap: 2px; }
        .shard-block { width: 100%; aspect-ratio: 1; border-radius: 1px; transition: background 0.2s; }
        .shard-active { background-color: #8b5cf6; box-shadow: 0 0 6px #8b5cf680; }
        .shard-inactive { background-color: #1f2937; }
        
        .prose pre { background-color: #111827; padding: 1rem; border-radius: 0.5rem; border: 1px solid #374151; }
        .prose code { color: #a78bfa; }
        .cursor::after { content: '▋'; animation: blink 1s step-start infinite; color: #8b5cf6; margin-left: 2px; }
        @keyframes blink { 50% { opacity: 0; } }
    </style>
</head>
<body class="bg-gray-950 text-gray-200 h-screen w-screen overflow-hidden flex font-sans antialiased selection:bg-purple-500/30" x-data="meshApp()" x-init="initApp()">

    <!-- MODAL: Local Persona -->
    <div x-show="showPersonaModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" style="display: none;" x-transition>
        <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-[450px] shadow-2xl" @click.outside="showPersonaModal = false">
            <h2 class="text-xl font-bold text-white mb-1">Create Local Persona</h2>
            <p class="text-xs text-gray-400 mb-5">Stored securely in your browser's local storage.</p>
            <div class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold text-gray-400 mb-1">Avatar & Name</label>
                    <div class="flex gap-2">
                        <input type="text" x-model="newPersona.avatar" class="w-16 bg-gray-950 border border-gray-700 rounded-lg p-2 text-center text-xl focus:border-purple-500 outline-none">
                        <input type="text" x-model="newPersona.name" class="flex-1 bg-gray-950 border border-gray-700 rounded-lg p-2 text-sm text-white focus:border-purple-500 outline-none" placeholder="e.g. Code Assistant">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-400 mb-1">System Prompt</label>
                    <textarea x-model="newPersona.sysPrompt" rows="3" class="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-sm text-gray-300 focus:border-purple-500 outline-none"></textarea>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-400 mb-1">Temperature: <span x-text="newPersona.temp"></span></label>
                    <input type="range" x-model="newPersona.temp" min="0" max="1" step="0.1" class="w-full accent-purple-500">
                </div>
            </div>
            <div class="flex justify-end gap-3 mt-6">
                <button @click="showPersonaModal = false" class="px-4 py-2 rounded-lg text-sm font-semibold text-gray-400 hover:text-white transition">Cancel</button>
                <button @click="savePersona()" class="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold transition">Save Locally</button>
            </div>
        </div>
    </div>

    <!-- MODAL: Unified Memory Settings -->
    <div x-show="showMemoryModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" style="display: none;" x-transition>
        <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-[500px] shadow-2xl" @click.outside="showMemoryModal = false">
            <h2 class="text-xl font-bold text-white mb-1 flex items-center gap-2">
                <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                Unified Memory & Privacy
            </h2>
            <p class="text-xs text-gray-400 mb-5">Configure decentralized vector DHT sharing. Changes are saved locally.</p>
            
            <div class="space-y-3">
                <label class="flex items-start gap-3 p-3 rounded-lg border border-gray-700 hover:bg-gray-800/50 cursor-pointer transition" :class="memoryLevel === 'Isolated' ? 'bg-gray-800/50 ring-1 ring-blue-500/50 border-blue-500/30' : ''">
                    <input type="radio" x-model="memoryLevel" value="Isolated" class="mt-1 accent-blue-500">
                    <div>
                        <div class="text-sm font-semibold text-white">Isolated (Default)</div>
                        <div class="text-xs text-gray-400">Strict data sovereignty. Local vectors are never shared or queried against the DHT swarm.</div>
                    </div>
                </label>
                <label class="flex items-start gap-3 p-3 rounded-lg border border-gray-700 hover:bg-gray-800/50 cursor-pointer transition" :class="memoryLevel === 'Contributor' ? 'bg-gray-800/50 ring-1 ring-blue-500/50 border-blue-500/30' : ''">
                    <input type="radio" x-model="memoryLevel" value="Contributor" class="mt-1 accent-blue-500">
                    <div>
                        <div class="text-sm font-semibold text-white">Contributor</div>
                        <div class="text-xs text-gray-400">Anonymizes and seeds local embeddings to the swarm, but does not query external nodes for context.</div>
                    </div>
                </label>
                <label class="flex items-start gap-3 p-3 rounded-lg border border-gray-700 hover:bg-gray-800/50 cursor-pointer transition" :class="memoryLevel === 'Participant' ? 'bg-gray-800/50 ring-1 ring-blue-500/50 border-blue-500/30' : ''">
                    <input type="radio" x-model="memoryLevel" value="Participant" class="mt-1 accent-blue-500">
                    <div>
                        <div class="text-sm font-semibold text-white flex items-center gap-2">Participant <span class="px-1.5 py-0.5 rounded bg-blue-900/50 text-blue-400 text-[10px] uppercase font-bold tracking-wider border border-blue-700/50">Full RAG</span></div>
                        <div class="text-xs text-gray-400">Seeds anonymized vectors and dynamically queries the DHT swarm for expanded decentralized context.</div>
                    </div>
                </label>
            </div>
            
            <div class="flex justify-end gap-3 mt-6">
                <button @click="saveMemoryLevel()" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold transition shadow-lg w-full">Apply Memory Settings</button>
            </div>
        </div>
    </div>

    <!-- MODAL: Model Connectors & API Hooks -->
    <div x-show="showConnectorsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" style="display: none;" x-transition>
        <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-[550px] shadow-2xl" @click.outside="showConnectorsModal = false">
            <h2 class="text-xl font-bold text-white mb-1 flex items-center gap-2">
                <svg class="w-6 h-6 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                Model Connectors & API Hooks
            </h2>
            <p class="text-xs text-gray-400 mb-5">Configure hybrid fallback routing and external application webhooks. Keys are encrypted and isolated locally.</p>
            
            <div class="space-y-4">
                <div class="p-4 bg-gray-950 border border-gray-800 rounded-lg">
                    <h3 class="text-sm font-semibold text-gray-300 mb-3">Proprietary API Adapter</h3>
                    <div class="grid grid-cols-2 gap-3 mb-3">
                        <div>
                            <label class="block text-xs text-gray-500 mb-1">Provider Schema</label>
                            <select x-model="connectorConfig.provider" class="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-sm text-white focus:border-emerald-500 outline-none">
                                <option value="openai">OpenAI Compatible</option>
                                <option value="anthropic">Anthropic Claude</option>
                                <option value="gemini">Google Gemini</option>
                                <option value="custom">Custom Webhook</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 mb-1">API Key (Locally Encrypted)</label>
                            <input type="password" x-model="connectorConfig.apiKey" placeholder="sk-..." class="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-sm text-white focus:border-emerald-500 outline-none">
                        </div>
                    </div>
                    <label class="flex items-center gap-2 cursor-pointer mt-2 w-max">
                        <input type="checkbox" x-model="connectorConfig.hybridFallback" class="accent-emerald-500 w-4 h-4 rounded bg-gray-900 border-gray-700">
                        <span class="text-sm font-semibold text-gray-300">Enable Hybrid Fallback Engine</span>
                    </label>
                    <p class="text-[10px] text-gray-500 mt-1 ml-6">Automatically routes complex reasoning tasks to the proprietary endpoint, bypassing the local P2P mesh.</p>
                </div>

                <div class="p-4 bg-gray-950 border border-gray-800 rounded-lg">
                    <h3 class="text-sm font-semibold text-gray-300 mb-3">External Application Webhooks</h3>
                    <div class="mb-3">
                        <label class="block text-xs text-gray-500 mb-1">Outgoing Webhook URL</label>
                        <div class="flex gap-2">
                            <input type="text" x-model="connectorConfig.webhookUrl" placeholder="https://app.local/webhook" class="flex-1 bg-gray-900 border border-gray-700 rounded-lg p-2 text-sm text-white focus:border-emerald-500 outline-none">
                            <button @click="testWebhook()" class="px-3 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-xs font-semibold text-white transition shrink-0">Test Hook</button>
                        </div>
                        <div x-show="webhookTestResult" class="text-xs text-emerald-400 font-mono mt-2" x-text="webhookTestResult"></div>
                    </div>
                    <div class="mt-3 text-[10px] text-gray-500 font-mono p-2 bg-gray-900 rounded border border-gray-800 break-all">
                        INCOMING: <span class="text-emerald-400">POST /api/webhooks/incoming</span><br>
                        PAYLOAD: <span class="text-gray-400">{ "source": "App", "context": "..." }</span>
                    </div>
                </div>
            </div>
            
            <div class="flex justify-end gap-3 mt-6">
                <button @click="showConnectorsModal = false" class="px-4 py-2 rounded-lg text-sm font-semibold text-gray-400 hover:text-white transition">Cancel</button>
                <button @click="saveConnectorConfig()" class="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition shadow-lg">Save Configuration</button>
            </div>
        </div>
    </div>


    <!-- MODAL: Shard Health Visualizer -->
    <div x-show="showShardModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" style="display: none;" x-transition>
        <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-[600px] shadow-2xl" @click.outside="showShardModal = false">
            <h2 class="text-xl font-bold text-white mb-1 flex items-center gap-2">
                <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
                Shard Health: <span class="text-blue-400 font-mono text-sm" x-text="activeShardFile?.name"></span>
            </h2>
            <p class="text-xs text-gray-400 mb-5">Visualizing specific SHA-256 chunks stored locally versus seeded across the mesh.</p>
            
            <div class="bg-gray-950 border border-gray-800 rounded-lg p-4 mb-4">
                <div class="grid grid-cols-10 gap-2 max-h-64 overflow-y-auto pr-2">
                    <template x-for="block in activeShardBlocks" :key="block.id">
                        <div class="relative group cursor-crosshair">
                            <div class="w-full aspect-square rounded-sm transition-all duration-300"
                                 :class="block.status === 'seeded' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-gray-800'"></div>
                            
                            <!-- Tooltip -->
                            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-gray-900 border border-gray-700 rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                                <div class="text-[10px] text-gray-400 font-mono mb-1">Block #<span x-text="block.id"></span></div>
                                <div class="text-[10px] text-gray-300 font-mono truncate" x-text="'Hash: ' + block.hash"></div>
                                <div class="text-[10px] mt-1" :class="block.status === 'seeded' ? 'text-emerald-400' : 'text-gray-500'" x-text="block.status === 'seeded' ? 'Seeded on ' + block.node : 'Pending Sync'"></div>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
            
            <div class="flex justify-between items-center">
                <div class="flex items-center gap-4 text-xs font-semibold">
                    <div class="flex items-center gap-1"><div class="w-3 h-3 bg-emerald-500 rounded-sm"></div> <span class="text-gray-300">Seeded</span></div>
                    <div class="flex items-center gap-1"><div class="w-3 h-3 bg-gray-800 rounded-sm"></div> <span class="text-gray-500">Pending</span></div>
                </div>
                <button @click="showShardModal = false" class="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-white text-sm font-semibold transition">Close Viewer</button>
            </div>
        </div>
    </div>

    <!-- MODAL: Seed Local File (.pmem) -->
    <div x-show="showSeedModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" style="display: none;" x-transition>
        <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-[550px] shadow-2xl" @click.outside="showSeedModal = false">
            <h2 class="text-xl font-bold text-white mb-1 flex items-center gap-2">
                <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path></svg>
                Seed File into Mesh (.pmem)
            </h2>
            <p class="text-xs text-gray-400 mb-5">Select a local file to cryptographically fragment and seed into the distributed .pmem vault.</p>
            
            <div class="space-y-4">
                <div class="border-2 border-dashed border-gray-700 rounded-lg p-8 flex flex-col items-center justify-center bg-gray-950 transition hover:border-purple-500/50 cursor-pointer"
                     @click="$refs.fileInput.click()">
                    <svg class="w-10 h-10 text-gray-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                    <div class="text-sm text-gray-300 font-semibold" x-text="selectedFile ? selectedFile.name : 'Click to select a file'"></div>
                    <div class="text-xs text-gray-500 mt-1" x-text="selectedFile ? (selectedFile.size / 1024).toFixed(1) + ' KB' : 'Any text or data file'"></div>
                    <input type="file" x-ref="fileInput" class="hidden" @change="handleFileSelect($event)">
                </div>

                <div x-show="seederProgress > 0" class="mt-4">
                    <div class="flex justify-between text-xs text-gray-400 mb-1">
                        <span>Fragmenting & Seeding...</span>
                        <span x-text="Math.round(seederProgress) + '%'"></span>
                    </div>
                    <div class="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                        <div class="bg-purple-500 h-2 rounded-full transition-all duration-300 ease-out" :style="`width: ${seederProgress}%`"></div>
                    </div>
                </div>

                <div x-show="seededFiles.length > 0" class="mt-4">
                    <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Seeded Archives</h3>
                    <div class="space-y-2 max-h-32 overflow-y-auto pr-2">
                        <template x-for="file in seededFiles" :key="file.name">
                            <div class="flex items-center justify-between bg-gray-950 border border-gray-800 p-2 rounded-lg">
                                <div class="flex items-center gap-2">
                                    <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                                    <span class="text-xs text-gray-300 truncate w-48" x-text="file.name"></span>
                                </div>
                                <div class="text-[10px] text-gray-500 font-mono" x-text="file.shards + ' shards'"></div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
            
            <div class="flex justify-end gap-3 mt-6">
                <button @click="showSeedModal = false" class="px-4 py-2 rounded-lg text-sm font-semibold text-gray-400 hover:text-white transition">Close</button>
                <button @click="seedFileToMesh()" :disabled="!selectedFile || isSeeding" class="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-semibold transition shadow-lg">Fragment & Seed</button>
            </div>
        </div>
    </div>

    <!-- ZONE A: Torrent Dashboard -->
    <div class="w-1/2 h-full border-r border-gray-800 flex flex-col bg-gray-900/40 relative z-10 overflow-hidden">
        <div class="px-5 pt-5 pb-0 border-b border-gray-800 bg-gray-950/50 backdrop-blur-md flex flex-col gap-4">
            <div class="flex justify-between items-start">
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-3">
                        <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                        Asynchronous Compute Grid
                    </h1>
                    <p class="text-xs text-gray-500 mt-1 uppercase tracking-wider font-semibold">Stateless Execution Mesh</p>
                </div>
                <button @click="showSeedModal = true" class="bg-gray-800 border border-gray-700 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-2 transition">
                    <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                    Seed Local File
                </button>
            </div>
            
            <div class="flex gap-4">
                <button @click="activeZoneATab = 'compute'" class="px-3 py-2 text-sm font-semibold border-b-2 transition-colors focus:outline-none" :class="activeZoneATab === 'compute' ? 'border-purple-500 text-purple-400' : 'border-transparent text-gray-400 hover:text-gray-300'">Compute Stats</button>
                <button @click="activeZoneATab = 'explorer'" class="px-3 py-2 text-sm font-semibold border-b-2 transition-colors focus:outline-none" :class="activeZoneATab === 'explorer' ? 'border-purple-500 text-purple-400' : 'border-transparent text-gray-400 hover:text-gray-300'">Swarm File Explorer</button>
            </div>
        </div>

        <div class="p-5 flex-1 overflow-y-auto">
            <div x-show="activeZoneATab === 'compute'" x-transition>
            <!-- Global Stats -->
            <div class="grid grid-cols-3 gap-4 mb-6">
                <div class="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4">
                    <div class="text-xs text-gray-400 mb-1">Grid CPU Load</div>
                    <div class="text-2xl font-mono text-purple-400" x-text="metrics.system_cpu + '%'">--%</div>
                </div>
                <div class="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4">
                    <div class="text-xs text-gray-400 mb-1">Available Memory Map</div>
                    <div class="text-2xl font-mono text-blue-400"><span x-text="metrics.free_ram"></span><span class="text-sm text-gray-500 ml-1">MB</span></div>
                </div>
                <div class="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4">
                    <div class="text-xs text-gray-400 mb-1">System Clock</div>
                    <div class="text-2xl font-mono text-gray-300" x-text="metrics.timestamp">--:--:--</div>
                </div>
            </div>
            
            <!-- Unified Memory Stats -->
            <h2 class="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wider flex items-center gap-2">
                <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                Unified Vector Memory
            </h2>
            <div class="grid grid-cols-3 gap-4 mb-6">
                <div class="bg-gray-950 border border-gray-800 rounded-lg p-4">
                    <div class="text-xs text-gray-400 mb-1">Local Index Size</div>
                    <div class="text-xl font-mono text-gray-300"><span x-text="metrics.local_vector_size"></span> <span class="text-[10px] text-gray-500 uppercase">Shards</span></div>
                </div>
                <div class="bg-gray-950 border border-gray-800 rounded-lg p-4">
                    <div class="text-xs text-gray-400 mb-1">Swarm Pool Size</div>
                    <div class="text-xl font-mono text-emerald-400"><span x-text="metrics.swarm_pool_size"></span> <span class="text-[10px] text-gray-500 uppercase">Shards</span></div>
                </div>
                <div class="bg-gray-950 border border-gray-800 rounded-lg p-4">
                    <div class="text-xs text-gray-400 mb-1">Active Memory Nodes</div>
                    <div class="text-xl font-mono text-blue-400" x-text="metrics.active_memory_nodes"></div>
                </div>
            </div>

            <!-- Peer Table -->
            <h2 class="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wider">Worker Nodes</h2>
            <div class="bg-gray-950 border border-gray-800 rounded-lg overflow-hidden">
                <table class="w-full text-left text-sm">
                    <thead class="bg-gray-900 border-b border-gray-800 text-xs text-gray-400">
                        <tr>
                            <th class="p-3 font-medium">Node ID</th>
                            <th class="p-3 font-medium">Memory DHT</th>
                            <th class="p-3 font-medium">VRAM</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-800/50">
                        <template x-for="peer in metrics.peers" :key="peer.id">
                            <tr class="hover:bg-gray-800/30 transition-colors">
                                <td class="p-3 font-mono text-gray-300" x-text="peer.id"></td>
                                <td class="p-3">
                                    <span x-show="peer.shares_memory" class="px-2 py-0.5 rounded bg-blue-900/30 border border-blue-700/50 text-blue-400 text-[10px] uppercase font-bold tracking-wider">Sharing</span>
                                    <span x-show="!peer.shares_memory" class="px-2 py-0.5 rounded bg-gray-900/50 border border-gray-700/50 text-gray-500 text-[10px] uppercase font-bold tracking-wider">Isolated</span>
                                </td>
                                <td class="p-3 text-gray-300 font-mono text-xs" x-text="Math.round(peer.ram/1024) + 'GB'"></td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>

            <!-- Shard Visualizer -->
            <h2 class="text-sm font-semibold text-gray-300 mt-8 mb-3 uppercase tracking-wider">Background Shard Health</h2>
            <div class="bg-gray-950 border border-gray-800 rounded-lg p-4">
                <div class="shard-grid">
                    <template x-for="i in 100">
                        <div class="shard-block" :class="(Math.random() * 100 < metrics.system_cpu) ? 'shard-active' : 'shard-inactive'"></div>
                    </template>
                </div>
            </div>
            </div>
            
            <!-- SWARM FILE EXPLORER TAB -->
            <div x-show="activeZoneATab === 'explorer'" style="display: none;" x-transition>
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-sm font-semibold text-gray-300 uppercase tracking-wider">Distributed Seed Vault</h2>
                    
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-semibold text-gray-500">Filter:</span>
                        <select x-model="explorerFilter" class="bg-gray-900 border border-gray-700 rounded-lg text-xs text-white p-1.5 focus:outline-none focus:border-purple-500">
                            <option value="all">All Files</option>
                            <option value="pmem">.pmem Memory Packs</option>
                            <option value="raw">Raw Files</option>
                        </select>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 gap-3">
                    <template x-for="f in filteredExplorerFiles" :key="f.id">
                        <div class="bg-gray-950 border border-gray-800 rounded-lg p-3 flex flex-col gap-2 hover:border-gray-700 transition">
                            <div class="flex justify-between items-start">
                                <div class="flex items-center gap-2">
                                    <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                                    <span class="text-sm font-semibold text-gray-200" x-text="f.name"></span>
                                    <span x-show="f.is_pmem" class="px-1.5 py-0.5 rounded bg-blue-900/30 text-blue-400 text-[10px] uppercase font-bold tracking-wider border border-blue-700/50">Vector</span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <span class="text-xs text-gray-500 font-mono" x-text="f.size_kb + ' KB'"></span>
                                </div>
                            </div>
                            
                            <div class="flex justify-between items-end mt-1">
                                <div class="flex items-center gap-4">
                                    <div class="text-[10px] text-gray-400 uppercase tracking-widest font-semibold">
                                        Status: 
                                        <span :class="f.state === 'Local' ? 'text-gray-400' : (f.state === 'Swarm' ? 'text-emerald-400' : 'text-blue-400')" x-text="f.state"></span>
                                    </div>
                                    <div class="text-[10px] text-gray-400 uppercase tracking-widest font-semibold flex items-center gap-1">
                                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                                        <span x-text="f.shards + ' shards'"></span>
                                    </div>
                                </div>
                                <div class="flex gap-2">
                                    <button @click="inspectShards(f.id, f.name)" class="px-2 py-1 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded text-[10px] text-gray-300 font-semibold uppercase tracking-wider transition">Inspect Shards</button>
                                    <button @click="toggleSeedState(f.id)" class="px-2 py-1 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded text-[10px] text-gray-300 font-semibold uppercase tracking-wider transition" x-text="f.state === 'Local' ? 'Split to Seeds' : 'Toggle Seeding'"></button>
                                    <button @click="deleteFile(f.id)" class="px-2 py-1 bg-red-900/30 hover:bg-red-900/50 border border-red-700/50 rounded text-[10px] text-red-400 font-semibold uppercase tracking-wider transition">Delete</button>
                                </div>
                            </div>
                        </div>
                    </template>
                    <div x-show="filteredExplorerFiles.length === 0" class="text-sm text-gray-500 italic p-4 text-center border border-gray-800 border-dashed rounded-lg">
                        No files found. Seed a local file to populate the mesh vault.
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ZONE B: Gemini AI Stream (Client Interface) -->
    <div class="w-1/2 h-full flex flex-col bg-gray-950 relative">
        <div class="p-4 border-b border-gray-800 bg-gray-950/80 backdrop-blur-md flex justify-between items-center z-20">
            <div>
                <h1 class="text-lg font-bold text-white flex items-center gap-2">
                    Client Interface
                </h1>
            </div>
            
            <div class="flex items-center gap-3">
                <!-- Unified Memory Settings Button -->
                <button @click="showMemoryModal = true" class="flex items-center gap-2 bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 hover:bg-gray-800 transition shadow-sm" :class="memoryLevel === 'Isolated' ? 'text-gray-400' : 'text-blue-400 border-blue-800/50'">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                    <span class="text-xs font-semibold" x-text="memoryLevel"></span>
                </button>
                
                <div class="w-px h-6 bg-gray-800"></div>
                
                <!-- Model Connectors Button -->
                <button @click="showConnectorsModal = true" class="flex items-center gap-2 bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 hover:bg-gray-800 transition shadow-sm text-emerald-400 border-emerald-800/50" title="API Connectors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    <span class="text-xs font-semibold">Connectors</span>
                </button>

                <!-- LOCAL PERSONA MANAGER -->
                <div class="flex items-center gap-2 bg-gray-900 border border-gray-700 rounded-lg px-2 py-1">
                    <span class="text-xl" x-text="activePersona?.avatar"></span>
                    <select x-model="activePersonaId" @change="switchPersona()" class="bg-transparent text-sm text-gray-200 font-semibold outline-none border-none focus:ring-0 w-36">
                        <template x-for="p in personas" :key="p.id">
                            <option :value="p.id" x-text="p.name" class="bg-gray-900"></option>
                        </template>
                    </select>
                </div>
                <button @click="showPersonaModal = true" class="p-1.5 rounded bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 transition" title="New Persona">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                </button>
            </div>
        </div>
        
        <div class="bg-purple-900/20 border-b border-purple-900/50 px-4 py-2 flex items-center gap-2">
            <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span class="text-xs text-purple-300 font-mono truncate">Local System Prompt: <span x-text="activePersona?.sysPrompt"></span></span>
        </div>

        <div id="chat-container" class="flex-1 overflow-y-auto p-6 space-y-6 pb-32">
            <template x-for="(msg, index) in chatHistory" :key="index">
                <div class="flex gap-4" :class="msg.role === 'user' ? 'flex-row-reverse' : ''">
                    <div class="w-8 h-8 rounded border flex items-center justify-center shrink-0 text-xl" 
                         :class="msg.role === 'system' ? 'bg-blue-900/30 border-blue-700/50 text-blue-400 text-sm' : msg.role === 'user' ? 'bg-gray-800 border-gray-700' : 'bg-gray-800 border-gray-700'"
                         x-html="msg.avatar"></div>
                    
                    <div class="flex-1" :class="msg.role === 'user' ? 'max-w-[80%]' : ''">
                        <template x-if="msg.role === 'ai' && msg.peer">
                            <div class="text-[10px] font-mono text-purple-400 mb-1 flex items-center gap-1 uppercase tracking-widest">
                                <span class="relative flex h-1.5 w-1.5 mr-1"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span><span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-purple-500"></span></span>
                                Executed by <span x-text="msg.peer"></span>
                            </div>
                        </template>

                        <div :class="msg.role === 'user' ? 'bg-gray-800 border border-gray-700 rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm text-gray-200' : (msg.role === 'system' ? 'text-blue-400 font-mono text-xs mt-2' : 'prose prose-invert max-w-none text-sm text-gray-300')">
                            <template x-if="msg.role === 'user' || msg.role === 'system'">
                                <span x-html="msg.raw"></span>
                            </template>
                            <template x-if="msg.role === 'ai'">
                                <div x-html="msg.html" :class="msg.isTyping ? 'cursor' : ''"></div>
                            </template>
                        </div>
                    </div>
                </div>
            </template>
        </div>

        <div class="absolute bottom-0 w-full p-6 bg-gradient-to-t from-gray-950 via-gray-950 to-transparent">
            <form @submit.prevent="sendPrompt()" class="relative max-w-3xl mx-auto flex items-end gap-2 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl p-2 transition-all focus-within:border-purple-500/50 focus-within:ring-1 focus-within:ring-purple-500/50">
                <textarea x-model="inputText" @keydown.enter.prevent="if(!$event.shiftKey) sendPrompt()" :disabled="isProcessing" rows="1" class="w-full bg-transparent border-0 text-sm text-gray-100 placeholder-gray-500 focus:ring-0 resize-none py-3 px-3 max-h-32 disabled:opacity-50" placeholder="Ask your local persona anything..."></textarea>
                <button type="submit" :disabled="isProcessing" class="p-3 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 text-white transition-colors shrink-0 mb-0.5 mr-0.5 shadow-lg">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"></path></svg>
                </button>
            </form>
        </div>
    </div>

    <script>
        function meshApp() {
            return {
                ws: null,
                teamWs: null,
                metrics: { cpu: 0, free_ram: 0, peers: [], timestamp: '--:--:--', local_vector_size: 0, active_memory_nodes: 0, swarm_pool_size: 0 },
                personas: [],
                activePersonaId: null,
                activePersona: null,
                showPersonaModal: false,
                showMemoryModal: false,
                showTeamDashboard: false,
                showConnectorsModal: false,
                showSeedModal: false,
                selectedFile: null,
                fileContent: '',
                isSeeding: false,
                seederProgress: 0,
                seededFiles: [],
                connectorConfig: { provider: 'openai', apiKey: '', hybridFallback: false, webhookUrl: '' },
                webhookTestResult: '',
                memoryLevel: 'Isolated',
                newPersona: { name: '', sysPrompt: '', temp: 0.7, avatar: '👤' },
                inputText: '',
                chatHistory: [],
                isProcessing: false,

                activeTeamId: null,
                activeTeamName: '',
                newTeamName: '',
                joinTeamHash: '',
                teamVault: {},
                teamEvents: [],
                vaultKey: '',
                vaultValue: '',
                isFederated: false,
                federatedProgress: 0,
                
                activeZoneATab: 'compute',
                explorerFiles: [],
                explorerFilter: 'all',
                showShardModal: false,
                activeShardFile: null,
                activeShardBlocks: [],
                
                get filteredExplorerFiles() {
                    if (this.explorerFilter === 'all') return this.explorerFiles;
                    if (this.explorerFilter === 'pmem') return this.explorerFiles.filter(f => f.is_pmem);
                    return this.explorerFiles.filter(f => !f.is_pmem);
                },
                
                async fetchExplorerFiles() {
                    try {
                        const res = await fetch('/api/explorer/files');
                        this.explorerFiles = await res.json();
                    } catch(e) {}
                },
                async inspectShards(file_id, file_name) {
                    try {
                        const res = await fetch(`/api/explorer/shards/${file_id}`);
                        this.activeShardBlocks = await res.json();
                        this.activeShardFile = { id: file_id, name: file_name };
                        this.showShardModal = true;
                    } catch(e) {}
                },
                async toggleSeedState(file_id) {
                    try {
                        await fetch('/api/explorer/action', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ file_id, action: 'toggle_seed' })
                        });
                        await this.fetchExplorerFiles();
                    } catch(e) {}
                },
                async deleteFile(file_id) {
                    try {
                        await fetch('/api/explorer/action', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ file_id, action: 'delete' })
                        });
                        await this.fetchExplorerFiles();
                    } catch(e) {}
                },
                
                async initApp() {
                    const storedP = localStorage.getItem('local_mesh_personas');
                    if (storedP) {
                        this.personas = JSON.parse(storedP);
                    } else {
                        this.personas = [
                            { id: 1, name: 'Default Assistant', sysPrompt: 'You are a helpful AI.', temp: 0.5, avatar: '🤖' }
                        ];
                        localStorage.setItem('local_mesh_personas', JSON.stringify(this.personas));
                    }
                    this.activePersonaId = this.personas[0].id;
                    this.switchPersona();
                    
                    const storedMem = localStorage.getItem('local_memory_level');
                    if (storedMem) this.memoryLevel = storedMem;
                    
                    const storedConn = localStorage.getItem('local_connector_config');
                    if (storedConn) {
                        try {
                            this.connectorConfig = JSON.parse(storedConn);
                        } catch(e) {}
                    }
                    
                    // Sync initial memory state with backend
                    await this.syncMemoryState();

                    this.chatHistory.push({
                        role: 'ai', raw: '', html: '<p>Client initialized. Personas are securely isolated in local storage.</p>', avatar: '🌐', isTyping: false
                    });

                    this.connectWs();
                },
                
                async syncMemoryState() {
                    try {
                        await fetch('/api/memory/toggle', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ level: this.memoryLevel })
                        });
                    } catch(e) {}
                },

                async saveMemoryLevel() {
                    localStorage.setItem('local_memory_level', this.memoryLevel);
                    await this.syncMemoryState();
                    this.showMemoryModal = false;
                    
                    // Add system message to indicate privacy choice
                    this.chatHistory.push({
                        role: 'system', raw: `Memory setting updated to <strong>${this.memoryLevel}</strong>.`, avatar: '🔒', isTyping: false
                    });
                    this.scrollToBottom();
                },
                
                switchPersona() {
                    this.activePersona = this.personas.find(p => p.id == this.activePersonaId) || this.personas[0];
                },
                
                savePersona() {
                    if(!this.newPersona.name) return;
                    const p = { ...this.newPersona, id: Date.now() };
                    this.personas.push(p);
                    localStorage.setItem('local_mesh_personas', JSON.stringify(this.personas));
                    this.activePersonaId = p.id;
                    this.switchPersona();
                    this.showPersonaModal = false;
                    this.newPersona = { name: '', sysPrompt: '', temp: 0.7, avatar: '👤' };
                },

                async saveConnectorConfig() {
                    localStorage.setItem('local_connector_config', JSON.stringify(this.connectorConfig));
                    try {
                        await fetch('/api/connectors/config', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                provider: this.connectorConfig.provider,
                                api_key: "LOCAL_ENCRYPTED",
                                hybrid_fallback: this.connectorConfig.hybridFallback,
                                webhook_url: this.connectorConfig.webhookUrl
                            })
                        });
                    } catch(e) {}
                    
                    this.showConnectorsModal = false;
                    this.chatHistory.push({
                        role: 'system', raw: `Secure connector gateway updated. Hybrid fallback is <strong class="${this.connectorConfig.hybridFallback ? 'text-emerald-400' : 'text-gray-400'}">${this.connectorConfig.hybridFallback ? 'ENABLED' : 'DISABLED'}</strong>.`, avatar: '⚡', isTyping: false
                    });
                    this.scrollToBottom();
                },

                async testWebhook() {
                    if (!this.connectorConfig.webhookUrl) return;
                    this.webhookTestResult = "Pinging...";
                    try {
                        const res = await fetch('/api/connectors/test-hook', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ url: this.connectorConfig.webhookUrl })
                        });
                        const data = await res.json();
                        this.webhookTestResult = data.message;
                    } catch(e) {
                        this.webhookTestResult = "Connection failed.";
                    }
                    setTimeout(() => this.webhookTestResult = '', 3000);
                },

                handleFileSelect(event) {
                    const file = event.target.files[0];
                    if (!file) return;
                    this.selectedFile = file;
                    this.seederProgress = 0;
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        this.fileContent = e.target.result;
                    };
                    reader.readAsText(file);
                },

                async seedFileToMesh() {
                    if (!this.selectedFile || !this.fileContent || this.isSeeding) return;
                    this.isSeeding = true;
                    this.seederProgress = 10;
                    
                    // Simulate cryptographic fragmentation
                    const interval = setInterval(() => {
                        this.seederProgress += Math.random() * 20;
                        if (this.seederProgress >= 95) {
                            clearInterval(interval);
                            this.finalizeSeeding();
                        }
                    }, 300);
                },

                async finalizeSeeding() {
                    try {
                        const res = await fetch('/api/explorer/split', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                filename: this.selectedFile.name,
                                content: this.fileContent,
                                team_id: this.activeTeamId
                            })
                        });
                        const data = await res.json();
                        if (data.status === 'success') {
                            this.seederProgress = 100;
                            this.seededFiles.push({ name: data.filename, shards: data.shards });
                            this.fetchExplorerFiles();
                            this.activeZoneATab = 'explorer';
                            if (this.activeTeamId) {
                                this.addTeamEvent(`Seeded ${data.filename} into shared vault.`);
                            }
                            this.chatHistory.push({
                                role: 'system', raw: `Distributed file \`${data.filename}\` securely into the mesh (.pmem virtual vault).`, avatar: '📦', isTyping: false
                            });
                            this.scrollToBottom();
                        }
                    } catch(e) {}
                    
                    setTimeout(() => {
                        this.isSeeding = false;
                        this.seederProgress = 0;
                        this.selectedFile = null;
                        this.fileContent = '';
                    }, 1000);
                },

                async createTeam() {
                    if (!this.newTeamName) return;
                    const res = await fetch('/api/teams/create', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: this.newTeamName })
                    });
                    const data = await res.json();
                    if (data.status === 'success') {
                        this.activeTeamId = data.team_id;
                        this.activeTeamName = data.name;
                        this.connectTeamWs();
                        this.addTeamEvent(`Swarm created: ${this.activeTeamName}`);
                    }
                },

                async joinTeam() {
                    if (!this.joinTeamHash) return;
                    const res = await fetch('/api/teams/join', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ hash_id: this.joinTeamHash })
                    });
                    const data = await res.json();
                    if (data.status === 'success') {
                        this.activeTeamId = data.team_id;
                        this.activeTeamName = data.name;
                        this.connectTeamWs();
                        this.addTeamEvent(`Joined Swarm: ${this.activeTeamName}`);
                    } else {
                        alert("Invalid Swarm Hash");
                    }
                },

                leaveTeam() {
                    if (this.teamWs) this.teamWs.close();
                    this.activeTeamId = null;
                    this.activeTeamName = '';
                    this.teamEvents = [];
                    this.teamVault = {};
                },

                connectTeamWs() {
                    if (this.teamWs) this.teamWs.close();
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    this.teamWs = new WebSocket(`${protocol}//${window.location.host}/ws/team/${this.activeTeamId}`);
                    this.teamWs.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        if (data.type === 'team_event') {
                            this.addTeamEvent(data.event);
                            if (data.event.includes('Federated sharding active')) {
                                this.federateProgressSim();
                            }
                        }
                        else if (data.type === 'pmem_sync') {
                            this.teamVault = data.vault;
                            this.addTeamEvent('Vault synchronized from swarm.');
                        }
                    };
                },

                syncToVault() {
                    if (!this.vaultKey || !this.vaultValue || !this.teamWs) return;
                    this.teamVault[this.vaultKey] = this.vaultValue;
                    this.teamWs.send(JSON.stringify({
                        action: 'pmem_sync',
                        key: this.vaultKey,
                        value: this.vaultValue
                    }));
                    this.addTeamEvent(`Pushed to vault: [${this.vaultKey}]`);
                    this.vaultKey = '';
                    this.vaultValue = '';
                },

                addTeamEvent(msg) {
                    this.teamEvents.unshift(msg);
                    if (this.teamEvents.length > 50) this.teamEvents.pop();
                },

                federateProgressSim() {
                    this.federatedProgress = 10;
                    const interval = setInterval(() => {
                        this.federatedProgress += Math.random() * 20;
                        if (this.federatedProgress >= 100) {
                            this.federatedProgress = 100;
                            clearInterval(interval);
                            setTimeout(() => { this.federatedProgress = 0; }, 1500);
                        }
                    }, 500);
                },

                connectWs() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/metrics`);
                    this.ws.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        if (data.type === 'metrics') this.metrics = data;
                        else if (data.type === 'token') this.handleToken(data);
                    };
                    this.ws.onclose = () => setTimeout(() => this.connectWs(), 2000);
                },

                async sendPrompt() {
                    if (!this.inputText.trim() || this.isProcessing) return;
                    this.isProcessing = true;
                    
                    const promptText = this.inputText;
                    this.inputText = '';
                    
                    this.chatHistory.push({ role: 'user', raw: promptText, html: '', avatar: '🧑‍💻' });
                    this.scrollToBottom();

                    let memoryContextStr = "";

                    // Unified Memory Retrieval / Local Embedding Check
                    if (this.memoryLevel !== "Isolated") {
                        this.chatHistory.push({
                            role: 'system', raw: `Embedding local vectors & querying DHT swarm...`, avatar: '🔍', isTyping: false
                        });
                        this.scrollToBottom();
                        
                        try {
                            const res = await fetch('/api/memory/query', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ query: promptText, level: this.memoryLevel })
                            });
                            const memData = await res.json();
                            
                            if (memData.status === "contributed") {
                                this.chatHistory.push({
                                    role: 'system', raw: `Vectors anonymized and seeded. No external query made (Contributor Mode).`, avatar: '✅', isTyping: false
                                });
                            } else if (memData.status === "success") {
                                memoryContextStr = memData.context_injected;
                                this.chatHistory.push({
                                    role: 'system', raw: `Retrieved ${memData.retrieved} fragments from ${memData.nodes_accessed} DHT nodes. Vector prefix: <code>${memData.vector_preview}</code>`, avatar: '🧠', isTyping: false
                                });
                            }
                        } catch(e) {}
                        this.scrollToBottom();
                    }

                    // Prepare AI Message Slot
                    this.chatHistory.push({ role: 'ai', raw: '', html: '', peer: 'Routing...', avatar: this.activePersona.avatar, isTyping: true });
                    
                    if (this.isFederated && this.activeTeamId) {
                        this.addTeamEvent(`Dispatching prompt payload to federated swarm...`);
                        this.federateProgressSim();
                    }

                    // Bundle payload to Mesh
                    const payload = {
                        action: 'compute_task',
                        prompt: promptText,
                        system_prompt: this.activePersona.sysPrompt,
                        temperature: this.activePersona.temp,
                        memory_context: memoryContextStr,
                        team_id: this.activeTeamId,
                        is_federated: this.isFederated,
                        is_hybrid: this.connectorConfig.hybridFallback,
                        api_key: this.connectorConfig.apiKey
                    };
                    
                    this.ws.send(JSON.stringify(payload));
                    this.scrollToBottom();
                },
                
                handleToken(data) {
                    let lastMsg = this.chatHistory[this.chatHistory.length - 1];
                    if (lastMsg && lastMsg.role === 'ai') {
                        lastMsg.raw += data.text;
                        lastMsg.html = marked.parse(lastMsg.raw);
                        lastMsg.peer = data.peer;
                        
                        if (data.is_final) {
                            lastMsg.isTyping = false;
                            this.isProcessing = false;
                        }
                        this.scrollToBottom();
                    }
                },
                
                scrollToBottom() {
                    setTimeout(() => {
                        const container = document.getElementById('chat-container');
                        if(container) container.scrollTop = container.scrollHeight;
                    }, 50);
                }
            }
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("=====================================================")
    print(" Starting Local Persona & Unified Memory Mesh UI")
    print(" Ensure dependencies are installed:")
    print("   pip install fastapi uvicorn websockets pydantic")
    print("=====================================================")
    uvicorn.run("mesh_gui:app", host="0.0.0.0", port=8080, reload=True)
