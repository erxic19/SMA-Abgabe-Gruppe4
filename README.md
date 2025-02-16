# **SMA-Abgabe – Gruppe 4**  

## **Voraussetzungen**    
- **Docker & Docker-Compose**  
- **Git**  
- **Python**  

---

## **Installation**  
1. **Repository klonen:**  
   ```bash
   git clone https://github.com/erxic19/SMA-Abgabe-Gruppe4.git
   ```
2. **Umgebungsvariablen setzen:**  
   - Erstelle eine `.env`-Datei.  
   - Nutze die Datei `.env.example` als Vorlage für die benötigten Variablen.  

3. **Verzeichnis wechseln:**  
   ```bash
   cd .\SMA-Abgabe-Gruppe4\
   ```
4. **Container starten:**  
   ```bash
   docker-compose up -d
   ```

---

## **Workflows importieren & konfigurieren**  

1. **n8n öffnen:**  
   - Aufrufen unter: [http://localhost:5678](http://localhost:5678)  

2. **Workflows importieren:**  
   - Navigiere zu **"Workflows" → "Import"**.  
   - Lade die Datei **`config/SMA_FINAL_Abgabe.json`** hoch.  

3. **Zugangsdaten setzen:**  
   - Konfiguriere die notwendigen **Credentials** für:  
     - **Qdrant**  (Qdrant URL: http://host.docker.internal:6333)
     - **Ollama** (Ollama URL: http://host.docker.internal:11434) 
     - **Zotero** 
     - **OpenAI**, falls gewünscht. 

---

## **Obsidian konfigurieren**  
1. **Neuen Vault erstellen:**  
   - Der Vault sollte sich in einem **freigegebenen Ordner** befinden, auf den **n8n/docker zugreifen kann** (dieser wird in `docker-compose.yml` erstellt).  

2. **Pfad für Dateizugriff setzen:**  
   - In den Obsidian-Einstellungen den **Pfad für "Read/Write Files from Disk" anpassen**.  

---

## **Qdrant Collections einrichten**  
1. In n8n die beiden **Nodes im roten Kasten ausführen**.  
2. Anschließend die Nodes **löschen**.
3. **Workflow einmal ausführen**, damit die Collections befüllt werden.  
4. Falls ein **Batchsize-Fehler** auftritt:  
   - Dokumente **schrittweise in Zotero** hinzufügen und nacheinander embedden.  
   - Die Batchsize anpassen und erneut testen.  

---

## **Ollama konfigurieren**  
- **Mistral-Modell importieren**, um es für den Chatbot verfügbar zu machen.  

---

## **Chatbot starten**  
1. **Script ausführen:**  
   ```bash
   streamlit run chatbot.py
   ```
2. **Modell auswählen & Frage stellen**  
