from openai import OpenAI
from rag import collection, embedding_model
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

question = input("سوال شما: ")

# پیدا کردن اطلاعات مرتبط در RAG
question_embedding = embedding_model.encode(
    [question]
).tolist()

results = collection.query(
    query_embeddings=question_embedding,
    n_results=2
)

context = "\n".join(results["documents"][0])

# فرستادن اطلاعات پیدا شده به LLM
prompt = f"""
تو دستیار هوش مصنوعی مجموعه TRAIN هستی.

فقط بر اساس اطلاعات زیر پاسخ بده.
اگر پاسخ در اطلاعات وجود ندارد، صادقانه بگو اطلاعات کافی در اختیار نداری
و چیزی را حدس نزن.

اطلاعات TRAIN:
{context}

سؤال کاربر:
{question}
"""

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\nپاسخ Assistly:")
print(response.choices[0].message.content)