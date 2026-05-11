"""
Drop new images / videos into the data/ folder, then run:
    python index_media.py
Each file is indexed using its filename as the Pinecone ID, so re-running
is safe — existing entries are updated in place, nothing is duplicated.
"""
import pathlib
from embedder import embed_image, embed_video
from pinecone_store import init_index, upsert_item

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm"}

DATA_DIR = pathlib.Path("data")


def index_all():
    print("Connecting to Pinecone...")
    index = init_index()
    print("Ready.\n")

    files = sorted(DATA_DIR.iterdir()) if DATA_DIR.exists() else []
    if not files:
        print("data/ folder is empty. Drop images or videos there and re-run.")
        return

    indexed = 0
    for path in files:
        ext = path.suffix.lower()
        if ext in IMAGE_EXTS:
            print(f"[image] Embedding {path.name} ...")
            vec = embed_image(str(path))
            upsert_item(index, f"img-{path.stem}", vec, {
                "content_type": "image",
                "source": path.name,
                "description": f"Image: {path.name}",
            })
            print(f"        -> indexed as img-{path.stem}")
            indexed += 1

        elif ext in VIDEO_EXTS:
            print(f"[video] Embedding {path.name} ...")
            vec = embed_video(str(path))
            upsert_item(index, f"vid-{path.stem}", vec, {
                "content_type": "video",
                "source": path.name,
                "description": f"Video: {path.name}",
            })
            print(f"        -> indexed as vid-{path.stem}")
            indexed += 1

        else:
            print(f"[skip]  {path.name} (unsupported type)")

    print(f"\nDone. {indexed} file(s) indexed into Pinecone.")
    print("Refresh the chat app and your new media is searchable immediately.")


if __name__ == "__main__":
    index_all()
