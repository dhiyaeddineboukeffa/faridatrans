# 🚌 Project Farida — How to Run from Scratch

A complete step-by-step guide to get the application running on a fresh Windows machine after downloading from GitHub.

---

## ✅ Prerequisites

Before you start, make sure the following software is installed on your computer:

| Software | Minimum Version | Download Link |
|---|---|---|
| **Python** | 3.10+ | https://www.python.org/downloads/ |
| **Node.js** | 18+ | https://nodejs.org/ |
| **Git** *(optional)* | Any | https://git-scm.com/ |

> **Important:** During Python installation, check the box **"Add Python to PATH"**.  
> During Node.js installation, keep all defaults.

---

## 📥 Step 1 — Download the Project

### Option A: Download as ZIP from GitHub
1. Go to the GitHub repository page
2. Click the green **`< > Code`** button → **Download ZIP**
3. Extract the ZIP to a folder, e.g.:  
   `C:\Users\YourName\Desktop\faridatrans-master`

### Option B: Clone with Git
```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

---

## 📂 Project Structure

After extracting, you should see:

```
faridatrans-master/
├── frontend/               ← Next.js web interface
├── backend/
│   ├── routing-service/    ← Python route calculation API
│   └── ingestion-service/  ← Python data ingestion service
├── run_project.ps1         ← One-click launcher script
└── HOW_TO_RUN.md           ← This file
```

---

## 🐍 Step 2 — Install Python Dependencies

You need to install dependencies for **both** backend services.

Open **PowerShell** or **Command Prompt** and run:

### Routing Service
```powershell
cd "C:\path\to\faridatrans-master\backend\routing-service"
pip install -r requirements.txt
```

### Ingestion Service
```powershell
cd "C:\path\to\faridatrans-master\backend\ingestion-service"
pip install -r requirements.txt
```

> **Tip:** Replace `C:\path\to\faridatrans-master` with the actual path where you extracted the project.

---

## 🌐 Step 3 — Install Frontend Dependencies

```powershell
cd "C:\path\to\faridatrans-master\frontend"
npm install
```

This downloads all the required JavaScript packages (may take 1–2 minutes on first run).

---

## 🚀 Step 4 — Run the Application

### ⚡ Easiest way: One-Click Script

From the **root folder** of the project, right-click on **`run_project.ps1`** and choose **"Run with PowerShell"**.

Or run it from PowerShell directly:

```powershell
cd "C:\path\to\faridatrans-master"
powershell -ExecutionPolicy Bypass -File .\run_project.ps1
```

This will automatically open **3 separate terminal windows**:
- 🟢 **Routing Service** — runs on `http://localhost:8000`
- 🟡 **Ingestion Service** — runs on `http://localhost:8001`
- 🔵 **Frontend** — runs on `http://localhost:3000`

---

### 🛠️ Manual way: Run each service separately

If you prefer to start each service yourself, open **3 separate PowerShell windows**:

**Window 1 — Routing Service (Backend)**
```powershell
cd "C:\path\to\faridatrans-master\backend\routing-service"
python main.py
```
Wait until you see: `Application started, Proximity engine loaded.`

**Window 2 — Ingestion Service (Backend)**
```powershell
cd "C:\path\to\faridatrans-master\backend\ingestion-service"
python main.py
```

**Window 3 — Frontend**
```powershell
cd "C:\path\to\faridatrans-master\frontend"
npm run dev
```
Wait until you see: `✓ Ready on http://localhost:3000`

---

## 🌍 Step 5 — Open the App

Once all 3 services are running, open your browser and go to:

```
http://localhost:3000
```

You should see the **Project Farida** map interface. 🗺️

---

## 🗺️ How to Use

1. **Select an origin** from the dropdown (e.g., *ZAAMOUCHE*)
2. **Select a destination** (e.g., *CONSTANTINE*)
3. Click **Find Route**
4. The route will be drawn on the map and **Trip Details** will appear in the sidebar showing:
   - Total travel time and number of transfers
   - Mode of transport (Bus, Tram, Walk, Taxi)
   - All intermediate stations along the route (click to expand)

---

## ❗ Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `python is not recognized` | Python not in PATH | Reinstall Python and check "Add to PATH" |
| `npm is not recognized` | Node.js not installed | Download and install Node.js from nodejs.org |
| `pip install` fails | Missing pip | Run `python -m ensurepip --upgrade` |
| `cannot be loaded, running scripts is disabled` | PowerShell execution policy | Run with `powershell -ExecutionPolicy Bypass -File .\run_project.ps1` |
| `Route not found` error in app | Routing service not running | Make sure Window 1 (routing service) started without errors |
| Frontend shows blank page | Frontend not built yet | Wait a few seconds after `npm run dev`, then refresh |
| `No stops found near origin` | GPS not available | Use the dropdown to select a stop manually |

---

## 🔌 Port Reference

| Service | URL |
|---|---|
| Frontend (Web App) | http://localhost:3000 |
| Routing API | http://localhost:8000 |
| Routing API Docs | http://localhost:8000/docs |
| Ingestion Service | http://localhost:8001 |

---

## 🛑 Stopping the App

Simply close the 3 terminal windows that were opened, or press **`Ctrl + C`** in each one.

---

*Project Farida — Transit Navigation for Constantine, Algeria*
