from openai import OpenAI
from config import OPENROUTER_API_KEY

# Free model for testing. Once you add credits at openrouter.ai/settings/credits,
# swap this to "anthropic/claude-opus-4" for the full experience.
_CHAT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

_SYSTEM_PROMPT = (
    "You are a helpful assistant with access to a multimodal knowledge base "
    "containing text, images, and videos. Use the retrieved context below to "
    "answer the user's question accurately and concisely. "
    "Never include markdown image links or file paths in your response — "
    "the interface will display the actual media automatically. "
    "If the context does not contain enough information, say so clearly."
)


def generate_answer(query: str, retrieved: list[dict]) -> str:
    context_lines = []
    for i, item in enumerate(retrieved, 1):
        meta = item.get("metadata", {})
        content_type = meta.get("content_type", "unknown")
        description = meta.get("description", "")
        source = meta.get("source", "")
        score = item.get("score", 0)
        context_lines.append(
            f"{i}. [{content_type}] {description} (source: {source}, relevance: {score:.3f})"
        )

    context = "\n".join(context_lines) if context_lines else "No relevant content found."

    response = _client.chat.completions.create(
        model=_CHAT_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Retrieved context:\n{context}\n\nQuestion: {query}"},
        ],
    )
    return response.choices[0].message.content
