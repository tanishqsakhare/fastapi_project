from fastapi import FastAPI
from multiprocessing import Process, Queue, Manager
import time
import random
import uvicorn
from fastapi.responses import HTMLResponse

app = FastAPI()    

# Global variables (will be initialized later)
manager = None
status_dict = None
queues = []
processes = []

def worker(queue_id: int, process_id: int, q: Queue, status_dict):
    """Each process keeps working on tasks from its queue."""
    while True:
        task = q.get()
        if task == "STOP":
            status_dict[f"Queue-{queue_id}-Process-{process_id}"] = "Stopped"
            break
        status_dict[f"Queue-{queue_id}-Process-{process_id}"] = f"Working on {task}"
        for i in range(3):
            time.sleep(random.uniform(1, 2))
            status_dict[f"Queue-{queue_id}-Process-{process_id}"] = f"{task}: step {i+1}/3 done"
        status_dict[f"Queue-{queue_id}-Process-{process_id}"] = f"{task} completed"

@app.get("/")
def home():
    return {"message": "FastAPI Multiprocessing Demo"}

@app.get("/add-task")
def add_task(queue_id: int, task: str):
    """Add a task to the selected queue (via browser or API)."""
    if not queues or queue_id < 0 or queue_id >= len(queues):
        return {"error": "Invalid queue_id. Must be 0, 1, or 2."}
    queues[queue_id].put(task)
    return {"message": f"Task '{task}' added to Queue-{queue_id}"}

@app.get("/status")
def get_status():
    """Return live status of all processes."""
    if not status_dict:
        return {"error": "System not initialized yet."}
    return dict(status_dict)

@app.post("/stop")
def stop_all():
    """Stop all worker processes."""
    for q in queues:
        for _ in range(2):
            q.put("STOP")
    return {"message": "Stopping all processes..."}

@app.get("/control", response_class=HTMLResponse)
def control_panel():
    """A simple HTML UI to add tasks and view status."""
    return """
    <html>
    <head>
        <title>Task Control Panel</title>
        <style>
            body { font-family: Arial; background: #f8fafc; padding: 40px; }
            h2 { color: #2563eb; }
            input, select, button {
                padding: 8px 12px; margin: 8px; font-size: 15px;
                border-radius: 6px; border: 1px solid #ccc;
            }
            button {
                background-color: #2563eb; color: white; border: none;
                border-radius: 6px; cursor: pointer;
            }
            button:hover { background-color: #1e40af; }
            a { color: #2563eb; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h2>🚀 Add Task to a Queue</h2>

        <form action="/add-task" method="get">
            <label>Queue ID (0–2):</label>
            <select name="queue_id">
                <option value="0">Queue 0</option>
                <option value="1">Queue 1</option>
                <option value="2">Queue 2</option>
            </select><br>

            <label>Task Name:</label>
            <input type="text" name="task" placeholder="e.g. AnalyzeData" required><br>

            <button type="submit">Add Task</button>
        </form>

        <hr>
        <h3>🧠 Useful Links</h3>
        <p><a href="/status" target="_blank">View JSON Status</a></p>
    </body>
    </html>
    """

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """A simple live dashboard that auto-refreshes status every 2 seconds."""
    return """
    <html>
    <head>
        <title>Live Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #f9fafb; padding: 40px; }
            h2 { color: #2563eb; }
            table { border-collapse: collapse; width: 80%; margin-top: 20px; }
            th, td {
                border: 1px solid #ccc;
                padding: 10px;
                text-align: left;
            }
            th { background: #2563eb; color: white; }
            tr:nth-child(even) { background: #f3f4f6; }
            #status { margin-top: 20px; }
        </style>
        <script>
            async function refreshStatus() {
                const res = await fetch('/status');
                const data = await res.json();
                const tableBody = document.getElementById('status');
                tableBody.innerHTML = '';
                for (const [proc, state] of Object.entries(data)) {
                    const row = `<tr><td>${proc}</td><td>${state}</td></tr>`;
                    tableBody.innerHTML += row;
                }
            }
            setInterval(refreshStatus, 2000);
            window.onload = refreshStatus;
        </script>
    </head>
    <body>
        <h2>📊 Real-Time Process Dashboard</h2>
        <p>Auto-refreshes every 2 seconds</p>
        <table>
            <thead>
                <tr><th>Process</th><th>Status</th></tr>
            </thead>
            <tbody id="status">
                <tr><td colspan="2">Loading...</td></tr>
            </tbody>
        </table>

        <hr>
        <p><a href="/control">➕ Add New Task</a></p>
    </body>
    </html>
    """

if __name__ == "__main__":
    manager = Manager()
    status_dict = manager.dict()
    queues = [Queue() for _ in range(3)]
    processes = []

    # Start 6 worker processes (2 processes per queue)
    for q_id, q in enumerate(queues):
        for p_id in range(2):
            name = f"Queue-{q_id}-Process-{p_id}"
            status_dict[name] = "Idle"
            p = Process(target=worker, args=(q_id, p_id, q, status_dict))
            p.daemon = True
            p.start()
            processes.append(p)

    print("All 6 worker processes started.")
    print("Open browser → http://127.0.0.1:8000/control")

    uvicorn.run(app, host="127.0.0.1", port=8000)
