import re

with open("mesh_gui.py", "r") as f:
    content = f.read()

# Add to state
state_search = """                isFederated: false,
                federatedProgress: 0,"""

state_replace = """                isFederated: false,
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
                },"""

content = content.replace(state_search, state_replace)

init_search = """                    // Connect WebSocket
                    this.connectWebSocket();"""

init_replace = """                    // Connect WebSocket
                    this.connectWebSocket();
                    
                    this.fetchExplorerFiles();
                    setInterval(() => {
                        if (this.activeZoneATab === 'explorer') {
                            this.fetchExplorerFiles();
                        }
                    }, 2000);"""
                    
content = content.replace(init_search, init_replace)

finalize_seeding_search = """                        const res = await fetch('/api/pmem/seed', {"""
finalize_seeding_replace = """                        const res = await fetch('/api/explorer/split', {"""
content = content.replace(finalize_seeding_search, finalize_seeding_replace)

finalize_seeding_success_search = """                        if (data.status === 'success') {
                            this.seederProgress = 100;
                            this.seededFiles.push({ name: data.filename, shards: data.shards });"""
finalize_seeding_success_replace = """                        if (data.status === 'success') {
                            this.seederProgress = 100;
                            this.seededFiles.push({ name: data.filename, shards: data.shards });
                            this.fetchExplorerFiles();
                            this.activeZoneATab = 'explorer';"""
content = content.replace(finalize_seeding_success_search, finalize_seeding_success_replace)


with open("mesh_gui.py", "w") as f:
    f.write(content)
