from flask import Flask, request, jsonify, render_template, send_from_directory
from embedder import embed_text
from pinecone_store import init_index, query
from rag_query import generate_answer
import os

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

print("Connecting to Pinecone...")
_index = init_index()
print("Ready.")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/data/<path:filename>")
def serve_data(filename):
    return send_from_directory(DATA_DIR, filename)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = (data or {}).get("message", "").strip()
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        query_vec = embed_text(user_message)
        results = query(_index, query_vec, top_k=3)
        answer = generate_answer(user_message, results)
        media = [
            {
                "content_type": r.get("metadata", {}).get("content_type", ""),
                "source": r.get("metadata", {}).get("source", ""),
                "description": r.get("metadata", {}).get("description", ""),
                "score": r.get("score", 0),
            }
            for r in results
            if r.get("metadata", {}).get("content_type") in ("image", "video")
        ]
        return jsonify({"answer": answer, "media": media})
    except Exception as e:
        return jsonify({"answer": f"⚠️ Error: {str(e)}"}), 200


if __name__ == "__main__":
    app.run(debug=False, port=5000)
