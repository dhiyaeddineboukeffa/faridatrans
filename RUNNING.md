# How to Run the Application

You need to run **three separate terminals** to start the entire application.

## 1. Frontend (The Web Interface)
This runs the React/Next.js website.

1.  Open a terminal.
2.  Navigate to the frontend folder:
    ```powershell
    cd "c:\Users\bob\Desktop\project farida\frontend"
    ```
3.  Start the server:
    ```powershell
    npm run dev
    ```
4.  Open your browser to: [http://localhost:3000](http://localhost:3000)

## 2. Backend - Routing Service
This calculates the best routes.

1.  Open a **new** terminal.
2.  Navigate to the routing service folder:
    ```powershell
    cd "c:\Users\bob\Desktop\project farida\backend\routing-service"
    ```
3.  Start the service:
    ```powershell
    python main.py
    ```

## 3. Backend - Ingestion Service
This handles data updates (stops, vehicles).

1.  Open a **new** terminal.
2.  Navigate to the ingestion service folder:
    ```powershell
    cd "c:\Users\bob\Desktop\project farida\backend\ingestion-service"
    ```
3.  Start the service:
    ```powershell
    python main.py
    ```

---

### Common Errors
*   **`npm error code ENOENT`**: You are in the wrong folder. Make sure you `cd` into the `frontend` folder before running `npm run dev`.
*   **`paython` is not recognized**: You made a typo. The command is `python` (or sometimes `python3` depending on your setup), not `paython`.
