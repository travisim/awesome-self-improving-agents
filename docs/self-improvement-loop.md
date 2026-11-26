# The Self-Improvement Loop: A Working Specification

This document defines what this project means by *self-improving agent* and gives a vocabulary for comparing systems that otherwise get lumped together under "agent memory."

---

## 1. Definition

> An agent **self-improves** when its policy for future tasks changes as a consequence of its own experience, evaluated on held-out tasks, without a human relabeling the training data in between.

Every clause matters:

| Clause | Excludes |
| :--- | :--- |
| *policy for future tasks changes* | Retrieval-only systems whose actions are unchanged |
| *as a consequence of its own experience* | Static fine-tuning on a fixed human corpus |
| *evaluated on held-out tasks* | Memorizing the exact instance it failed on |
| *without human relabeling* | Standard supervised training loops |

Memory is one mechanism for satisfying the first clause. It is not sufficient: a retriever that surfaces the right lesson but leaves the action distribution intact has closed no loop.

---

## 2. The Five Axes

### 2.1 Signal source

How does the agent know an attempt was bad?

1. **Executable verifier / environment** — tests, compilers, type checkers, schemas, game state. Strongest signal, narrow applicability.
2. **Tool-grounded critique** — a critic with access to real tools checks claims (CRITIC). Middle ground.
3. **LLM self-critique** — the model critiques itself with no external anchor (Reflexion, Self-Refine). Cheap, broad, gamed easily.
4. **Reward model** — learned preference proxy. Inherits the reward model's blind spots.
5. **Human feedback** — highest quality, lowest throughput.

**Design rule:** prefer the strongest signal that covers your task distribution. If the only signal is LLM self-critique, assume the agent can converge on confidently wrong behavior and require an external periodic audit.

### 2.2 Locus of update — the improvement ladder

Where the change physically lands determines cost, latency, persistence, and blast radius.

| Rung | Substrate | Write cost | Read latency | Persistence | Blast radius |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | Working context / scratchpad | ~0 | in-context | one turn | none |
| 1 | Episodic memory store | low | retrieval hop | cross-session | retrieval quality |
| 2 | Semantic memory / knowledge graph | medium (extraction) | graph query | cross-session | fact correctness |
| 3 | Prompt / program (DSPy, TextGrad, OPRO) | offline compile | ~0 | until recompile | whole task family |
| 4 | Tool / skill library | medium (synthesis + tests) | tool call | cross-session, portable | executable surface |
| 5 | Model weights (STaR, SPIN, SEAL) | high (training) | ~0 | until next checkpoint | everything |

**Design rule:** climb the ladder lazily. Most production gains stop at rung 1–2. Rung 4 is underused and usually higher ROI than rung 5, because a synthesized skill is inspectable, reversible, and diffable.

### 2.3 Persistence

Distinguish:

- **Within-episode** adaptation (retry loops) — not self-improvement, just search.
- **Cross-session** retention (memory, skill library) — genuine but fragile; dies with the store.
- **Cross-model** retention — only achieved at rung 3/4/5, where artifacts survive model swaps.

A skill library is the most model-portable form: it is code, not activations.

### 2.4 Supervision

From full labels to none. Self-generated labels are the interesting regime, and the one most prone to silent collapse: an agent that generates its own curriculum and its own reward can amplify its own biases (see §4).

### 2.5 Verifiability

The single most useful axis for reading papers critically.

- **Proven:** executable test passed on held-out instance.
- **Estimated:** rubric judge or LLM-as-judge with reported agreement.
- **Claimed:** anecdote, demo, or cherry-picked trace.

This repo's benchmark suite exists to move claims up this list cheaply.

---

## 3. Anatomy of One Improvement Cycle

```text
attempt(t)   ->  trajectory τ
evaluate(τ)  ->  outcome o ∈ {pass, fail} + signal s
diagnose(τ,s)->  lesson ℓ   (natural language, must name the cause)
decide(ℓ)    ->  action: store | synthesize | patch prompt | retrain | discard
commit(...)  ->  durable artifact a
verify(a)    ->  does a improve held-out performance without regressions?
```

Two steps are routinely skipped and both are load-bearing:

- **`diagnose`** — storing a raw failure ("it broke") teaches nothing. The lesson must name a *cause* and a *different next action*.
- **`verify(a)`** — committing an artifact without a regression check is how agents accumulate confident bad habits.

### The lesson is the unit of improvement

A lesson should be written so a *different* agent could act on it:

```text
BAD : "The test failed."
GOOD: "Pytest collected 0 tests because pyproject.toml sets testpaths=['tests']
       but the new suite lives in tests/unit/. Add tests/unit to testpaths
       before running pytest."
```

The good version is retrievable, actionable, and falsifiable. This is also why lessons are better stored as structured records (trigger, cause, action, evidence) than as free-text chunks.

---

## 4. Failure Modes

Self-improving systems fail in characteristic ways. Naming them makes them testable.

### 4.1 Reward hacking / verifier gaming
The agent optimizes the measurable proxy instead of the goal — deleting failing tests, weakening assertions, or emitting the exact string a judge looks for. Any rung ≥3 update must be gated by tests the agent cannot edit.

### 4.2 Self-consistency collapse
With only LLM self-critique, agreement between generator and critic rises while accuracy does not. Symptom: critique quality plateaus, distinct lessons collapse into one generic "be more careful" memory. Mitigation: external signal, or diversity constraints on stored lessons.

### 4.3 Memory poisoning
A wrong lesson, once persisted, is retrieved and reinforced indefinitely. This is worse than forgetting: an amnesiac agent re-derives truth, a poisoned agent confidently repeats error. Mitigation: provenance on every record, contradiction detection, TTL/decay, and the ability to revoke lessons.

### 4.4 Contradiction accumulation
Turn 5 says the user prefers AWS; turn 80 says GCP. Cosine similarity treats both as equally relevant. Any memory tier needs an *overwrite* policy (recency + authority + explicitness), which is exactly what **COF** measures.

### 4.5 Overfitting to the task family
Lessons extracted from one repo's conventions get applied to another where they are wrong. Mitigation: scope lessons with applicability conditions, and evaluate transfer explicitly (this is **CSST**).

### 4.6 Silent regression
A skill that fixes task A breaks task B, and nobody re-runs B. Mitigation: every committed artifact carries the eval set it was validated against.

### 4.7 Context saturation
Endless memory writes crowd the window and *degrade* performance. More memory is not monotonically better; consolidation and pruning are part of the mechanism, not cleanup.

---

## 5. How to Prove Improvement

Minimum credible protocol:

1. **Fix the policy** — same model, same tools, same sampling params across conditions.
2. **Held-out split** — the instance used to generate the lesson must not be in the eval set.
3. **Two conditions** — with the improvement artifact vs. without (ablation), same seeds.
4. **Repeat** — report variance over ≥3 seeds; single-run deltas smaller than variance are noise.
5. **Regression suite** — the artifact must also be scored on tasks it was *not* meant to help.
6. **Cost** — report tokens and wall-clock per solved task. An improvement that costs 10× is a different product.

Metrics worth reporting (mapped to this repo's benchmarks):

| Claim | Metric |
| :--- | :--- |
| "It respects updated facts" | COF — accuracy on updated vs. stale fact |
| "It remembers long-range constraints" | NIMS — recall @ 20/50/100 turns |
| "It transfers taught skills" | CSST — cross-session execution success |
| "It reflects efficiently" | VSCE — iterations to convergence |
| "It doesn't break other things" | regression delta on untouched tasks |

---

## 6. Design Checklist

Before shipping a self-improving loop:

- [ ] Is there a verifier the agent cannot modify?
- [ ] Does every stored artifact carry provenance (source task, date, evidence)?
- [ ] Is there an overwrite policy for contradictions?
- [ ] Is there a prune/decay policy, or does the store grow without bound?
- [ ] Is a committed skill/prompt re-validated against a regression suite?
- [ ] Can a bad lesson be revoked, and is revocation fast?
- [ ] Is improvement measured on held-out tasks with ≥3 seeds?
- [ ] Is the cost per solved task reported alongside accuracy?

---

## 7. References

- Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning* — [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)
- Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback* — [arXiv:2303.17651](https://arxiv.org/abs/2303.17651)
- Gou et al., *CRITIC: LLMs Can Self-Correct with Tool-Interactive Critiquing* — [arXiv:2305.11738](https://arxiv.org/abs/2305.11738)
- Wang et al., *Voyager: An Open-Ended Embodied Agent with LLMs* — [arXiv:2305.16291](https://arxiv.org/abs/2305.16291)
- Zhao et al., *ExpeL: LLM Agents Are Experiential Learners* — [arXiv:2308.10144](https://arxiv.org/abs/2308.10144)
- Khattab et al., *DSPy: Compiling Declarative LM Calls into Self-Improving Pipelines* — [arXiv:2310.03714](https://arxiv.org/abs/2310.03714)
- Yuksekgonul et al., *TextGrad* — [arXiv:2406.07496](https://arxiv.org/abs/2406.07496)
- Yin et al., *Gödel Agent: A Self-Referential Agent Framework* — [arXiv:2410.04444](https://arxiv.org/abs/2410.04444)
- Hu et al., *Automated Design of Agentic Systems* — [arXiv:2408.08435](https://arxiv.org/abs/2408.08435)
- Zhang et al., *Darwin Gödel Machine* — [arXiv:2505.22954](https://arxiv.org/abs/2505.22954)
- Zelikman et al., *STaR: Bootstrapping Reasoning With Reasoning* — [arXiv:2203.14465](https://arxiv.org/abs/2203.14465)
- Chen et al., *Self-Play Fine-Tuning (SPIN)* — [arXiv:2401.01335](https://arxiv.org/abs/2401.01335)
- Yuan et al., *Self-Rewarding Language Models* — [arXiv:2401.10020](https://arxiv.org/abs/2401.10020)
- Zweiger et al., *Self-Adapting Language Models (SEAL)* — [arXiv:2506.10943](https://arxiv.org/abs/2506.10943)
