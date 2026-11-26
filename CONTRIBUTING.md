# Contributing to Awesome Self-Improving Agents 🔁

Thanks for helping make this a reliable map of how agents actually improve.

This repo optimizes for **signal over volume**. A single well-verified entry is worth more than ten unverified links.

---

## Ways to contribute

### 1. Add a framework

1. It must be open source with a public repository and a license.
2. It must implement a real improvement or memory mechanism — not a thin wrapper.
3. Add a row to the appropriate table in `README.md`:
   - **Memory & context substrates**, or
   - **Improvement loops, skill libraries & agent scaffolds**.
4. Fill every column honestly: mechanism, locus of update, storage/backend, and one specific sentence on why it belongs.
5. Star counts come from the GitHub API, not from memory:

```bash
gh api repos/OWNER/REPO --jq '{stars: .stargazers_count, pushed: .pushed_at}'
```

### 2. Add a paper

- Use one entry per paper, grouped by **where the improvement lands**.
- Required format: `[Short Title](https://arxiv.org/abs/XXXX.XXXXX) | Year | One-sentence contribution.` (replace the placeholder with the real ID)
- Verify the arXiv ID resolves before submitting:

```bash
curl -sSL "https://export.arxiv.org/api/query?id_list=2303.11366" | grep -o '<title>[^<]*</title>' | head -2
```

- Prefer the canonical venue version; link arXiv for access.

### 3. Add benchmark scenarios

Append to the relevant dataset in `benchmarks/dataset/`:

| File | Metric | Prefix |
| :--- | :--- | :--- |
| `contradiction_overwrite.json` | COF | `cof-` |
| `needle_in_multiturn.json` | NIMS | `nims-` |
| `cross_session_transfer.json` | CSST | `csst-` |

Rules:
- IDs unique and prefixed.
- Do not modify or delete existing records in the same PR.
- `expected_answer` must differ from `stale_trap` (the validator enforces this).
- Make the case realistic: a scenario no system could fail measures nothing.

Validate before pushing:

```bash
python3 benchmarks/runner/eval_memory.py --validate
```

### 4. Implement a memory adapter

Create a module in `benchmarks/runner/adapters/` implementing `MemoryAdapter`:

```python
from benchmarks.runner.adapters.base import MemoryAdapter, register_adapter

@register_adapter
class Mem0Adapter(MemoryAdapter):
    name = "mem0"

    def store(self, key, value, metadata=None): ...
    def retrieve(self, query, limit=5): ...
    def update(self, key, new_value): ...
    def reset(self): ...
```

Contract highlights:
- `retrieve` returns stored **values** (strings), most relevant first.
- `reset` fully clears state — cross-session tests depend on a real boundary.
- Adapters must not call an LLM; they are the storage layer only.
- No network calls in CI tests; use a local instance or skip markers.

Check discovery:

```bash
python3 benchmarks/runner/eval_memory.py --list-adapters
```

### 5. Submit a reproducible leaderboard run

The leaderboard is currently **community-reported and unverified**. To replace a row with real data you must provide:

1. A harness script (in-repo or linked).
2. The exact config (model, version, temperature, seeds).
3. Archived logs for **at least 3 seeds**.
4. The eval split used, with held-out tasks excluded from lesson generation.

Only then may a row set `"reproduced": true`. The CI provenance check enforces that unverified rows carry no numeric scores.

---

## Quality bar

A PR is ready when:

- [ ] `python3 benchmarks/runner/eval_memory.py --validate` passes
- [ ] Every added link resolves
- [ ] Claims are either cited or explicitly marked unverified
- [ ] No fabricated numbers, star counts, or benchmark results
- [ ] One logical change per PR

We reject: typo-only PRs, link-dump PRs with no descriptions, marketing copy for closed products, and any benchmark claim without a harness.

---

## Local workflow

```bash
git clone https://github.com/travisim/awesome-self-improving-agents
cd awesome-self-improving-agents
python3 benchmarks/runner/eval_memory.py --validate
python3 benchmarks/runner/eval_memory.py --stats
```

Then branch, commit, push:

```bash
git checkout -b docs/add-zep-deep-dive
git commit -m "docs(memory): add Zep/Graphiti deep dive"
git push -u origin docs/add-zep-deep-dive
gh pr create --fill
```

Commit style: `docs:`, `feat:`, `fix:`, `test:`, `ci:`.

---

## Review

Maintainers review within a few days. If a PR goes quiet, a single polite ping is welcome — repeated pings are not.
