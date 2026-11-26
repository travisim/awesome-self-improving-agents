## What does this change?

<!-- One paragraph. Link the issue if there is one: Fixes #NN -->

## Type

- [ ] Dataset scenario(s)
- [ ] Adapter implementation
- [ ] Docs / paper entry
- [ ] Tooling / CI
- [ ] Fix

## Checklist

- [ ] `python3 benchmarks/runner/eval_memory.py --validate` passes
- [ ] Every added link resolves
- [ ] Claims are cited, or explicitly marked unverified
- [ ] No fabricated benchmark numbers or star counts
- [ ] One logical change per PR

## For dataset changes

- [ ] Existing records were not modified or renumbered
- [ ] New IDs are unique and correctly prefixed (`cof-`, `nims-`, `csst-`, `vsce-`)
- [ ] `expected_answer` differs from `stale_trap` where applicable

## For adapter changes

- [ ] Implements `MemoryAdapter` and is registered with `@register_adapter`
- [ ] `reset()` fully clears state
- [ ] No network calls in CI paths
