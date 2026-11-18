import json
import os
import shutil
from fastembed import TextEmbedding
import chromadb
from chromadb.config import Settings

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "darglobal_realestate"
KNOWLEDGE_BASE_PATH = "data/processed/unified_knowledge_base.json"

def build_vectorstore():
    print(f"Loading knowledge base from {KNOWLEDGE_BASE_PATH}...")
    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"Total documents to index: {len(documents)}")

    # Clear existing Chroma store if present
    if os.path.exists(CHROMA_PATH):
        print(f"Resetting existing chroma database at {CHROMA_PATH}...")
        shutil.rmtree(CHROMA_PATH)

    os.makedirs(CHROMA_PATH, exist_ok=True)

    print("Initializing FastEmbed embedding model (BAAI/bge-small-en-v1.5)...")
    embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    print(f"Initializing ChromaDB PersistentClient at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    ids = []
    texts = []
    metadatas = []

    for idx, doc in enumerate(documents):
        doc_id = doc.get("id") or f"doc_{idx}"
        text_content = doc.get("content", "").strip()
        if not text_content:
            continue

        ids.append(str(doc_id))
        texts.append(text_content)
        metadatas.append({
            "source": doc.get("source", "Unknown"),
            "category": doc.get("category", "General"),
            "title": doc.get("title", "Untitled")[:150],
            "brand": doc.get("brand", "None")[:100],
            "country": doc.get("country", "Global")[:50],
            "city": doc.get("city", "General")[:50],
            "price": str(doc.get("price", "N/A"))[:50],
            "url": doc.get("url", "")[:250],
        })

    print(f"Generating embeddings for {len(texts)} documents in batches...")
    batch_size = 64
    all_embeddings = []
    
    # FastEmbed generates a generator
    raw_embeddings = list(embed_model.embed(texts))
    for emb in raw_embeddings:
        all_embeddings.append(emb.tolist())

    print(f"Generated {len(all_embeddings)} embeddings. Inserting into ChromaDB...")
    
    # Chroma insert in batches
    for i in range(0, len(ids), batch_size):
        end = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:end],
            embeddings=all_embeddings[i:end],
            documents=texts[i:end],
            metadatas=metadatas[i:end]
        )
        print(f"Inserted documents {i+1} to {end}...")

    print(f"\nSuccessfully built ChromaDB vector store with {collection.count()} records at {CHROMA_PATH}!")

    # Verify query
    test_query = "What luxury Lamborghini villas does DarGlobal develop in Spain?"
    print(f"\n--- Testing retrieval with query: '{test_query}' ---")
    query_emb = list(embed_model.embed([test_query]))[0].tolist()
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=2
    )

    for i in range(len(results["ids"][0])):
        print(f"Rank {i+1}:")
        print(f"  Title: {results['metadatas'][0][i]['title']}")
        print(f"  Source: {results['metadatas'][0][i]['source']}")
        print(f"  Distance: {results['distances'][0][i]:.4f}")
        print(f"  Snippet: {results['documents'][0][i][:160]}...\n")

if __name__ == "__main__":
    build_vectorstore()
