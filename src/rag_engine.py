import os
from typing import List, Dict, Any, Optional
import chromadb
from fastembed import TextEmbedding

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
COLLECTION_NAME = "darglobal_realestate"

SYSTEM_PROMPT = """You are the official Senior AI Real Estate Advisor representing DarGlobal PLC and Wasalt Real Estate.

Your role:
1. Provide authoritative, precise, and sophisticated information regarding DarGlobal's ultra-luxury international developments (e.g., Tierra Viva by Lamborghini in Spain, DaVinci Tower by Pagani in Dubai, The Astera by Aston Martin in RAK, AIDA in Oman with Trump Organization & Fendi Casa, Trump Tower Dubai, Trump Plaza & Trump Tower Jeddah, Les Vagues by Elie Saab in Qatar, Neptune Villas by Mouawad in Riyadh) and corporate insights (London Stock Exchange LSE: DAR, 17.3% ROE, CEO Ziad El Chaar).
2. Assist clients with Saudi Arabia real estate opportunities from Wasalt (apartments, luxury villas, compounds, commercial properties, and investment FAQs across Riyadh, Jeddah, Al Khobar, Dammam, Makkah, and Madinah).
3. Always ground your answers strictly on the Provided Context below. Do not make up facts or inventory. If specific details (such as current real-time availability) are not in the context, guide the user to consult DarGlobal sales or visit the provided project links.
4. When mentioning properties, highlight key specifications: brand partner, exact city/country, price guide/currency, bedrooms, area, handover date, and luxury amenities.
5. Provide direct Markdown links to the official project or property URLs when relevant.
6. Respond with elegance, professionalism, and clarity. Format your responses with clear headings, bullet points, and highlight metrics."""

class RAGEngine:
    def __init__(self, chroma_path: str = CHROMA_PATH, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.chroma_path = chroma_path
        self.model_name = model_name
        self._init_components()

    def _init_components(self):
        print(f"Loading RAGEngine vector store from {self.chroma_path}...")
        self.embed_model = TextEmbedding(model_name=self.model_name)
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        try:
            self.collection = self.chroma_client.get_collection(COLLECTION_NAME)
        except Exception:
            self.collection = self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

    def retrieve(
        self,
        query: str,
        n_results: int = 4,
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top relevant documents matching the query.
        """
        query_emb = list(self.embed_model.embed([query]))[0].tolist()
        
        where_filter = None
        if source_filter and source_filter.lower() != "all":
            where_filter = {"source": source_filter}

        query_args = {
            "query_embeddings": [query_emb],
            "n_results": n_results
        }
        if where_filter:
            query_args["where"] = where_filter

        results = self.collection.query(**query_args)

        docs = []
        if results and results.get("ids") and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                meta = results["metadatas"][0][i]
                doc_text = results["documents"][0][i]
                distance = results["distances"][0][i] if results.get("distances") else 0.0
                docs.append({
                    "id": results["ids"][0][i],
                    "title": meta.get("title", "Untitled"),
                    "source": meta.get("source", "General"),
                    "category": meta.get("category", "General"),
                    "city": meta.get("city", ""),
                    "country": meta.get("country", ""),
                    "price": meta.get("price", "N/A"),
                    "url": meta.get("url", ""),
                    "distance": distance,
                    "relevance_score": round(1.0 - distance, 3),
                    "content": doc_text
                })
        return docs

    def format_prompt(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Format context and chat history into OpenAI messages format.
        """
        context_parts = []
        for idx, doc in enumerate(retrieved_docs):
            context_parts.append(f"--- Context Document {idx+1} [{doc['source']}: {doc['title']}] ---\n{doc['content']}\n")

        full_context = "\n".join(context_parts) if context_parts else "No specific documents found in database."

        user_content = f"""Provided Context:
{full_context}

User Question:
{query}

Please provide a detailed, helpful, and beautifully formatted response based on the context above."""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        if chat_history:
            # Include last few turns of conversation for contextual continuity
            recent_turns = chat_history[-6:]
            for turn in recent_turns:
                messages.append(turn)

        messages.append({"role": "user", "content": user_content})
        return messages
