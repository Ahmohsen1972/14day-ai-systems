import os
import glob
from dotenv import load_dotenv
from openai import OpenAI
from src.rag_core import (
    chunk_text,
    embed_texts,
    retrieve,
    answer_with_context
)
 
DOCS_PATH = "data/docs"
 
 
def load_documents():
    docs = []
    for path in glob.glob(f"{DOCS_PATH}/*.txt"):
        size = os.path.getsize(path) / (1024 * 1024)
        print(f"{path} → {size:.2f} MB")        
        with open(path, "r", encoding="utf-8") as f:
            docs.append(f.read())
    return docs
 
 
def main():
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 
    print("Loading documents...")
    raw_docs = load_documents()
 
    print("Chunking documents...")
    chunks = []
    for doc in raw_docs:
        chunks.extend(chunk_text(doc))
 
    print("Embedding documents...")
    doc_vectors = embed_texts(client, chunks)
 
    print("\nDocument-Aware AI Assistant (type 'exit' to quit)\n")
 
    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
 
        query_vec = embed_texts(client, [question])[0]
        context_chunks = retrieve(query_vec, doc_vectors, chunks)
        answer = answer_with_context(client, question, context_chunks)
 
        print("\nAssistant:")
        print(answer)
        print("\n" + "-" * 40 + "\n")
 
 
if __name__ == "__main__":
    main()