---
name: Dataset scenario
about: Propose new benchmark scenarios (COF / NIMS / CSST / VSCE)
labels: dataset, good first issue
---

## Metric

- [ ] COF — contradiction & overwrite fidelity
- [ ] NIMS — needle in multi-turn session
- [ ] CSST — cross-session skill transfer
- [ ] VSCE — verbal self-correction efficiency (planned, see #7)

## Scenario

<!-- The realistic situation: what fact/constraint/skill, and why it's hard for an agent. -->

## Why it's not trivial

<!-- A case no system could fail measures nothing. What makes this tempting to get wrong? -->

## Acceptance

- [ ] Unique, prefixed ID
- [ ] `python3 benchmarks/runner/eval_memory.py --validate` passes
- [ ] Existing records untouched
