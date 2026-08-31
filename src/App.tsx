/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { Terminal, Download, FileCode2, Network, Server } from 'lucide-react';

export default function App() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-200 font-sans p-6 sm:p-12">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="border-b border-neutral-800 pb-8">
          <div className="flex items-center gap-3 mb-4 text-emerald-500">
            <Network className="w-8 h-8" />
            <h1 className="text-3xl font-bold tracking-tight text-white">
              Advanced P2P Swarm Network
            </h1>
          </div>
          <p className="text-neutral-400 text-lg max-w-2xl leading-relaxed">
            The Python decentralized local-area mesh network engine has been successfully generated. 
            This environment serves as your asset hub to download and review the script.
          </p>
        </header>

        <main className="grid gap-8 md:grid-cols-2">
          {/* Status & Location Panel */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4 text-neutral-300">
              <FileCode2 className="w-5 h-5 text-blue-400" />
              <h2 className="text-lg font-semibold">Script Location</h2>
            </div>
            <div className="bg-neutral-950 p-4 rounded-lg font-mono text-sm text-neutral-400 break-all mb-6">
              /p2p_mesh.py
            </div>
            
            <p className="text-sm text-neutral-500 mb-6">
              You can find this file in the AI Studio file explorer (usually located on the left pane of your editor environment).
            </p>

            <div className="flex items-center gap-2 mb-4 text-neutral-300">
              <Server className="w-5 h-5 text-purple-400" />
              <h2 className="text-lg font-semibold">Distributed AI Inference Features</h2>
            </div>
            <ul className="space-y-3 text-sm text-neutral-400">
              <li className="flex items-start gap-2">
                <span className="text-purple-500 mt-0.5">✓</span>
                Local Client Persona Manager (Isolated SQLite/JSON)
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-500 mt-0.5">✓</span>
                Stateless Asynchronous Compute & Model Pooling
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-500 mt-0.5">✓</span>
                Tailwind & Alpine.js Dual-Pane Dashboard
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-500 mt-0.5">✓</span>
                Opt-In Decentralized Memory (Vector Indexing)
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-500 mt-0.5">✓</span>
                Privacy Guardrails (Isolated, Contributor, Participant)
              </li>
            </ul>
          </div>

          {/* Execution Instructions */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4 text-neutral-300">
              <Terminal className="w-5 h-5 text-emerald-400" />
              <h2 className="text-lg font-semibold">Execution Instructions</h2>
            </div>
            
            <p className="text-sm text-neutral-400 mb-4">
              To test the distributed AI cluster, install the required dependencies and spin up your nodes.
            </p>

            <div className="space-y-4">
              <div>
                <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2 block">
                  Prerequisites
                </span>
                <div className="bg-neutral-950 p-3 rounded-lg font-mono text-sm overflow-x-auto text-yellow-400">
                  pip install psutil
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2 block">
                  Node 1 (Default Ports)
                </span>
                <div className="bg-neutral-950 p-3 rounded-lg font-mono text-sm overflow-x-auto text-emerald-400">
                  python p2p_mesh.py
                </div>
              </div>
              
              <div>
                <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2 block">
                  Node 2 (Custom Ports)
                </span>
                <div className="bg-neutral-950 p-3 rounded-lg font-mono text-sm overflow-x-auto text-emerald-400">
                  python p2p_mesh.py --tcp-port 8001
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2 block">
                  Testing the Mesh GUI
                </span>
                <div className="text-xs text-neutral-400 mb-2">
                  We've built a full-stack FastAPI application that provides a real-time, dual-pane telemetry and chat dashboard. To run it locally:
                </div>
                <div className="bg-neutral-950 p-2 rounded border border-neutral-800 font-mono text-[11px] text-neutral-300">
                  <div className="text-neutral-500 mb-1"># 1. Install required dependencies</div>
                  <div className="mb-2">pip install fastapi uvicorn websockets</div>
                  <div className="text-neutral-500 mb-1"># 2. Launch the Mesh Orchestrator GUI</div>
                  <div>python mesh_gui.py</div>
                </div>
                <div className="text-xs text-neutral-400 mt-2">
                  Once running, open <code className="text-purple-400 bg-neutral-950 px-1 rounded">http://localhost:8080</code> to view the dual-pane UI. Create custom local personas in the chat pane, and watch how their isolated system prompts are wrapped and passed into the dumb execution grid.
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
