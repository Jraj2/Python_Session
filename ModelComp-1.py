import pandas as pd
import time, re, chromadb
from chromadb.utils import embedding_functions
from tabulate import tabulate

# 1. 20 SOP RULES
sop_docs = [
    {"id": "HR_01", "text": "Maternity leave is 16 weeks. Paternity leave is 8 weeks."},
    {"id": "HR_02", "text": "Bereavement: 5 days for immediate family, 2 days for extended."},
    {"id": "IT_01", "text": "Laptops replaced every 3 years. Budget is $2,500."},
    {"id": "IT_02", "text": "VPN is mandatory for public Wi-Fi usage."},
    {"id": "TRV_01", "text": "Flights > 10 hours allow Business Class. Else Economy."},
    {"id": "TRV_02", "text": "Stipend: $100 for NYC/London/Tokyo, $60 elsewhere."},
    {"id": "FIN_01", "text": "Expenses > $25 require a digital receipt."},
    {"id": "FIN_02", "text": "Client entertainment cap is $150 per head."},
    {"id": "SEC_01", "text": "Report lost badges within 2 hours."},
    {"id": "SEC_02", "text": "Visitors must be escorted in Zone A."},
    {"id": "OPS_01", "text": "Office hours: 9AM-6PM. Core hours: 10AM-4PM."},
    {"id": "OPS_02", "text": "Meeting rooms max booking: 3 hours."},
    {"id": "LEGL_01", "text": "NDAs required before vendor IP sharing."},
    {"id": "HR_03", "text": "Annual leave is 25 days."},
    {"id": "IT_03", "text": "Software requests need Dept Head approval."},
    {"id": "FIN_03", "text": "Submit invoices by the 25th of the month."},
    {"id": "OPS_03", "text": "Desk sharing mandatory if in office < 3 days/week."},
    {"id": "TRV_03", "text": "Hotel bookings must be 14 days in advance."},
    {"id": "LEGL_02", "text": "Contract signatures require 2 witnesses."},
    {"id": "SEC_03", "text": "Tailgating through secure doors is a Tier-1 violation."}
]

# 2. VECTOR DB SETUP
chroma_client = chromadb.Client()
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = chroma_client.get_or_create_collection(name="lab_sop", embedding_function=emb_fn)
collection.add(documents=[d['text'] for d in sop_docs], ids=[d['id'] for d in sop_docs])

# 3. TEST SET
test_set = [
    {"q": "How long is paternity leave?", "gold": "8 weeks"},
    {"q": "Can I book Business for an 11-hour flight?", "gold": "Business Class"},
    {"q": "What is my meal budget in Chicago?", "gold": "$60"},
    {"q": "When should I report a lost badge?", "gold": "2 hours"},
    {"q": "How old must a laptop be to get a new one?", "gold": "3 years"},
    {"q": "Do I need a receipt for a $30 lunch?", "gold": "Yes"},
    {"q": "Can I book a room for 4 hours?", "gold": "3 hours"},
    {"q": "What is the client entertainment limit?", "gold": "$150"}
]

print(f"✅ KB and Test Set Ready.")

def run_prompt_only(q):
    # Simulated "uninformed" LLM
    if "paternity" in q.lower(): ans = "Usually 2 weeks."
    elif "laptop" in q.lower(): ans = "Laptops are replaced every 5 years."
    else: ans = "I am not sure, check the portal."
    return {"ans": ans, "cost": 0.01, "lat": 0.2}

def run_rag(q):
    # Actual Retrieval
    res = collection.query(query_texts=[q], n_results=1)
    ans = f"[SOURCE: {res['ids'][0][0]}] {res['documents'][0][0]}"
    return {"ans": ans, "cost": 0.05, "lat": 0.5}

def run_fewshot_adapter(q):
    # Retrieval + Strict Formatting
    res = collection.query(query_texts=[q], n_results=1)
    ans = f"### COMPLIANCE REPORT ###\nINFO: {res['documents'][0][0]}\nID: {res['ids'][0][0]}"
    return {"ans": ans, "cost": 0.08, "lat": 0.4}

def run_agent(q):
    # Retrieval + "Action" (Tool use)
    res = collection.query(query_texts=[q], n_results=1)
    ans = f"THOUGHT: Checking SOP... ACTION: Created Jira Ticket T-100. RESULT: {res['documents'][0][0]}"
    return {"ans": ans, "cost": 0.15, "lat": 1.1}

all_results = []

for case in test_set:
    q = case['q']
    gold = case['gold']

    # Execute all 4 pipelines with the CURRENT question
    p = run_prompt_only(q)
    r = run_rag(q)
    f = run_fewshot_adapter(q)
    a = run_agent(q)

    # DYNAMIC SCORING FUNCTION
    def calculate_score(ans, target):
        # If the key information (gold) is in the answer, 100 points.
        return 100 if target.lower() in ans.lower() else 0

    all_results.append({
        "Question": q,
        "Prompt-Only": p['ans'],
        "RAG": r['ans'],
        "Adapter": f['ans'],
        "Agent": a['ans'],
        "P_Score": calculate_score(p['ans'], gold),
        "R_Score": calculate_score(r['ans'], gold),
        "F_Score": calculate_score(f['ans'], gold),
        "A_Score": calculate_score(a['ans'], gold),
        "P_Cost": p['cost'], "R_Cost": r['cost'], "F_Cost": f['cost'], "A_Cost": a['cost']
    })

# Convert to DataFrame for visualization
results_df = pd.DataFrame(all_results)
print("✅ All tests executed and scored.")


# 1. TRACE TABLE (Question vs. Every Answer)
trace_cols = ["Question", "Prompt-Only", "RAG", "Adapter", "Agent"]
print("\n" + "="*50 + "\nDETAILED OUTPUT TRACE (HOW THEY ANSWERED)\n" + "="*50)
print(tabulate(results_df[trace_cols], headers='keys', tablefmt='grid'))

# 2. CALCULATED LEADERBOARD (Averages)
leaderboard = [
    ["Prompt-Only", results_df["P_Score"].mean(), results_df["P_Cost"].sum(), "Low", "Generic Responses"],
    ["RAG", results_df["R_Score"].mean(), results_df["R_Cost"].sum(), "High", "Factually Grounded"],
    ["Few-Shot Adapter", results_df["F_Score"].mean(), results_df["F_Cost"].sum(), "Strict", "Professional Branding"],
    ["Agent", results_df["A_Score"].mean(), results_df["A_Cost"].sum(), "High", "Process Automation"]
]

print("\n" + "="*50 + "\nDYNAMIC SCORING LEADERBOARD\n" + "="*50)
print(tabulate(leaderboard, headers=["Method", "Avg Accuracy (%)", "Total Cost ($)", "Format Control", "Best For..."], tablefmt='fancy_grid'))