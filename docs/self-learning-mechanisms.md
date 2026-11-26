# Reflection & Skill Synthesis

> **Position in this repo:** Pillars 2 and 3 of the [five pillars](../README.md#-the-five-pillars). Memory stores the lesson (Pillar 1); reflection produces it; skill synthesis turns it into something executable.

Both mechanisms operate **without gradient updates**. They change behavior by changing context, memory, or the tool surface.

---

## 1. Reflection: Verbal Reinforcement

### The loop

```text
1. ACT        agent attempts task -> trajectory T1
2. EVALUATE   environment returns a signal (test failure, compiler error, judge score)
3. DIAGNOSE   agent writes a critique C1 naming a CAUSE and a DIFFERENT next action
4. PERSIST    C1 is written to episodic memory with provenance
5. RETRY      agent re-attempts, conditioned on C1 -> T2
6. VERIFY     did the retry actually succeed?
```

Step 6 is not optional. Without it you are storing hypotheses as if they were lessons.

### What separates a useful critique from noise

| Weak critique | Strong critique |
| :--- | :--- |
| "The test failed." | "`pytest` collected 0 tests because `testpaths` omitted `tests/unit/`." |
| "Be more careful." | "Use `Decimal`, not `float`, for currency fields in this codebase." |
| "Try again." | "The API rejects batch >100; chunk the request before retrying." |

A usable lesson has a **trigger** (when does this apply), a **cause**, an **action**, and **evidence** (the trace that proved it). Store them as structured fields, not free-text blobs — retrieval quality depends on the trigger being explicit.

### Grounding matters more than eloquence

Self-critique with no external anchor tends to converge on plausible-sounding but unfalsifiable advice. Systems that critique *with tools* — running the test, reading the doc, checking the type — produce far more actionable lessons (CRITIC). Practical rule: **if the critique cannot cite an observation, don't persist it as a lesson.** Persist it as a hypothesis instead.

### Reflection budget

Reflection is not free. Each iteration costs tokens and latency, and returns diminish quickly:

- Cap iterations per task (typically 2–4).
- Track **iterations-to-convergence** — this is exactly what **VSCE** is designed to measure.
- If a critique does not change the next action, stop. Repeating identical reflections is a known degenerate loop.

### Anti-patterns

1. **Critique laundering** — rewriting the failure in softer words with no new action.
2. **Scope creep** — a lesson from one repo applied everywhere. Always attach applicability conditions.
3. **Unbounded growth** — thousands of micro-lessons that individually look fine and collectively drown retrieval.
4. **Self-grading** — the same model instance writes the critique and decides it passed.

---

## 2. Skill Synthesis: From Trajectory to Tool

When a task finally succeeds after iteration, the valuable artifact is not the transcript — it is the *generalized procedure*.

### The distillation contract

```text
1. TRIAL      agent struggles; repeated failures produce lessons
2. GATE       all verification passes for the first time
3. ABSTRACT   extract the invariant steps, discard incidental ones
4. TYPING     emit a callable unit (function/tool) with signature + docstring
5. INDEX      embed the description so future agents can find it
6. REGISTER   add to the skill registry with version + provenance
7. SCOPE      record the conditions under which it applies
```

The hard part is step 3. A transcript is a specific path through a specific environment; a skill must capture what generalizes. Over-abstracting yields a useless wrapper; under-abstracting yields a brittle script with hardcoded paths.

### A skill record should answer

```yaml
name: sql-to-prisma-migration
signature: "(schema_path: str, out_dir: str) -> list[str]"
description: "Convert a legacy SQL schema dump into Prisma model files."
preconditions:
  - "Input is a .sql dump, not a live connection string"
  - "Target project already has prisma/schema.prisma"
verified_by:
  - "tests/test_migration.py::test_roundtrip"
provenance:
  source_session: "sess_2026_11_03"
  evidence: "3 successful runs, 0 regressions"
version: 1
```

That record is reviewable in a pull request. That is the point: **procedural memory should be code-reviewed like code**, because it *is* code that will execute later.

### When synthesis is the wrong move

- The task succeeded once, by luck, with no verifier.
- The steps depend on volatile external state (a UI layout, an API that changes weekly).
- The "skill" is a one-liner wrapper around an existing tool — just call the tool.

### Skill libraries rot

A skill that passed in March may be wrong in November. Without an expiry policy, a skill registry becomes a museum of confidently broken procedures. Include a `last_verified` date and re-run the gate periodically.

---

## 3. Consolidation ("Sleep Cycles")

Reflection and synthesis both *add* records. Consolidation is the counterweight:

- **Contradiction resolution** — when two lessons conflict, pick a winner by recency + evidence strength, demote the loser.
- **Entity merging** — collapse `travis`, `Travis Sim`, `user_501` into one entity.
- **Lesson deduplication** — ten lessons saying "chunk large requests" should become one with examples.
- **Promotion** — repeated successful *episodes* become a *semantic* fact; repeated successful *facts* become a *skill*.
- **Pruning** — drop low-utility records; measure utility by retrieval-then-success, not by creation date.

Skipping consolidation is the most common reason a memory system peaks in month one and degrades thereafter.

---

## 4. References

- Shinn et al., *Reflexion* — [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)
- Madaan et al., *Self-Refine* — [arXiv:2303.17651](https://arxiv.org/abs/2303.17651)
- Gou et al., *CRITIC* — [arXiv:2305.11738](https://arxiv.org/abs/2305.11738)
- Wang et al., *Voyager* — [arXiv:2305.16291](https://arxiv.org/abs/2305.16291)
- Zhao et al., *ExpeL* — [arXiv:2308.10144](https://arxiv.org/abs/2308.10144)
- Qian et al., *CREATOR: Tool Creation for LLMs* — [arXiv:2305.14318](https://arxiv.org/abs/2305.14318)
- Qin et al., *ToolLLM* — [arXiv:2307.16789](https://arxiv.org/abs/2307.16789)
- Wang et al., *Agent Workflow Memory* — [arXiv:2409.07429](https://arxiv.org/abs/2409.07429)
