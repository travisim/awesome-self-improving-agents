# Landscape: Who Improves What, and How

A comparison of the frameworks in this list along the axes from [self-improvement-loop.md](self-improvement-loop.md). Descriptions reflect each project's public documentation; where a capability is unproven or not shipped, that is stated rather than assumed.

> **Read this as a map, not a scoreboard.** "Locus of update" describes the mechanism a project provides — it does not guarantee that agents built on it measurably improve. Only reproducible runs settle that.

---

## Comparison matrix

| Project | Primary mechanism | Locus of update | Verification built in? | Persistence | Best fit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mem0** | Extract → dedupe → update facts per user | Episodic + semantic store | No (retrieval quality only) | Cross-session, per-tenant | Personalized assistants with many users |
| **Zep / Graphiti** | Temporal knowledge graph with validity intervals | Semantic graph | No | Cross-session, time-aware | Facts that change over time (billing, ownership, config) |
| **Letta** | OS-style context paging; self-editing memory blocks | Working + archival memory | No | Cross-session | Long-running agents that must manage their own context |
| **Cognee** | Deterministic ECL pipelines into a graph | Semantic graph | Partial (pipeline determinism) | Cross-session | Teams that need repeatable graph construction |
| **HippoRAG** | KG + Personalized PageRank over passages | Semantic (retrieval) | Retrieval benchmarks | Rebuildable index | Multi-hop QA over large corpora |
| **LangMem** | Memory tools for LangGraph state | Episodic + profile | No | Cross-session | LangGraph-native apps |
| **Voyager** | Automatic curriculum + skill library | Procedural (code) | Yes — environment feedback | Skill library | Open-ended task domains with a simulator |
| **ExpeL** | Cross-task insight extraction | Context/insight bank | Task success only | Cross-task | Repeated similar task families |
| **Agent Workflow Memory** | Induces reusable workflows from traces | Procedural (workflows) | Task success only | Cross-session | Web/navigation agents |
| **DSPy** | Compiles prompts/programs against a metric | Prompt/program | Yes — your metric | Until recompile | Pipelines with a measurable objective |
| **TextGrad** | Natural-language "gradients" through a program | Prompt/program | Depends on objective | Until recompile | Optimizing multi-component LLM systems |
| **SWE-agent** | Agent-computer interface tuned for repos | Tools + context | Yes — test suites | Per-run | Software engineering tasks |
| **OpenHands** | Execution-feedback loop on real machines | Context + tools | Yes — execution | Per-run (state can persist) | General software agents |
| **Gödel Agent / ADAS** | Search over agent code | Agent source | Yes — task metric | Until re-search | Research on agent design search |
| **Darwin Gödel Machine** | Evolutionary search over self-modifying agents | Agent code | Yes — benchmarks | Lineage archived | Open-ended self-improvement research |

---

## Reading the matrix

### "Verification built in?" is the column that matters most

A framework that only stores memory (Mem0, Zep, Letta, LangMem) gives you **the substrate for improvement but not the loop**. You still need a verifier and a commit/rollback policy. Frameworks with an execution loop (SWE-agent, OpenHands, Voyager) close the loop by construction but are domain-bound.

### Persistence is not the same as durability

- A **fact in a vector store** persists but is silently degraded by supersession problems.
- A **skill in a code registry** persists and is reviewable — but rots if never re-verified.
- A **compiled prompt** persists until the model version changes, at which point it may need recompiling.

### The strongest production pattern today

Most teams that report real gains combine **two** rungs:

```text
episodic store (rung 1)  +  skill library (rung 4)  +  test suite as verifier
```

- Memory supplies *context* about this user/task.
- Skills supply *executable procedure*.
- Tests supply *truth*.

Weight-level self-training (rung 5) is deliberately last: it is the most expensive, hardest to roll back, and requires a signal strong enough to justify retraining.

---

## Where each project stops

| Project | What it does not do |
| :--- | :--- |
| Mem0 / Zep / Letta / LangMem | Do not decide *whether a lesson changed behavior*; no verifier, no regression gate |
| HippoRAG / Cognee | Build indexes; they do not run an improvement loop |
| Voyager / ExpeL / AWM | Improve within a task family; transfer outside it is unproven |
| DSPy / TextGrad | Optimize artifacts offline; no runtime learning from failures unless you wire it |
| SWE-agent / OpenHands | Excellent per-run feedback loop; cross-session accumulation is left to you |
| Gödel Agent / DGM | Research prototypes; compute-heavy; results are benchmark-specific |

The gap this repo is built around: **almost nothing ships a turnkey "commit lesson → verify no regression → keep or roll back" loop.** That is the missing middleware, and the benchmarks here are meant to make it measurable.

---

## Selecting a stack

| If you need… | Start with | Add |
| :--- | :--- | :--- |
| Per-user personalization | Mem0 or LangMem | COF scenarios from this repo |
| Facts with history | Zep / Graphiti | Supersession tests (COF) |
| Long-running autonomy | Letta | Write-policy limits + pruning |
| Multi-hop knowledge | HippoRAG or Cognee | Graph extraction quality checks |
| Repo-level coding tasks | SWE-agent or OpenHands | Skill extraction from successful patches |
| Prompt optimization | DSPy or TextGrad | Held-out eval + regression suite |

---

## Contributing to this comparison

PRs that correct a row must link to the project's documentation or a reproducible run. Claims without a citation or a harness will be marked *unverified* rather than merged as fact.
