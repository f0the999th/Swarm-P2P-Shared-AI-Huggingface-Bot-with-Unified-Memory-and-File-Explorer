import re

with open("mesh_gui.py", "r") as f:
    content = f.read()

journal_pane = """
            <!-- MEMORY JOURNAL TAB -->
            <div x-show="activeZoneATab === 'journal'" style="display: none;" x-transition>
                <div class="flex justify-between items-center mb-4 border-b border-amber-900/30 pb-3">
                    <div>
                        <h2 class="text-lg font-serif italic text-amber-500 tracking-wide">Cognitive Quest Log</h2>
                        <p class="text-[10px] text-amber-700/70 uppercase tracking-widest font-semibold mt-0.5">Level-of-Importance (LoI) Engine</p>
                    </div>
                    <button @click="addJournalEntry()" class="px-3 py-1.5 border border-amber-700/50 hover:bg-amber-900/30 text-amber-500 text-xs font-serif rounded transition flex items-center gap-2 shadow-[0_0_10px_rgba(217,119,6,0.1)]">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                        Scribe Memory
                    </button>
                </div>
                
                <div class="space-y-6 overflow-y-auto pr-2 pb-10">
                    <!-- Categories -->
                    <template x-for="tier in ['Legendary Core', 'Active Quests', 'Dormant Archives']" :key="tier">
                        <div x-show="journalMemories.filter(m => m.tier === tier).length > 0">
                            <h3 class="text-sm font-serif italic text-gray-400 border-b border-gray-800 pb-1 mb-3 flex items-center gap-2">
                                <span x-text="tier" :class="tier === 'Legendary Core' ? 'text-amber-500' : (tier === 'Active Quests' ? 'text-emerald-500' : 'text-gray-500')"></span>
                                <span class="text-[10px] bg-gray-900 px-1.5 py-0.5 rounded text-gray-500" x-text="journalMemories.filter(m => m.tier === tier).length"></span>
                            </h3>
                            <div class="grid grid-cols-1 gap-3">
                                <template x-for="mem in journalMemories.filter(m => m.tier === tier)" :key="mem.id">
                                    <div class="bg-gray-900/80 border rounded-sm p-3 relative group transition duration-300" 
                                         :class="mem.locked ? 'border-amber-700/50 shadow-[0_0_8px_rgba(217,119,6,0.1)]' : 'border-gray-800 hover:border-gray-600'">
                                         
                                        <div class="flex justify-between items-start mb-2">
                                            <div class="flex items-center gap-2 text-[10px] text-gray-500 font-mono bg-gray-950 px-2 py-0.5 rounded">
                                                <svg class="w-3 h-3 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                                                <span x-text="mem.cid"></span>
                                            </div>
                                            <button @click="toggleJournalLock(mem.id)" class="text-gray-500 hover:text-amber-500 transition focus:outline-none" :class="mem.locked ? 'text-amber-500' : ''" title="Pin / Lock Importance">
                                                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z"></path></svg>
                                            </button>
                                        </div>
                                        
                                        <p class="text-sm text-gray-300 font-serif leading-relaxed mb-3" x-text="mem.content"></p>
                                        
                                        <div class="flex items-center gap-3">
                                            <div class="flex-1">
                                                <div class="flex justify-between text-[10px] text-gray-500 uppercase tracking-widest mb-1">
                                                    <span>LoI Score</span>
                                                    <span x-text="Math.round(mem.score)"></span>
                                                </div>
                                                <div class="h-1 w-full bg-gray-950 rounded-full overflow-hidden">
                                                    <div class="h-full transition-all duration-1000 ease-out" 
                                                         :class="mem.score > 80 ? 'bg-amber-500' : (mem.score > 30 ? 'bg-emerald-500' : 'bg-gray-600')"
                                                         :style="`width: ${Math.min(100, mem.score)}%`"></div>
                                                </div>
                                            </div>
                                            <div class="text-[10px] text-gray-500 flex flex-col items-end">
                                                <span>Access: <span class="text-gray-300 font-mono" x-text="mem.accesses"></span></span>
                                            </div>
                                        </div>
                                        
                                    </div>
                                </template>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </div>
"""

pane_str = """            </div>
        </div>
    </div>

    <!-- ZONE B: Gemini AI Stream (Client Interface) -->"""
pane_repl = """            </div>""" + journal_pane + """
    <!-- ZONE B: Gemini AI Stream (Client Interface) -->"""

content = content.replace(pane_str, pane_repl)

with open("mesh_gui.py", "w") as f:
    f.write(content)
