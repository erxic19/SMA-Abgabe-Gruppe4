import streamlit as st
import requests
import os
from openai import OpenAI
from qdrant_client import QdrantClient
from typing import List, Tuple

# ~~~~~~~~~~~~~ Konfiguration ~~~~~~~~~~~~~
QDRANT_URL = os.environ.get("QDRANT_URL", "http://host.docker.internal:6333/")
COLLECTION_ZOTERO = "ZoteroNeu"
COLLECTION_OBSIDIAN = "obsidianNeu"
VECTOR_SIZE = 1536

# API Keys aus Umgebungsvariablen
OPENAI_API_KEY = os.environ.get("API_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")


# Client-Initialisierung
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
qdrant_client = QdrantClient(url=QDRANT_URL) if QDRANT_URL else None

# ~~~~~~~~~~~~~ Funktionen ~~~~~~~~~~~~~
EMBEDDING_MODEL = "text-embedding-3-small"

def search_qdrant(collection_name: str, query_embedding: List[float], limit: int = 3) -> List:
    """Durchsucht Qdrant-Sammlung"""
    if not qdrant_client:
        st.error("Qdrant-Client nicht initialisiert")
        return []
    
    try:
        return qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit
        )
    except Exception as e:
        st.error(f"Qdrant-Suche fehlgeschlagen: {e}")
        return []

def internet_search(query: str, max_results: int = 3) -> List[dict]:
    """Internet-Suche mit Serper API"""
    if not SERPER_API_KEY:
        st.error("Serper API-Key fehlt")
        return []

    try:
        headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json={"q": query, "num": max_results}
        )
        return response.json().get('organic', [])[:max_results]
    except Exception as e:
        st.error(f"Internet-Suche fehlgeschlagen: {e}")
        return []

def get_best_source(question_embedding: List[float]) -> Tuple[List, str]:
    """Quellenpriorisierung"""
    zotero_hits = search_qdrant(COLLECTION_ZOTERO, question_embedding)
    if zotero_hits and zotero_hits[0].score > 0.35:  # Angepasster Schwellenwert
        return zotero_hits, "Zotero"
    
    obsidian_hits = search_qdrant(COLLECTION_OBSIDIAN, question_embedding)
    if obsidian_hits:
        return obsidian_hits, "Obsidian"
    
    return [], "Internet"

def get_embedding(text: str) -> List[float]:
    """Generiert Embedding"""
    if not client:
        st.error("OpenAI-Client nicht initialisiert")
        return []
    
    try:
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL,
            dimensions=VECTOR_SIZE
        )
        return response.data[0].embedding
    except Exception as e:
        st.error(f"Embedding-Erstellung fehlgeschlagen: {e}")
        return []

def generate_context(hits: List, source_type: str) -> str:
    """Erstellt Kontext mit Metadaten"""
    context = []
    
    if source_type in ["Zotero", "Obsidian"]:
        for i, hit in enumerate(hits, 1):
            title = hit.payload.get('metadata', {}).get('name', 'Ohne Titel')
            content = hit.payload.get('content', '')
            context.append(
                f"Quelle {i} ({source_type}): [Titel: {title}]\n{content}"
            )
        return "\n\n".join(context)
    
    if source_type == "Internet":
        for i, result in enumerate(hits, 1):
            title = result.get('title', 'Ohne Titel')
            snippet = result.get('snippet', '')
            context.append(
                f"Web-Ergebnis {i}: {title}\n{snippet}"
            )
        return "\n\n".join(context)
    
    return ""

def generate_response(prompt: str, use_openai: bool) -> str:
    """Generiert Antwort"""
    try:
        if use_openai:
            if not client:
                return "OpenAI-Client nicht verfügbar"
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Antworte präzise auf Deutsch"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        else:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.5, "num_predict": 1000}
                }
            )
            return response.json().get("response", "Keine Antwort erhalten")
    except Exception as e:
        return f"Fehler: {str(e)}"

def answer_question(question: str, use_openai: bool) -> Tuple[str, str, List[str]]:
    """Beantwortet Fragen mit Quellenangaben"""
    question_embedding = get_embedding(question)
    best_hits, source_type = get_best_source(question_embedding)
    file_names = []
    
    if source_type == "Internet":
        best_hits = internet_search(question)
        if not best_hits:
            return "❌ Keine relevanten Informationen gefunden.", "Keine Quelle", []
    else:
        file_names = [
            hit.payload.get('metadata', {}).get('name', 'Unbekannter Titel')
            for hit in best_hits
            if hit.payload.get('metadata')
        ]
    
    st.session_state.last_payload = [hit.payload for hit in best_hits] if best_hits else []
    context = generate_context(best_hits, source_type)
    
    prompt = f"""Kontextinformationen:
{context}

Frage: {question}

Antwortanforderungen:
- Antwort basierend AUSSCHLIESSLICH auf den Dokumenten, die Dokumente haben immer recht
- Fachterminologie beibehalten
- Antwort auf Deutsch"""
    
    return generate_response(prompt, use_openai), source_type, file_names

def display_internet_results(results: List[dict]):
    """Zeigt Web-Ergebnisse an"""
    if not results:
        st.warning("Keine Web-Ergebnisse gefunden")
        return
    
    st.subheader("🌐 Web-Suchergebnisse")
    for i, result in enumerate(results, 1):
        with st.expander(f"Ergebnis {i}: {result.get('title', 'Kein Titel')}"):
            st.markdown(f"**URL:** [{result.get('link', '')}]({result.get('link', '')})")
            st.markdown(f"**Inhalt:** {result.get('snippet', 'Keine Beschreibung')}")

# ~~~~~~~~~~~~~ UI ~~~~~~~~~~~~~
def main():
    st.set_page_config(page_title="IT-Security Assistant", page_icon="🔒")
    st.title("🔒 IT-Security Knowledge Assistant")
    
    with st.expander("⚙️ Einstellungen", expanded=False):
        model_choice = st.radio(
            "Modellauswahl:",
            ["OpenAI (GPT-3.5)", "Lokales Mistral"],
            help="Wählen Sie zwischen Cloud- und lokaler KI"
        )
    
    question = st.text_input("**Stelle deine IT-Sicherheitsfrage:**", "")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if st.button("Analysieren", help="Standardanalyse mit Priorisierung lokaler Quellen"):
            if not question.strip():
                st.warning("Bitte Frage eingeben!")
                return
                
            with st.spinner("🔍 Analysiere Wissensquellen..."):
                use_openai = model_choice == "OpenAI (GPT-3.5)"
                answer, source, file_names = answer_question(question, use_openai)
                
            st.subheader("Ergebnis:")
            st.markdown(answer)
            
            if source != "Internet" and file_names:
                st.markdown("**Verwendete Quellen:**")
                for file in file_names:
                    st.markdown(f"- 📄 {file}")
            
            st.markdown(f"**Quelle:** {source}")
            
            with st.expander("🔍 Debug-Informationen"):
                st.write("Letzte Payload-Struktur:", st.session_state.get('last_payload', []))
                st.write("Qdrant-Status:", 
                        "Verbunden" if qdrant_client else "Nicht verbunden",
                        f"({QDRANT_URL})")
    
    with col2:
        if st.button("🌐 Web-Suche", help="Direkte Suche im Internet"):
            if not question.strip():
                st.warning("Bitte Frage eingeben!")
                return
                
            with st.spinner("🌐 Durchsuche das Internet..."):
                web_results = internet_search(question)
                display_internet_results(web_results)
    
    st.markdown("---")
    st.caption("KI-System für IT-Sicherheitsanalysen | SMA-Prüfungsleistung Gruppe 4")

if __name__ == "__main__":
    main()