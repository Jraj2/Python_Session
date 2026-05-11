import os
import pandas as pd
import time
import chromadb
from chromadb.utils import embedding_functions
from tabulate import tabulate

# 1. LOAD THE GEOM_2024 DOCUMENT
file_path = "GEOM_2024.txt"

if os.path.exists(file_path):
    with open(file_path, "r") as f:
        full_corpus = f.read()
    print(f"✅ Document Loaded: {file_path} ({len(full_corpus)} characters)")
else:
    print("❌ ERROR: GEOM_2024.txt not found. Please run the document creation block first.")

# 2. SETUP EMBEDDING MODEL
# We use a standard industry-grade embedding function
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# ==========================================
# PHASE 1: LOAD CORPUS & SETUP
# ==========================================
file_path = "GEOM_2024.txt" # Update this to your path if different

if not os.path.exists(file_path):
    print("❌ Critical Error: File not found. Please upload GEOM_2024.txt to Colab.")
else:
    with open(file_path, "r") as f:
        full_corpus = f.read()

# Setup Embedding Model (The 'Translator')
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# ==========================================
# PHASE 2: SEMANTIC CHUNKING
# ==========================================
# Leaders: We use small chunks to make the K-value search meaningful
def create_micro_chunks(text):
    # Splits into small semantic units (lines/sentences)
    return [c.strip() for c in text.split("\n") if len(c.strip()) > 15]

current_chunks = create_micro_chunks(full_corpus)
print(f"✅ Chunking Complete: Created {len(current_chunks)} semantic chunks.")

# ==========================================
# PHASE 3: VECTOR STORE (ChromaDB)
# ==========================================
chroma_client = chromadb.Client()
try:
    chroma_client.delete_collection("rag_engineering_lab")
except:
    pass

collection = chroma_client.get_or_create_collection(name="rag_engineering_lab", embedding_function=emb_fn)

collection.add(
    documents=current_chunks,
    metadatas=[{"section": "GEOM_2024"} for _ in current_chunks],
    ids=[f"id_{i}" for i in range(len(current_chunks))]
)
print("✅ Vector Store Ready.")

# ==========================================
# PHASE 4: THE EVALUATION HARNESS
# ==========================================
eval_set = [
    {"q": "Probation period length?", "check": "6 months"},
    {"q": "Annual PTO days?", "check": "25 days"},
    {"q": "Paternity leave length?", "check": "8 weeks"},
    {"q": "Hotel cap in Tokyo?", "check": "450"},
    {"q": "Billable trip for 9 hours. Business Class?", "check": "8 hours"},
    {"q": "Lost device reporting time?", "check": "4 hours"},
    {"q": "Office dogs policy?", "check": "REFUSE"},
    {"q": "SpaceX flight booking?", "check": "REFUSE"}
]

def run_evaluation(k_val, threshold_val):
    results = []
    for item in eval_set:
        # 1. RETRIEVE
        query_res = collection.query(query_texts=[item['q']], n_results=k_val, include=['documents', 'distances'])

        best_dist = query_res['distances'][0][0]
        context = " ".join(query_res['documents'][0]).lower()

        # 2. SCORE (Logic based on Threshold)
        is_refusal = best_dist > threshold_val

        if item['check'] == "REFUSE":
            success = "✅ PASSED" if is_refusal else "❌ Hallucination"
        else:
            success = "✅ PASSED" if (not is_refusal and item['check'].lower() in context) else "❌ Inaccurate/Refused"

        results.append({"Question": item['q'], "Dist": round(best_dist, 2), "Status": success})

    report = pd.DataFrame(results)
    pass_rate = (report['Status'] == "✅ PASSED").mean() * 100
    return report, pass_rate

# ==========================================
# PHASE 5: THE FINAL SHIPMENT (THE COMPARISON)
# ==========================================
# Test 1: Lazy RAG (Small search, Strict gate)
lazy_report, lazy_rate = run_evaluation(k_val=1, threshold_val=0.4)

# Test 2: Optimized RAG (Deep search, Balanced gate)
opt_report, opt_rate = run_evaluation(k_val=5, threshold_val=0.6)

print("\n" + "="*60)
print(f"FINAL RAG PERFORMANCE COMPARISON")
print("="*60)
print(f"Lazy RAG (K=1, T=0.4) Pass Rate: {lazy_rate}%")
print(f"Optimized RAG (K=5, T=0.6) Pass Rate: {opt_rate}%")
print("="*60)

# Show the trace table for the Batch
print("\nDETAILED EVALUATION TRACE (OPTIMIZED RUN):")
print(tabulate(opt_report, headers='keys', tablefmt='fancy_grid'))