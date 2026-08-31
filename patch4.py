import re

with open("mesh_gui.py", "r") as f:
    content = f.read()

toggle_search = """<button @click="toggleSeedState(f.id)" class="px-2 py-1 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded text-[10px] text-gray-300 font-semibold uppercase tracking-wider transition">Toggle Seed</button>"""
toggle_replace = """<button @click="toggleSeedState(f.id)" class="px-2 py-1 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded text-[10px] text-gray-300 font-semibold uppercase tracking-wider transition" x-text="f.state === 'Local' ? 'Split to Seeds' : 'Toggle Seeding'"></button>"""
content = content.replace(toggle_search, toggle_replace)

with open("mesh_gui.py", "w") as f:
    f.write(content)
