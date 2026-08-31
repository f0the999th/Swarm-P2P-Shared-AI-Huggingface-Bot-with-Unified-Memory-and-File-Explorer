import re

with open("mesh_gui.py", "r") as f:
    content = f.read()

# Add explorer_files to MeshSimulator
init_str = """        self.peers = []
        self.teams = {}
        self.webhook_queue = []"""
init_replace = """        self.peers = []
        self.teams = {}
        self.webhook_queue = []
        self.explorer_files = {}"""
content = content.replace(init_str, init_replace)

routes_str = """@app.post("/api/pmem/seed")"""

routes_add = """class ExplorerSplitPayload(BaseModel):
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

@app.post("/api/pmem/seed")"""

content = content.replace(routes_str, routes_add)

with open("mesh_gui.py", "w") as f:
    f.write(content)
