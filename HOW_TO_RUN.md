# 🚌 Project Farida — How to Run from Scratch

A complete step-by-step guide to get the application running after downloading from GitHub, using **VS Code** or any terminal.

---

## ✅ Prerequisites

Install the following before starting:

| Software | Min Version | Download |
|---|---|---|
| **Python** | 3.10+ | https://www.python.org/downloads/ |
| **Node.js** | 18+ | https://nodejs.org/ |
| **VS Code** *(recommended)* | Any | https://code.visualstudio.com/ |
| **Git** *(optional)* | Any | https://git-scm.com/ |

> **Important:** During Python installation, check **"Add Python to PATH"**.

### Recommended VS Code Extensions
Install these from the Extensions panel (`Ctrl+Shift+X`):

| Extension | Purpose |
|---|---|
| **Python** (Microsoft) | Python syntax, linting, IntelliSense |
| **ES7+ React/Redux/React-Native snippets** | React/TSX support |
| **Tailwind CSS IntelliSense** | Autocomplete for CSS classes |
| **Prettier** | Code formatting |

---

## 📥 Step 1 — Download the Project

### Option A: Download ZIP from GitHub
1. Go to the GitHub repository page
2. Click **`< > Code`** → **Download ZIP**
3. Extract the ZIP somewhere, e.g. `C:\Projects\faridatrans-master`

### Option B: Clone with Git
```bash
git clone https://github.com/dhiyaeddineboukeffa/faridatrans.git
```

---

## 🗂️ Step 2 — Open in VS Code

1. Open **VS Code**
2. Go to **File → Open Folder…**
3. Select the `faridatrans-master` folder
4. VS Code will load the project — you'll see this structure in the Explorer panel:

```
faridatrans-master/
├── frontend/               ← Next.js web interface
├── backend/
│   ├── routing-service/    ← Python route API (port 8000)
│   └── ingestion-service/  ← Python ingestion service (port 8001)
├── run_project.ps1         ← One-click launcher
└── HOW_TO_RUN.md
```

---

## 🐍 Step 3 — Install Python Dependencies

Open the **VS Code integrated terminal** with `` Ctrl+` `` (backtick) and run:

### Routing Service
```bash
cd backend/routing-service
pip install -r requirements.txt
```

### Ingestion Service
```bash
cd ../ingestion-service
pip install -r requirements.txt
```

> **Tip:** You can open multiple terminals in VS Code using the **`+`** button in the terminal panel — useful for running all 3 services simultaneously.

---

## 🌐 Step 4 — Install Frontend Dependencies

In the VS Code terminal:
```bash
cd frontend
npm install
```
This downloads all JavaScript packages (1–2 min on first run).

---

## 🚀 Step 5 — Run the Application

You need **3 terminal tabs** running at the same time. In VS Code, click **`+`** in the terminal panel to open new tabs.

### Terminal 1 — Routing Service
```bash
cd backend/routing-service
python main.py
```
✅ Wait for: `Application started, Proximity engine loaded.`

### Terminal 2 — Ingestion Service
```bash
cd backend/ingestion-service
python main.py
```

### Terminal 3 — Frontend
```bash
cd frontend
npm run dev
```
✅ Wait for: `✓ Ready on http://localhost:3000`

---

### ⚡ Alternative: One-Click Script

Instead of the 3 terminals above, open **one** VS Code terminal and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1
```

This opens 3 separate windows automatically.

---

## 🌍 Step 6 — Open the App

With all 3 services running, open your browser and go to:

```
http://localhost:3000
```

You'll see the **Project Farida** map. 🗺️

---

## 🗺️ How to Use

1. Select an **origin** from the dropdown (e.g. *ZAAMOUCHE*)
2. Select a **destination** (e.g. *CONSTANTINE*)
3. Click **Find Route**
4. The route appears on the map and **Trip Details** shows in the sidebar:
   - Total duration and transfers
   - Transport mode (Bus, Walk, etc.)
   - All intermediate stations (click **"Show X intermediate stops"** to expand)

---

## 🔌 Port Reference

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Routing API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Ingestion Service | http://localhost:8001 |

> The **API Docs** at `/docs` let you test backend routes directly in the browser — useful for debugging.

---

## ❗ Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `python is not recognized` | Python not in PATH | Reinstall Python, check "Add to PATH" |
| `npm is not recognized` | Node.js not installed | Install Node.js from nodejs.org |
| `cannot be loaded, scripts disabled` | PowerShell policy | Run with `-ExecutionPolicy Bypass` as shown above |
| Frontend blank page | Next.js still starting | Wait a few seconds and refresh |
| `Route not found` in app | Routing service not running | Check Terminal 1 started without errors |
| `Module not found` (Python) | Dependencies missing | Re-run `pip install -r requirements.txt` |

---

## 🛑 Stopping the App

In each VS Code terminal tab, press **`Ctrl+C`** to stop the service. Or just close VS Code.

---

*Project Farida — Transit Navigation for Constantine, Algeria*
