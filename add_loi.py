import re

with open("mesh_gui.py", "r") as f:
    content = f.read()

# 1. Imports
imports = """from dataclasses import dataclass, field
import time
import math
import asyncio
import uuid"""

content = content.replace("import asyncio", imports)

# 2. MemoryBlock data class
dataclass_str = """
@dataclass
class MemoryBlock:
    id: str
    cid: str
    content: str
    base_importance: float
    importance_score: float = 0.0
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    tier: str = "Active Quests"
    locked: bool = False
    
    def recalculate(self):
        if self.locked:
            self.importance_score = 100.0
            self.tier = "Legendary Core"
            return
            
        t = (time.time() - self.last_accessed) / 60.0  # minutes
        decay_coeff = 0.05
        boost_factor = 2.0
        
        self.importance_score = (self.base_importance + (self.access_count * boost_factor)) * math.exp(-decay_coeff * t)
        
        if self.importance_score >= 80.0:
            self.tier = "Legendary Core"
        elif self.importance_score >= 30.0:
            self.tier = "Active Quests"
        else:
            self.tier = "Dormant Archives"

class MeshSimulator:"""

content = content.replace("class MeshSimulator:", dataclass_str)


# 3. Add to MeshSimulator init
init_str = """        self.explorer_files = {}"""
init_repl = """        self.explorer_files = {}
        self.memory_journal = {}
        self._add_memory("The user is developing a distributed mesh network.", 85.0)
        self._add_memory("API keys must be securely stored in the local vault.", 45.0)
        self._add_memory("Initial prototype completed in 2024.", 15.0)"""
content = content.replace(init_str, init_repl)

# 4. _add_memory method
add_mem_str = """        self.local_vector_index = random.randint(100, 500)

    def _add_memory(self, content: str, base: float):
        m_id = str(uuid.uuid4())[:8]
        cid = f"ipfs://Qm{hashlib.sha256(content.encode()).hexdigest()[:40]}"
        self.memory_journal[m_id] = MemoryBlock(
            id=m_id, cid=cid, content=content, base_importance=base, 
            importance_score=base, last_accessed=time.time()
        )
        self.memory_journal[m_id].recalculate()

    def get_network_state(self):"""
content = content.replace("        self.local_vector_index = random.randint(100, 500)\n\n    def get_network_state(self):", add_mem_str)


# 5. Inject memory check into compute task
compute_str = """        webhook_context = ""
        if self.webhook_queue:
            webhook_context = "\\n".join(self.webhook_queue)
            self.webhook_queue.clear()"""

compute_repl = """        webhook_context = ""
        if self.webhook_queue:
            webhook_context = "\\n".join(self.webhook_queue)
            self.webhook_queue.clear()
            
        relevant_memories = []
        for m in self.memory_journal.values():
            if any(word.lower() in m.content.lower() for word in prompt.split()) or m.tier == "Legendary Core":
                m.access_count += 1
                m.last_accessed = time.time()
                m.recalculate()
                relevant_memories.append(m.content)
                
        if relevant_memories:
            webhook_context += "\\n[Journal Log Retrieved]: " + " | ".join(relevant_memories)"""
content = content.replace(compute_str, compute_repl)

# 6. Add FastAPI routes for Journal
fastapi_routes = """@app.post("/api/memory/toggle")"""
journal_routes = """class JournalAction(BaseModel):
    id: str
    action: str

class NewMemory(BaseModel):
    content: str
    base_importance: float = 50.0

@app.get("/api/journal")
async def get_journal():
    return [
        {
            "id": m.id,
            "cid": m.cid,
            "content": m.content,
            "score": round(m.importance_score, 1),
            "tier": m.tier,
            "locked": m.locked,
            "accesses": m.access_count
        } for m in simulator.memory_journal.values()
    ]

@app.post("/api/journal/action")
async def journal_action(req: JournalAction):
    if req.id in simulator.memory_journal:
        mem = simulator.memory_journal[req.id]
        if req.action == "toggle_lock":
            mem.locked = not mem.locked
            mem.recalculate()
        elif req.action == "access":
            mem.access_count += 1
            mem.last_accessed = time.time()
            mem.recalculate()
        return {"status": "success"}
    return {"status": "error"}

@app.post("/api/journal/add")
async def add_journal(req: NewMemory):
    simulator._add_memory(req.content, req.base_importance)
    return {"status": "success"}

@app.post("/api/memory/toggle")"""
content = content.replace(fastapi_routes, journal_routes)

# 7. Add journal_loop to startup
broadcaster_str = """    broadcaster_task = asyncio.create_task(metrics_broadcaster())"""
broadcaster_repl = """    broadcaster_task = asyncio.create_task(metrics_broadcaster())
    
    async def journal_updater():
        try:
            while True:
                for mem in simulator.memory_journal.values():
                    mem.recalculate()
                await asyncio.sleep(5)
        except WebSocketDisconnect:
            pass
    journal_task = asyncio.create_task(journal_updater())"""
content = content.replace(broadcaster_str, broadcaster_repl)

cancel_str = """    except WebSocketDisconnect:
        broadcaster_task.cancel()"""
cancel_repl = """    except WebSocketDisconnect:
        broadcaster_task.cancel()
        journal_task.cancel()"""
content = content.replace(cancel_str, cancel_repl)

with open("mesh_gui.py", "w") as f:
    f.write(content)
