import re

with open("mesh_gui.py", "r") as f:
    content = f.read()

# Replace header
header_start = """        <div class="p-5 border-b border-gray-800 bg-gray-950/50 backdrop-blur-md flex justify-between items-start">
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

        <div class="p-5 flex-1 overflow-y-auto">"""

header_end = """        <div class="px-5 pt-5 pb-0 border-b border-gray-800 bg-gray-950/50 backdrop-blur-md flex flex-col gap-4">
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
            <div x-show="activeZoneATab === 'compute'" x-transition>"""

content = content.replace(header_start, header_end)


footer_start = """            <!-- Shard Visualizer -->
            <h2 class="text-sm font-semibold text-gray-300 mt-8 mb-3 uppercase tracking-wider">Background Shard Health</h2>
            <div class="bg-gray-950 border border-gray-800 rounded-lg p-4">
                <div class="shard-grid">
                    <template x-for="i in 100">
                        <div class="shard-block" :class="(Math.random() * 100 < metrics.system_cpu) ? 'shard-active' : 'shard-inactive'"></div>
                    </template>
                </div>
            </div>
        </div>
    </div>"""

footer_end = """            <!-- Shard Visualizer -->
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
                                    <button @click="toggleSeedState(f.id)" class="px-2 py-1 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded text-[10px] text-gray-300 font-semibold uppercase tracking-wider transition">Toggle Seed</button>
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
    </div>"""

content = content.replace(footer_start, footer_end)

with open("mesh_gui.py", "w") as f:
    f.write(content)
