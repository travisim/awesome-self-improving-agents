# Agent Memory & Self-Learning Benchmark Suite

Standardized benchmarks for evaluating autonomous agent memory retrieval, fact updating, and test-time learning capabilities.

---

## 📐 Benchmark Metrics

### 1. Contradiction & Overwrite Fidelity (COF)
* **Dataset:** `benchmarks/dataset/contradiction_overwrite.json`
* **Test:** Simulates user changes of preferences, API endpoints, or database configurations across turns.
* **Score:** Percentage of test cases where the agent answers with the *updated* fact instead of the *stale* fact.

### 2. Needle-in-Multi-Turn Session (NIMS)
* **Dataset:** `benchmarks/dataset/needle_in_multiturn.json`
* **Test:** Buries critical operational constraints (e.g. `--rate-limit=50`, `use_utc=true`) across long, noisy multi-turn conversations (20, 50, and 100 turns).
* **Score:** Recall accuracy when prompted for the constraint after 100 turns.

### 3. Cross-Session Skill Transfer (CSST)
* **Dataset:** `benchmarks/dataset/cross_session_transfer.json`
* **Test:** Tests whether an agent remembers and executes a custom skill taught in Session 1 when prompted in an independent Session 2.

---

## 🚀 Running the Evaluator

Run the deterministic benchmark evaluator:
```bash
python3 benchmarks/runner/eval_memory.py --dry-run
```
