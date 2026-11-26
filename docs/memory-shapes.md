# Architectural Guide: The Four Shapes of Agent Memory

Memory in autonomous agent systems is not a simple key-value store or vector index. Effective agents utilize a multi-tier memory hierarchy inspired by human cognitive science.

---

## 1. Working Memory (Active Buffer / Scratchpad)

### Definition
Working memory is the information actively held in the model's immediate attention span (KV-cache and system prompt).

### Characteristics
* **Substrate:** In-context tokens, scratchpads, tool invocation logs, and internal chain-of-thought traces.
* **Latency:** Instantaneous ($O(1)$ tool lookup, attention over existing tokens).
* **Failure Modes:**
  * *Context Rot:* As context exceeds 30k–50k tokens, attention to earlier instructions degrades.
  * *Distraction:* Irrelevant past turns degrade reasoning accuracy.

### Best Practices
* Keep system prompts lean and modular.
* Use sliding context windows with periodic deterministic summarization.

---

## 2. Episodic Memory (Experience & History)

### Definition
Episodic memory stores temporal records of past events, conversations, and agent experiences.

### Characteristics
* **Substrate:** Vector databases (embeddings), SQLite/Postgres chronological logs.
* **Query Paradigm:** Semantic similarity (`cos(q, doc)`) filtered by recency and relevance score.
* **Leading Frameworks:** [Mem0](https://github.com/mem0ai/mem0), [Letta](https://github.com/letta-ai/letta), [Zep](https://github.com/getzep/zep).

### Key Challenge: The Contradiction Dilemma
When an episodic memory store retrieves facts via pure cosine similarity, contradictory statements (e.g., Turn 5: *"User prefers AWS"* vs. Turn 80: *"User switched to GCP"*) often return with equal similarity scores, causing the agent to hallucinate or stall.

---

## 3. Semantic Memory (Knowledge Graphs & Entity Relational)

### Definition
Semantic memory organizes structured, factual knowledge independent of the specific episode in which it was learned.

### Characteristics
* **Substrate:** Entity-Relationship Knowledge Graphs (e.g., Neo4j, NetworkX, LanceDB Graph).
* **Representation:** Triples: `(Entity) -> [Relation] -> (Entity)`.
* **Leading Frameworks:** [HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG), [Cognee](https://github.com/topoteretes/cognee), Microsoft GraphRAG.

### Why Graphs Excel Over Dense Vectors
* **Multi-hop reasoning:** Discovering relationships like *"Alice works at Company X, which uses Tool Y"*.
* **Deterministic updates:** Updating an edge `(Company X, uses_database, CockroachDB)` instantly invalidates the previous relation without re-embedding entire conversation histories.

---

## 4. Procedural Memory (Skill Libraries & Reusable Workflows)

### Definition
Procedural memory represents "how to do things"—executable skills, workflow routines, and tool configurations compiled from past successes.

### Characteristics
* **Substrate:** Code repositories, AST trees, tool schema registries, compiled DSPy modules.
* **Inspiration:** [Voyager](https://github.com/MineDojo/Voyager) (autonomous Minecraft skill bank), [ExpeL](https://github.com/LeapLabTHU/ExpeL).
* **Mechanism:** When an agent solves a complex problem via iterative trial and error, it encapsulates the final working sequence into a reusable tool or prompt recipe.
