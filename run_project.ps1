$root = "c:\Users\LagunaNL5A\Desktop\ffa\faridatrans-master"

Write-Host "Starting Ingestion Service..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend\ingestion-service'; python main.py" -WorkingDirectory "$root\backend\ingestion-service"

Write-Host "Starting Routing Service..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend\routing-service'; python main.py" -WorkingDirectory "$root\backend\routing-service"

Write-Host "Starting Frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev" -WorkingDirectory "$root\frontend"

Write-Host "Project started! Please check the opened windows."
