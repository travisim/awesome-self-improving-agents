# Contributing to Awesome Agent Memory & Self-Learning 🧠

Thank you for your interest in contributing to **Awesome Agent Memory & Self-Learning**! This project is a community-driven hub bringing clarity and rigor to AI agent cognition.

---

## 🎯 How You Can Contribute

### 1. Add a Memory Framework or Engine
If you develop or know of a production-grade agent memory library:
1. Ensure the project is open-source with an active repository.
2. Edit `README.md` to add the project under the **Frameworks & Engines** table.
3. Include: Project Name, GitHub Stars, Primary Memory Shape, Storage Backend, and a 1-sentence highlight.

### 2. Add a Research Paper
Add influential academic papers on agent memory or self-learning under the relevant sections:
* Required format: `[Paper Title](link) (Conference/arXiv Year) - Key contribution summary.`

### 3. Add Benchmark Test Cases
Contribute new evaluation scenarios to `benchmarks/dataset/`:
* `contradiction_overwrite.json`: Scenarios testing memory updating when user instructions change.
* `needle_in_multiturn.json`: Multi-turn conversational scenarios with buried constraints.
* `cross_session_transfer.json`: Skill learning and cross-session procedural recall.

### 4. Implement a Memory Adapter
Create a Python adapter in `benchmarks/runner/adapters/` that implements the standard `MemoryAdapter` interface:
```python
class MemoryAdapter:
    def store(self, key: str, value: str, metadata: dict) -> None: ...
    def retrieve(self, query: str, limit: int = 5) -> list[str]: ...
    def update(self, key: str, new_value: str) -> None: ...
```

---

## 📋 Pull Request Guidelines

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feat/add-framework-name
   ```
2. Verify all datasets are valid JSON:
   ```bash
   python3 benchmarks/runner/eval_memory.py --dry-run
   ```
3. Commit with a clear commit message:
   ```bash
   git commit -m "docs: add HippoRAG to semantic memory frameworks"
   ```
4. Push and submit your Pull Request! Maintainers review PRs within 24-48 hours.
