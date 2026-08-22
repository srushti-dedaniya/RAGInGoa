# RAGInGoa

> **A multilingual, voice-enabled Retrieval-Augmented Generation system for intelligent question answering.**

RAGInGoa is a voice-first RAG system built for **Hacker House Goa 2026 — Task 2**. It combines speech recognition, semantic retrieval, vector search, LLM-based generation, and guardrails into a single conversational pipeline.

Users can ask questions through **voice or text** in **English, Hindi, or Marathi** and receive context-aware responses through an intelligent routing pipeline.

---

## Overview

RAGInGoa is designed around a simple principle:

> **Retrieve when relevant context exists. Generate naturally when it doesn't.**

The system determines whether a query is relevant to the provided knowledge base.

- **RAG-relevant query** → semantic retrieval → grounded answer
- **General query** → LLM-based response
- **Unsafe / invalid query** → guardrail handling

This prevents the system from blindly answering every question through retrieval while maintaining grounded responses for knowledge-base queries.

---

## Architecture

```text
                    ┌─────────────────┐
                    │      User       │
                    │   Voice / Text  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Sarvam STT    │
                    │ Speech-to-Text  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Query Router   │
                    └────────┬────────┘
                             │
                   ┌──────────┴──────────┐
                   ▼                     ▼
            RAG Relevant            General Query
                   │                     │
                   ▼                     ▼
            Query Embedding             LLM
                   │                     │
                   ▼                     │
             FAISS Search                │
                   │                     │
                   ▼                     │
            Retrieved Context            │
                   │                     │
                   ▼                     │
           Grounded Generation           │
                   │                     │
                   └──────────┴──────────┘
                             ▼
                    ┌─────────────────┐
                    │    Guardrails   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Final Answer   │
                    │   + Listen      │
                    └─────────────────┘
```
