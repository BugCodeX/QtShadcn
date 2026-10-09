# NumPy Docstring & Code Comment Style Guide

Comprehensive rules and conventions for NumPy-style docstrings (`pydocstyle` / ruff `D` rules) and human-readable code comments.

---

## 1. Docstring Structure & Sections

NumPy-style docstrings use section headers underlined with hyphens (`---`) matching the exact character length of the header text.

### Standard Section Order:

1. **Short Summary**: Single line explaining what the function/class/module does. Imperative mood, ends with a period.
2. **Deprecation Warning** (if applicable): `.. deprecated:: 1.2.0` note.
3. **Extended Summary** (optional): Paragraph elaborating on behavior, edge cases, algorithms.
4. **Parameters**:
   ```python
   Parameters
   ----------
   name : type or {choice1, choice2}
       Description of parameter.
   optionalName : type, optional
       Description with default value stated: ``(default: 10)``.
   ```
5. **Returns** / **Yields** / **Receives**:
   ```python
   Returns
   -------
   returnType
       Description of return value semantics.
   ```
6. **Raises** / **Warns**:
   ```python
   Raises
   ------
   ValueError
       When provided input is out of valid bounds.
   ```
7. **Attributes / Properties** (Classes/Widgets):
   ```python
   Attributes
   ----------
   tokenName : str
       Active theme token identifier.
   ```
8. **See Also** (optional): Related functions or classes.
9. **Notes** (optional): Technical quirks, algorithmic complexity, platform constraints.
10. **Examples** (optional): Doctests or usage examples.

---

## 2. Key pydocstyle & Ruff Rules Reference

- **D100-D103**: Public modules, classes, and methods must have docstrings.
- **D200**: One-line docstrings must fit on one line (`"""Single line summary."""`).
- **D205**: 1 blank line required between summary line and description/sections.
- **D212**: Multi-line docstring summary should start at the first line or follow project convention.
- **D400/D415**: First line should end with a period.
- **D401**: First line should be in imperative mood (e.g. "Calculate...", "Resolve...", "Return...").
- **D405-D411**: Section names must use standard title case and have proper underlining dashes without trailing colons.

---

## 3. Human-Sounding Code Comments

### Principles:

1. **Explain the WHY, not the WHAT**:
   - Code shows *how* something is done. Comments must explain *why* it was done this way or what subtle assumption exists.
2. **Zero Filler Phrases**:
   - Never write: *"This function is responsible for..."*, *"Variable for holding..."*, *"Helper function to..."*.
   - Avoid robotic translations of the syntax.
3. **Natural, Direct Voice**:
   - Write comments as if speaking to a peer engineer.
   - Mention gotchas, platform quirks (e.g. Windows path quirks, Qt event loop nuances, API workarounds).
4. **No redundant clutter**:
   - If a line of code is self-evident (e.g., `user.isActive = True`), do not add `# set user to active`.
