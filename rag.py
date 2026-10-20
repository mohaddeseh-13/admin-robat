import re

import chromadb
from sentence_transformers import SentenceTransformer


# =========================
# مدل Embedding
# =========================

embedding_model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


# =========================
# دیتابیس برداری
# =========================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="train_knowledge"
)


# =========================
# نرمال‌سازی فارسی
# =========================

def normalize_text(text):
    text = text.lower()

    text = text.replace("ي", "ی")
    text = text.replace("ى", "ی")
    text = text.replace("ك", "ک")

    text = text.replace("‌", " ")
    text = text.replace("ـ", "")

    text = re.sub(r"[؟?!،,.:؛]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================
# بارگذاری اطلاعات
# =========================

def load_knowledge():

    with open(
        "knowledge/train.txt",
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    chunks = [
        chunk.strip()
        for chunk in text.split("\n\n")
        if chunk.strip()
    ]

    embeddings = embedding_model.encode(
        chunks
    ).tolist()

    # دیتابیس قبلی را پاک می‌کنیم
    # تا اطلاعات قدیمی باقی نماند.

    try:
        chroma_client.delete_collection(
            name="train_knowledge"
        )
    except Exception:
        pass

    global collection

    collection = chroma_client.get_or_create_collection(
        name="train_knowledge"
    )

    collection.upsert(
        ids=[
            f"chunk_{i}"
            for i in range(len(chunks))
        ],
        documents=chunks,
        embeddings=embeddings
    )

    print(
        f"{len(chunks)} knowledge chunks loaded."
    )


# =========================
# اجرای اولیه
# =========================

if __name__ == "__main__":

    load_knowledge()