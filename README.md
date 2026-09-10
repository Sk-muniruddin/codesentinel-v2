# CodeSentinel v2

> **AI-powered GitHub Pull Request code reviewer with repository-aware RAG**

CodeSentinel v2 is an AI code-review application that automatically reviews GitHub Pull Requests, retrieves relevant existing repository context, and posts a structured review back to the Pull Request.

The project combines **GitHub Apps/Webhooks, FastAPI, Azure Blob Storage, Azure AI Search, Azure AI Foundry IQ, OpenAI Agents SDK, and GPT-5.4**.

---

## What CodeSentinel Does

A Pull Request contains only the proposed changes. A reviewer often needs to understand the existing codebase before deciding whether those changes are correct.

CodeSentinel addresses this by separating two sources of information:

- **GitHub PR diff** — the actual code being proposed.
- **Repository knowledge** — existing repository code synchronized from the `main` branch and indexed for retrieval.

The retrieved repository context and PR diff are then provided to an **OpenAI Agents SDK Agent using GPT-5.4**, which produces a structured code review.

The completed review is posted back to the GitHub Pull Request.

---

## Architecture


                         GitHub
                            │
                            │ Pull Request Webhook
                            ▼
                     ┌──────────────┐
                     │   FastAPI    │
                     │   Webhook    │
                     └──────┬───────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
          GitHub API              Foundry IQ
          PR Diff                 Knowledge Base
                 │                     │
                 │                     ▼
                 │              Azure AI Search
                 │                     │
                 │                     ▼
                 │              Repository Context
                 │              from main branch
                 │                     │
                 └──────────┬──────────┘
                            ▼
                  ┌─────────────────────┐
                  │ OpenAI Agents SDK   │
                  │ CodeSentinel Agent  │
                  └──────────┬──────────┘
                             │
                             ▼
                         GPT-5.4
                             │
                             ▼
                    Structured CodeReview
                             │
                             ▼
                     GitHub PR Review