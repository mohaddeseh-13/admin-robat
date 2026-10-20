from rag import collection, embedding_model


question = input("سوال شما: ")

question_embedding = embedding_model.encode(
    [question]
).tolist()

results = collection.query(
    query_embeddings=question_embedding,
    n_results=2
)

print("\nاطلاعات مرتبط:")
for document in results["documents"][0]:
    print("-", document)