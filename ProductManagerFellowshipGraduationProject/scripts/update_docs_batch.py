import os
import sys

def update_file(path, replacements):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    initial_len = len(content)
    replaced_count = 0
    for old_text, new_text in replacements:
        if old_text in content:
            content = content.replace(old_text, new_text)
            replaced_count += 1
        else:
            print(f"  [MISS] Could not find target in {path}: '{old_text[:50]}...'")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {path}: {replaced_count}/{len(replacements)} replacements applied (length {initial_len} -> {len(content)}).")

# Replacements for docs/architecture.md
arch_replacements = [
    ('RawStore[(AWS S3 Data Lake)]', 'RawStore[(Local Data Lake / AWS S3 Fallback)]'),
    ('Embeddings[OpenAI / Claude Embeddings]', 'Embeddings[HuggingFace MiniLM-L6-v2 Embeddings]'),
    ('VectorDB[(Vector DB: Pinecone / Weaviate)]', 'VectorDB[(Local Vector DB: ChromaDB)]'),
    ('Multi-Agent AI Analysis Layer [n8n Orchestration]', 'Multi-Agent AI Analysis Layer [Python Pipeline Orchestrator]'),
    ('MultiLLM[Multi-LLM Consensus: 2/3 Rule GPT + Claude + Gemini]', 'MultiLLM[Multi-LLM Consensus: 2/3 Rule Groq + HF Llama + Open Models]'),
    ('OpenAI `text-embedding-3-small`** or **Claude embeddings', 'Sentence-Transformers `sentence-transformers/all-MiniLM-L6-v2`** (Hugging Face / Open Source)'),
    ('Pinecone / Weaviate', 'ChromaDB / FAISS (Local Vector Database)'),
    ('Pinecone/Weaviate', 'ChromaDB/FAISS'),
    ('s3://blinkit-discovery-engine-raw/', 'data/raw/ (with optional s3://blinkit-discovery-engine-raw/ fallback)'),
    ('GPT-4o**, **Claude 3.5 Sonnet**, and **Gemini 1.5 Pro', 'Groq Llama-3.1**, **HuggingFace Llama-3.2**, and **Free Open Models'),
    ('GPT-4o', 'Groq Llama-3.1'),
    ('Claude 3.5 Sonnet', 'HuggingFace Llama-3.2'),
    ('Gemini 1.5 Pro', 'Free Open-Source Model'),
    ('claude_3_5', 'hf_llama_3_2'),
    ('gemini_1_5', 'open_model'),
    ('OpenAI `gpt-4o`, Anthropic `claude-3-5-sonnet`, Google `gemini-1.5-pro`', 'Groq API (`llama-3.1-8b-instant`), HuggingFace API (`meta-llama/Llama-3.2-3B-Instruct`), Free Open Models'),
    ('OpenAI `text-embedding-3-small` + Pinecone / Weaviate', 'Sentence-Transformers (`all-MiniLM-L6-v2`) + Local ChromaDB (`data/vectorstore`)'),
    ('AWS S3 (`s3://blinkit-discovery-engine-raw/`)', 'Local Data Lake (`data/raw/`) + AWS S3 fallback'),
    ('OpenAI/Claude vector index (Pinecone/Weaviate)', 'HuggingFace MiniLM vector index (Local ChromaDB)'),
    ('2/3 Consensus Engine (GPT-4o + Claude + Gemini)', '2/3 Consensus Engine (Groq Llama-3.1 + HF Llama-3.2 + Free Open Models)'),
    ('Multi-LLM client (OpenAI, Anthropic, Gemini, Groq)', 'Multi-LLM client (Groq, HuggingFace Inference API, Free Open Models)'),
    ('n8n_orchestrator.py', 'orchestrator.py'),
    ('2/3 Rule: GPT + Claude + Gemini', '2/3 Rule: Groq Llama-3.1 + HF Llama-3.2 + Free Open Models'),
    ('built using Python / n8n workflows', 'built using Python pipeline orchestrator'),
    ('n8n / Python Orchestrator', 'Python Pipeline Orchestrator (orchestrator.py)')
]

# Replacements for docs/implementation-plan.md
impl_replacements = [
    ('Save raw ingestion payloads to AWS S3 Raw Data Lake', 'Save raw ingestion payloads to Local Data Lake (data/raw/) / AWS S3 Fallback'),
    ('Vectorize cleaned records (OpenAI/Claude) & index in Vector DB (Pinecone/Weaviate)', 'Vectorize cleaned records (HuggingFace MiniLM) & index in Local Vector DB (ChromaDB)'),
    ('2/3 majority rule across GPT-4o, Claude 3.5, Gemini 1.5', '2/3 majority rule across Groq Llama-3.1, HuggingFace Llama-3.2, Free Open Models'),
    ('End-to-end n8n workflow pipeline reproducibility via CLI', 'End-to-end Python workflow pipeline reproducibility via CLI'),
    ('OpenAI/Claude vector index (Pinecone/Weaviate)', 'HuggingFace MiniLM vector index (Local ChromaDB)'),
    ('2/3 Consensus Engine (GPT-4o + Claude + Gemini)', '2/3 Consensus Engine (Groq Llama-3.1 + HF Llama-3.2 + Free Open Models)'),
    ('Multi-LLM client (OpenAI, Anthropic, Gemini, Groq)', 'Multi-LLM client (Groq, HuggingFace Inference API, Free Open Models)'),
    ('n8n_orchestrator.py', 'orchestrator.py'),
    ('Pinecone / Weaviate', 'ChromaDB / FAISS (Local Vector Database)'),
    ('Pinecone/Weaviate', 'ChromaDB/FAISS'),
    ('OpenAI `text-embedding-3-small`** or **Claude embeddings', 'Sentence-Transformers `sentence-transformers/all-MiniLM-L6-v2`** (Hugging Face / Open Source)'),
    ('GPT-4o**, **Claude 3.5 Sonnet**, and **Gemini 1.5 Pro', 'Groq Llama-3.1**, **HuggingFace Llama-3.2**, and **Free Open Models'),
    ('GPT-4o, Claude 3.5, and Gemini 1.5', 'Groq Llama-3.1, HuggingFace Llama-3.2, and Free Open Models'),
    ('GPT-4o, Claude 3.5, Gemini 1.5', 'Groq Llama-3.1, HuggingFace Llama-3.2, Free Open Models'),
    ('AWS S3 Raw Data Lake', 'Local Data Lake (data/raw/) & AWS S3 Fallback'),
    ('s3://blinkit-discovery-engine-raw/', 'data/raw/ (with optional s3://blinkit-discovery-engine-raw/ fallback)'),
    ('Full n8n workflow execution', 'Full Python multi-agent pipeline execution'),
    ('80,000+ total records to provide a massive raw data bucket buffer', '157,630 raw records collected across 10 multi-source channels (Play Store, App Store, Reddit, Twitter, YouTube, Quora, Forums, Zepto, Instamart, Tickets)'),
    ('80,000+ raw records capacity', '157,630 raw records ingested dataset'),
    ('GPT-4o', 'Groq Llama-3.1'),
    ('Claude 3.5', 'HuggingFace Llama-3.2'),
    ('Gemini 1.5', 'Free Open Model')
]

update_file('docs/architecture.md', arch_replacements)
update_file('docs/implementation-plan.md', impl_replacements)
