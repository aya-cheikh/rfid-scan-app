@echo off
cd /d "C:\Users\HP\Downloads\CODES"

:: Lancer l'application Streamlit sans ouvrir Edge
start "" /B streamlit run app.py --server.headless true --browser.gatherUsageStats false

:: Attendre que le serveur démarre
timeout /t 5 > nul

:: Ouvrir dans Chrome en mode application
start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --app=http://localhost:8501
