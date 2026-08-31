import re

with open("mesh_gui.py", "r") as f:
    content = f.read()

shard_modal = """
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
"""

insert_point = "    <!-- MODAL: Seed Local File (.pmem) -->"

content = content.replace(insert_point, shard_modal + "\n" + insert_point)

with open("mesh_gui.py", "w") as f:
    f.write(content)
