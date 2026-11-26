# Your first PR, end to end

This walks through one complete contribution — adding `--json` output to the dataset
validator — from fork to merged PR. It takes about 30 minutes and touches one file.

If you get stuck, open an issue and ask. Questions are welcome; half-finished PRs are fine.

---

## 0. Pick a task

Browse [`good first issue`](https://github.com/travisim/awesome-self-improving-agents/labels/good%20first%20issue).
This guide uses [#9](https://github.com/travisim/awesome-self-improving-agents/issues/9).

---

## 1. Fork and clone

```bash
gh repo fork travisim/awesome-self-improving-agents --clone=true
cd awesome-self-improving-agents
```

Without the GitHub CLI: fork on the web, then `git clone` your fork.

## 2. Confirm the baseline

```bash
python3 benchmarks/runner/eval_memory.py --validate
```

You should see three PASS lines and `All datasets valid. Total scenarios: 15`.
If this fails before you change anything, stop and open an issue.

## 3. Make the change

Open `benchmarks/runner/eval_memory.py` and find `main()` at the bottom. It builds an
`argparse` parser with `--validate`, `--list`, `--stats`, `--list-adapters`.

Add one flag:

```python
parser.add_argument("--json", action="store_true",
                    help="emit machine-readable output for --validate")
```

Then in `cmd_validate()`, collect results and branch on the flag. The shape you want:

```json
{
  "ok": true,
  "total_records": 15,
  "datasets": [
    {"file": "contradiction_overwrite.json", "metric": "COF", "records": 7, "ok": true, "errors": []}
  ]
}
```

Two rules:

1. When `--json` is set, **do not** print the human-readable lines — stdout must be valid JSON.
2. Exit codes must not change: `0` on success, `1` on any dataset error.

## 4. Test it

```bash
# still human-readable
python3 benchmarks/runner/eval_memory.py --validate

# valid JSON
python3 benchmarks/runner/eval_memory.py --validate --json | python3 -m json.tool

# failure path: break a schema on purpose, confirm exit code 1
cp benchmarks/dataset/contradiction_overwrite.json /tmp/backup.json
python3 - <<'PY'
import json, pathlib
p = pathlib.Path("benchmarks/dataset/contradiction_overwrite.json")
d = json.loads(p.read_text()); d[0].pop("expected_answer")
p.write_text(json.dumps(d, indent=2))
PY
python3 benchmarks/runner/eval_memory.py --validate --json; echo "exit=$?"
cp /tmp/backup.json benchmarks/dataset/contradiction_overwrite.json
```

That last check matters: a PR that only handles the happy path isn't done.

## 5. Commit and push

```bash
git checkout -b feat/validator-json-output
git add benchmarks/runner/eval_memory.py
git commit -m "feat(runner): add --json output to --validate"
git push -u origin feat/validator-json-output
```

Commit prefixes used here: `feat:`, `fix:`, `docs:`, `test:`, `ci:`.

## 6. Open the PR

```bash
gh pr create --fill
```

The template asks for a validation checklist — tick what you actually ran.
If you skipped something, say so. That is always better than claiming a check you didn't do.

## 7. Review

Expect a response within a few days. Small, focused PRs usually merge quickly.

If a maintainer asks for a change, push another commit to the same branch — the PR updates
automatically. If a PR goes quiet for a week, one polite ping is appropriate.

---

## What gets a PR rejected here

- **Fabricated numbers.** Never add a benchmark score or star count you did not measure.
- **Dataset churn.** Do not modify or renumber existing records in the same PR as new ones.
- **Scope creep.** One logical change per PR.
- **Typos only.** A single-word spelling fix isn't worth a review cycle on its own.

---

## After it merges

You're in the contributor list. The next step is whatever interests you — adapters (#1, #2),
research write-ups (#5, #6), or a new metric (#7). Each has acceptance criteria in the issue.
