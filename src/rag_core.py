import os
import json
import numpy as np
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
 
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
 
 
def chunk_text(text: str, size: int = 800, overlap: int = 100):
    text = " ".join(text.split())
    chunks = []
    start = 0

    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])

        if end == len(text):
            break   

        start = end - overlap
        if start < 0:
            start = 0

    return chunks

def embed_texts(client: OpenAI, texts: List[str]) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vectors = np.array([d.embedding for d in resp.data])
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors
 
 
def retrieve(query_vec, doc_vecs, docs, k=5):
    scores = doc_vecs @ query_vec
    top = np.argsort(-scores)[:k]
    return [docs[i] for i in top]
 
 
def answer_with_context(client: OpenAI, question: str, context_chunks: List[str]) -> str:
    context = "\n\n".join(context_chunks)
 
    system_prompt = (
        "You are a document-aware AI assistant.\n"
        "Answer using ONLY the provided context.\n"
        "If the answer is not in the context, say you do not have enough information.\n"
    )
 
    user_prompt = f"""
QUESTION:
{question}
 
CONTEXT:
{context}
"""
 
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=400,
    )
 
    return resp.choices[0].message.content.strip()