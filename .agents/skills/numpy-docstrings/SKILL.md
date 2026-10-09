---
name: numpy-docstrings
description: "Trigger: docstring, docstrings, pydocstyle, numpy docstrings, python comments, documentar codigo, ruff D. Write NumPy-style docstrings and natural comments."
license: MIT
metadata:
  author: BugCodeX
  version: "1.0"
---

# Skill: numpy-docstrings

## Activation Contract

Activate whenever writing, refactoring, or reviewing Python code, adding docstrings, generating API documentation, writing inline code comments, or enforcing `pydocstyle` / ruff `D` rules.

## Hard Rules

- **NumPy formatting**: Use standard NumPy section headers with dashes (`---`) matching header length exactly.
- **Quotes**: Double quotes (`"""..."""`) for all docstrings.
- **Proportional depth**:
  - Trivial getters, setters, or simple wrappers: use concise single-line docstrings.
  - Complex functions / public APIs: include `Parameters`, `Returns`, `Raises`, `Examples` when non-obvious.
- **Human-sounding comments**:
  - Comment the **WHY** or non-obvious **HOW**, never the obvious **WHAT**.
  - Write in natural, clear human language. Zero robotic narrations or re-stating variable names.
  - **Zero filler phrases**: Never use `"This function is responsible for..."`, `"Esta función se encarga de..."`, or `"Helper to..."`.
- **Public coverage**: All public modules, classes, methods, and functions require docstrings. Private methods require docstrings when non-trivial.
- **No abbreviations**: Use full descriptive names in parameter docs and comments (`button`, `color`, `index`, not `btn`, `col`, `idx`).
- **Line length**: Wrap docstring descriptions and comments to max 100 characters.

## Decision Gates

| Target | Docstring Strategy | Sections to Include |
| --- | --- | --- |
| **Module** (`.py` file) | High-level summary of module purpose and key components | Overview, optional `Notes` or `Examples` |
| **Class / Qt Widget** | Purpose, lifecycle, and component behavior | `Attributes`, `Parameters` (if not in `__init__`), `Examples` |
| **Complex Function** | Complete behavioral specification | `Parameters`, `Returns` (or `Yields`), `Raises`, `Examples` |
| **Simple Method / Wrapper** | Single-line direct verb phrase | None (one-line summary only) |
| **Inline Comment** | Explain intent, constraints, or non-obvious choices | Natural human rationale, no docstring blocks |

## Execution Steps

1. **Identify the construct**: Classify as module, class, widget, complex function, or trivial helper.
2. **Draft the summary**: Start with a concise, imperative one-line sentence ending in a period.
3. **Add relevant sections** from `assets/docstring-templates.py`:
   - `Parameters`: Name, type, and non-obvious constraints.
   - `Returns` / `Yields`: Concrete return types and semantics.
   - `Raises`: Specific exceptions callers are expected to catch.
   - `Attributes` / `Properties`: Public properties and state.
4. **Refine inline comments**:
   - Strip out redundant comments narrating obvious code.
   - Ensure remaining comments explain design rationale or domain quirks in human conversational tone.
5. **Lint check**: Verify syntax satisfies `pydocstyle` / ruff `D` rules (no missing sections, valid underline lengths).

## Output Contract

Return clean, fully annotated Python code featuring:

- Accurate NumPy-style docstrings fitted to target complexity.
- Thoughtful, natural human comments explaining non-obvious logic.
- Zero pydocstyle / ruff `D` violations.

## References

- `references/numpy-docstring-rules.md` — Detailed pydocstyle rules and section standards.
- `assets/docstring-templates.py` — Ready-to-use code templates and comment comparisons.
