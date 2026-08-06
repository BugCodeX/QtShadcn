---
name: pytest
description: "Trigger: pytest tests, pytest coverage, fixtures, mocking, markers, parametrize, test discovery. Write idiomatic Python pytest tests and test helpers."
license: Apache-2.0
metadata:
  author: "BugCodeX"
  version: "1.0"
  category: generic
  scope: [root]
  auto_invoke:
    - "Writing, reviewing, or running Python pytest tests"
    - "Working with test fixtures, mocking, or markers"
    - "Checking pytest coverage or test discovery"
---

# Skill: pytest

## Activation Contract

Activate when the user asks for any of the following for Python:

- Writing, reviewing, or refactoring tests
- Test fixtures, mocking, or monkeypatching
- Test markers, skipping, or parametrization
- Test discovery, coverage, or pytest configuration
- Designing testable code or test layout

## Hard Rules

- Use native `pytest` features first; avoid custom test runners or wrapper helpers.
- Use `@pytest.fixture` for shared dependencies; place cross-file fixtures in the nearest `conftest.py`.
- Use `monkeypatch` for environment variables, paths, and simple functions; use `unittest.mock` for object methods and external services.
- Use `@pytest.mark.parametrize` for multiple similar cases with different inputs.
- Use `@pytest.mark.skip` / `skipif` / `xfail` only for platform/version/dependency reasons, never to silence real failures.
- Keep tests under `tests/` or a clearly named test directory; name files `test_*.py` and functions `test_*`.

## Decision Gates

| Situation | Choose |
| ----------- | -------- |
| Shared setup used by many tests | Fixture in `conftest.py` or local fixture |
| Multiple similar input/expectation pairs | `@pytest.mark.parametrize` |
| External dependency or service | `unittest.mock.patch` or `MagicMock` |
| Environment/config changes during test | `monkeypatch` |
| Slow or conditional tests | Built-in markers, not ad-hoc flags |
| Reusable test data or complex schemas | Factory fixture or asset file |

## Execution Steps

1. Identify the code under test and the expected behavior or edge case.
2. List dependencies (files, environment, external APIs, databases) that must be controlled or isolated.
3. Create a fixture if setup is reused across multiple tests; otherwise use inline `arrange` inside the test.
4. Write the test function with `GIVEN/WHEN/THEN` structure: arrange inputs, call the function, assert outputs or side effects.
5. Apply `parametrize` when multiple inputs produce the same assertion pattern.
6. Mock external boundaries; avoid mocking the code under test itself.
7. Run `pytest -q` or the project's test command and fix any failures before returning.

## Output Contract

Return:

- The test files created or modified and their paths.
- Any fixtures, markers, or parametrization used.
- Any mocks or monkeypatching applied and why.
- The pytest command that verifies the tests pass.
- A brief summary of test coverage if coverage is part of the request.

## References

- `assets/pytest-template.py` — minimal test file template.
- `assets/conftest-template.py` — shared fixture template.
