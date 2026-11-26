# Self-Improvement Benchmark Suite

Standardized, inspectable benchmarks for whether an agent **changes its behavior** based on experience — not just whether it can retrieve a chunk.

> **Honesty note:** this suite ships *datasets + schema validation + an adapter interface*. It does not ship a model harness, and it does not print scores it did not compute. Any number you see must come from an adapter run you executed.

---

## Metrics

### 1. COF — Contradiction & Overwrite Fidelity ✅

**Question:** when a fact is superseded mid-history, does the agent answer with the *current* fact?

**Dataset:** [`dataset/contradiction_overwrite.json`](dataset/contradiction_overwrite.json)

Each case defines:

| Field | Meaning |
| :--- | :--- |
| `turn_initial` | the (later stale) fact stated early |
| `turn_update` | the contradicting statement made later |
| `query` | the question asked after both |
| `expected_answer` | the post-update truth |
| `stale_trap` | the answer that indicates the agent used the stale fact |

**Score:** `correct_with_update / total`. A system that ignores updates can score at most the share of cases where the stale value happens to be right — track that as the trivial baseline.

**Failure signature:** returning `stale_trap` means retrieval ranked an older, equally-similar chunk above the newer one. This is the canonical memory defect.

---

### 2. NIMS — Needle in Multi-Turn Session ✅

**Question:** can the agent recall a specific constraint injected far back in a noisy session?

**Dataset:** [`dataset/needle_in_multiturn.json`](dataset/needle_in_multiturn.json)

| Field | Meaning |
| :--- | :--- |
| `needle` | the exact constraint text (e.g. a rate limit, a timezone flag) |
| `injected_turn` | which turn it appeared at |
| `total_turns` | session length (20 / 50 / 100) |
| `query` | the later question that depends on it |
| `expected_value` | the literal value that must be recovered |

**Score:** recall accuracy bucketed by `total_turns`, so you can see degradation as distance grows rather than a single averaged number that hides it.

---

### 3. CSST — Cross-Session Skill Transfer ✅

**Question:** does a skill taught in session 1 actually execute in session 2?

**Dataset:** [`dataset/cross_session_transfer.json`](dataset/cross_session_transfer.json)

| Field | Meaning |
| :--- | :--- |
| `skill_name` | identifier for the taught procedure |
| `session_1_teaching` | the instruction describing the procedure |
| `session_2_task` | an independent request requiring it |
| `expected_command` | the concrete command/artifact proving it was applied |

**Score:** `successful_transfers / total`. Requires a fresh session boundary between the two — running both in one context invalidates the test.

---

### 4. VSCE — Verbal Self-Correction Efficiency 🚧 *wanted*

**Question:** how many reflection iterations does an agent need to converge, and does it converge at all?

**Status:** spec below, dataset not yet implemented — tracked in [issue #7](https://github.com/travisim/awesome-self-improving-agents/issues).

**Proposed record:**

```json
{
  "id": "vsce-001",
  "task": "...",
  "initial_failure": "...",
  "verifier": "pytest tests/test_x.py",
  "max_iterations": 4,
  "expected_convergence_iteration": 2,
  "degenerate_critiques": ["try again", "be more careful"]
}
```

**Proposed score:** `iterations_to_convergence` per task, plus `convergence_rate`, plus a *degenerate-reflection rate* (critiques that do not change the next action). That last one is the real signal: an agent that "reflects" for four turns and reruns the identical command is not reflecting.

---

## Adapter interface

To measure anything, implement `MemoryAdapter` from [`runner/adapters/base.py`](runner/adapters/base.py):

```python
from benchmarks.runner.adapters.base import MemoryAdapter

class MyAdapter(MemoryAdapter):
    name = "my-memory-backend"

    def store(self, key: str, value: str, metadata: dict) -> None: ...
    def retrieve(self, query: str, limit: int = 5) -> list[str]: ...
    def update(self, key: str, new_value: str) -> None: ...
    def reset(self) -> None: ...
```

Requirements:

1. `retrieve` must return the *stored values* (strings), most relevant first.
2. `reset` must fully clear state between sessions — CSST depends on it.
3. Adapters must not call an LLM. The adapter is the memory backend; the agent under test is separate.

---

## Running

```bash
# validate every dataset against its schema (CI runs this)
python3 benchmarks/runner/eval_memory.py --validate

# describe what's in each dataset
python3 benchmarks/runner/eval_memory.py --list

# corpus statistics
python3 benchmarks/runner/eval_memory.py --stats

# show discoverable adapters
python3 benchmarks/runner/eval_memory.py --list-adapters
```

Exit code is non-zero on any schema error, so CI fails loudly instead of silently passing.

---

## Adding scenarios

1. Append to the relevant JSON array — keep existing records intact.
2. Required keys are enforced by the validator; unknown keys are allowed.
3. IDs must be unique and prefixed (`cof-`, `nims-`, `csst-`).
4. Open a PR; CI validates the schema automatically.

Guidelines: prefer realistic, specific facts over toy placeholders; make the `stale_trap` genuinely tempting (a case so obvious that no system could fail it measures nothing).
