# Abgabe-SMA-Gruppe 4

## Voraussetzungen
- Docker & Docker-Compose

## Installation
1. Repo klonen: `git clone https://github.com/erxic19/SMA-Abgabe-Gruppe4.git`
2. `.env` erstellen (siehe `.env.example` für benötigte Variablen)
3. Container starten: `docker-compose up -d`

## Workflows importieren + konfigurieren (falls nicht schon vorhanden)
1. Öffne n8n unter `http://localhost:5678`
2. Gehe zu "Workflows" → "Import" und wähle die JSON-Dateien aus `config/SMA_FINAL_Abgabe.json`.
3. Credentials setzen (Qdrant, Ollama, Zotero)

## Obsidian konfigurieren
1. neuen Vault erstellen (In einem Ordner auf dem n8n/docker zugreifen kann (shared Ordner wird in docker-compose erstellt) 
2. neuen Pfad im Read/Write Files from Disk setzen

## Qdrant Collections
1. In n8n die beiden Nodes im Roten Kasten ausführen, danach am besten löschen.
2. Workflow einmal ausführen lassen, damit Collections befüllt werden.
	2.1 Falls Fehler kommt, dass Batchsize zu groß ist, Dokumente nach und nach in Zotero reinlegen und embedden. (und mit Batchsize rumprobieren)

## Ollama konfigurieren
1. Mistral Model importieren

## Chatbot einrichten
 1. chatbot.py ausführen und Model aussuchen
 2. Frage stellen
 