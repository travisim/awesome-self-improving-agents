# Self-Learning Mechanisms for Autonomous Agents

Self-learning in AI agents refers to **in-context, test-time performance improvement** without backpropagation or weight modification.

---

## 1. Reflexion: Verbal Reinforcement Learning

### The Core Loop
Instead of training neural network weights via reinforcement learning (RL), **Reflexion** uses natural language as the reward signal and policy critique:

```text
1. Execution: Agent attempts task -> Generates Trajectory T1
2. Evaluation: Environment returns failure (e.g., failed test, compiler error)
3. Reflection: Agent analyzes failure -> Writes Critique C1 ("I failed because X, next time do Y")
4. Episodic Storage: Critique C1 stored in agent memory
5. Retrial: Agent attempts task again, conditioned on C1 -> Produces Trajectory T2 (Success)
```

### Reference
* *Reflexion: Language Agents with Verbal Reinforcement Learning* (Shinn et al., NeurIPS 2023).

---

## 2. Automated Skill Synthesis & Tool Distillation

Agents that learn by doing do not keep raw conversation logs; they synthesize **executable tools**:

1. **Trial & Error Phase:** Agent struggles through a multi-step task (e.g., converting a legacy SQL query to Prisma ORM).
2. **Success Gate:** When all verification tests pass, the agent extracts the core logic.
3. **Abstraction:** The agent writes a standalone TypeScript or Python function with docstrings and type annotations.
4. **Registry Registration:** The skill is saved to the procedural memory library (`skills/sql-to-prisma.ts`) and indexed with a semantic embedding description so future agents can call it as a first-class tool.

---

## 3. Background Memory Consolidation (Sleep Cycles)

Human brains consolidate and prune memories during sleep. Autonomous agent architectures implement an analogous **periodic memory maintenance daemon**:

* **Contradiction Resolution:** Detect and prune superseded facts.
* **Entity Merging:** Combine duplicate representations of the same entity (e.g., `travis`, `Travis Sim`, `user_501`).
* **Persona Distillation:** Update the high-level user profile from granular conversation logs.
