import pathlib
from embedder import embed_text, embed_image, embed_video
from pinecone_store import init_index, upsert_item, query
from rag_query import generate_answer

SAMPLE_TEXT = (
    "Python is a versatile, high-level programming language widely used in data science, "
    "machine learning, web development, and automation. Its simple syntax makes it great "
    "for beginners while remaining powerful enough for production systems."
)


def index_content(index):
    print("\n--- Indexing content ---")

    # Text
    print("Embedding text sample...")
    vec = embed_text(SAMPLE_TEXT)
    upsert_item(index, "text-001", vec, {
        "content_type": "text",
        "source": "sample_text",
        "description": SAMPLE_TEXT[:120],
    })
    print("  text-001 indexed.")

    # Images — pick up any .jpg / .jpeg / .png in the data/ subfolder
    data_dir = pathlib.Path("data")
    image_paths = (
        list(data_dir.glob("*.jpg"))
        + list(data_dir.glob("*.jpeg"))
        + list(data_dir.glob("*.png"))
    )
    if image_paths:
        for i, img_path in enumerate(image_paths, 1):
            item_id = f"image-{i:03}"
            print(f"Embedding image: {img_path} -> {item_id}...")
            vec = embed_image(str(img_path))
            upsert_item(index, item_id, vec, {
                "content_type": "image",
                "source": img_path.name,
                "description": f"Image: {img_path.name}",
            })
            print(f"  {item_id} indexed.")
    else:
        print("  No images found — drop .jpg / .png files here to index them.")

    # Videos — pick up any .mp4 / .mov in the data/ subfolder (max 120 s each)
    video_paths = (
        list(data_dir.glob("*.mp4"))
        + list(data_dir.glob("*.mov"))
    )
    if video_paths:
        for i, vid_path in enumerate(video_paths, 1):
            item_id = f"video-{i:03}"
            print(f"Embedding video: {vid_path} -> {item_id}...")
            vec = embed_video(str(vid_path))
            upsert_item(index, item_id, vec, {
                "content_type": "video",
                "source": vid_path.name,
                "description": f"Video: {vid_path.name}",
            })
            print(f"  {item_id} indexed.")
    else:
        print("  No videos found — drop .mp4 / .mov files here to index them.")


def run_query(index, user_query: str):
    print(f"\n--- Query: '{user_query}' ---")
    query_vec = embed_text(user_query)
    results = query(index, query_vec, top_k=3)

    if not results:
        print("No results returned from Pinecone.")
        return

    print("Top matches:")
    for r in results:
        meta = r.get("metadata", {})
        print(f"  [{r['score']:.3f}] {r['id']} | {meta.get('content_type','?')} | {meta.get('description','')[:80]}")

    print("\nGenerating answer via OpenRouter...")
    answer = generate_answer(user_query, results)
    print(f"\nAnswer:\n{answer}")


def main():
    print("Initializing Pinecone index...")
    index = init_index()
    print("  Ready.")

    index_content(index)

    run_query(index, "What is Python used for?")
    run_query(index, "Show me something visual")


if __name__ == "__main__":
    main()
