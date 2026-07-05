# Caramel Assistant — Product Features

The Caramel Assistant offers the following core features:

**Instant Knowledge Retrieval.** The assistant indexes a customer's help
center articles, PDF manuals, and past support tickets, then retrieves the
most relevant passages to ground every answer, reducing hallucinated
responses.

**Multi-language Support.** Caramel Assistant can answer questions in 18
languages, automatically detecting the customer's language from their first
message.

**Human Handoff.** If the assistant's confidence score for an answer falls
below a configurable threshold (default 0.62), the conversation is
automatically escalated to a human support agent with the full chat history
attached.

**Citation Mode.** Every answer can optionally include inline citations
linking back to the exact source document and section used to generate the
response, which is important for regulated industries like fintech.

**Analytics Dashboard.** Administrators get a dashboard showing the most
common customer questions, unanswered questions ("knowledge gaps"), and
average resolution time.

**Integrations.** Caramel Assistant integrates natively with Zendesk,
Intercom, Salesforce Service Cloud, and Slack, and exposes a REST API for
custom integrations.

The assistant is built on a retrieval-augmented generation (RAG) architecture:
incoming questions are embedded, matched against a vector index of the
knowledge base, and the retrieved passages are passed to a large language
model to produce a grounded answer.
