import sys

with open('docs/architecture.md', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

replacements = [
    ('- **Groq Llama-3.1** (OpenAI)', '- **Groq Llama-3.1** (Groq API)'),
    ('- **HuggingFace Llama-3.2** (Anthropic)', '- **HuggingFace Llama-3.2** (Hugging Face Inference API)'),
    ('- **Free Open-Source Model** (Google DeepMind)', '- **Free Open-Source Model** (Hugging Face / Open Models)'),
    ('"gpt_4o": true,', '"groq_llama_3_1": true,'),
    ('"gpt_4o_approved": true,', '"groq_llama_3_1_approved": true,'),
    ('Embeddings (OpenAI) + Vector Indexing (Pinecone)', 'Embeddings (Sentence-Transformers MiniLM) + Local Vector Indexing (ChromaDB)'),
    ('OpenAI `text-embedding-3-small` + ChromaDB / FAISS (Local Vector Database)', 'Sentence-Transformers `sentence-transformers/all-MiniLM-L6-v2` + Local ChromaDB (`data/vectorstore`)'),
    ('[Browser] ──> [Vercel (React SPA)] ──> [Railway (FastAPI)] ──> [AWS S3 / Pinecone]', '[Browser] ──> [Vercel (React SPA)] ──> [FastAPI Backend] ──> [Local Data Lake / ChromaDB]'),
    ('└──> [Multi-LLM APIs (OpenAI / Claude / Gemini)]', '└──> [Multi-LLM APIs (Groq / HuggingFace Inference / Open Models)]'),
    ('OpenAI/Claude vector index (ChromaDB/FAISS)', 'Sentence-Transformers MiniLM vector index (ChromaDB/FAISS)'),
    ('2/3 Consensus Engine (Groq Llama-3.1 + Claude + Gemini)', '2/3 Consensus Engine (Groq Llama-3.1 + HF Llama-3.2 + Free Open Models)'),
    (
        'Raw feedback from 10 channels (App Store, Play Store, Reddit, Twitter, YouTube, Quora, Consumer Forums, Blinkit, Zepto, Instamart) is stored in an AWS S3 Data Lake, cleaned, vectorized via OpenAI/Claude embeddings, and indexed in Pinecone/Weaviate.',
        'Raw feedback from 10 channels (App Store, Play Store, Reddit, Twitter, YouTube, Quora, Consumer Forums, Blinkit, Zepto, Instamart) totalling 157,630 raw reviews is cleaned down to 5,320 high-quality records, vectorized via Sentence-Transformers (MiniLM-L6-v2) embeddings, and indexed in a local ChromaDB vector store.'
    ),
    (
        'through a **Multi-LLM Consensus Engine** ($\ge 2/3$ agreement across GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro)',
        'through a **Multi-LLM Consensus Engine** ($\ge 2/3$ agreement across Groq Llama-3.1, HuggingFace Llama-3.2, and Free Open Models)'
    )
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
    else:
        print(f"MISS: {old[:50]}")

with open('docs/architecture.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished updating architecture.md")
