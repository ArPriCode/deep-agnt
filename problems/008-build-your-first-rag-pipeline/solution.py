def answer(question, documents, model, k=3):
    chunks = []
    for doc in documents:
        chunks.extend(chunk_document(doc, 40, 10))

    if not chunks:
        prompt = f"Question: {question}"
        return model.ask(prompt)

    chunk_vecs = embed(chunks)
    question_vec = embed([question])[0]

    scores = chunk_vecs @ question_vec
    top_indices = np.argsort(scores)[::-1][:k]
    top_chunks = [chunks[i] for i in top_indices]

    context = "\n\n".join(top_chunks)
    prompt = f"Context:\n{context}\n\nQuestion: {question}"
    return model.ask(prompt)
