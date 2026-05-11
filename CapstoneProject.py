import pandas as pd

# -----------------------------
# Step 1: Load client input file
# -----------------------------
# Replace 'client_input.xlsx' with your actual file name
df = pd.read_excel("client_input.xlsx")

# -----------------------------
# Step 2: Book journal entries
# -----------------------------
# Create a Journal Entry ID for traceability
df["JournalEntryID"] = df.index + 1

# Example booking logic: Debit and Credit must balance
df["BookedDebit"] = df["Debit Amount"]
df["BookedCredit"] = df["Credit Amount"]

# -----------------------------
# Step 3: Reconciliation
# -----------------------------
# Rule: Debit - Credit should equal 0 for balanced entries
df["ReconciliationStatus"] = df.apply(
    lambda row: "Balanced" if abs(row["BookedDebit"] - row["BookedCredit"]) < 0.01 else "Mismatch",
    axis=1
)

# -----------------------------
# Step 4: Reporting
# -----------------------------
# Save booked entries with reconciliation status
df.to_excel("journal_entries_output.xlsx", index=False)

# Print summary
summary = df["ReconciliationStatus"].value_counts()
print("Reconciliation Summary:")
print(summary)

print("\nDetailed journal entries saved to 'journal_entries_output.xlsx'")