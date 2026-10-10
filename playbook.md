---
scope: project
---
<!-- gentle-playbook:v9 scope=project updated=2026-10-10 -->
# Playbook: Local Project

## Topology: Project Custom Layout

- `src/`

## Invariants

### [INVARIANT:b1] [B1] En el código de la librería (`qtshadcn/*`), NUNCA importar directamente `PySide6` o `PyQt6`; importar siempre desde `qtshadcn.common.binding`

- **Surface:** `core/style`
- **Rule:** En el código de la librería (`qtshadcn/*`), NUNCA importar directamente `PySide6` o `PyQt6`; importar siempre desde `qtshadcn.common.binding`.

### [INVARIANT:b2] [B2] Los modelos de dominio de tokens y temas deben usar Pydantic v2 `BaseModel` con `ConfigDict(frozen=True)` para garantizar inmutabilidad

- **Surface:** `core/style`
- **Rule:** Los modelos de dominio de tokens y temas deben usar Pydantic v2 `BaseModel` con `ConfigDict(frozen=True)` para garantizar inmutabilidad.

### [INVARIANT:b3] [B3] Encadenar siempre las excepciones causadas por dependencias faltantes o fallos externos mediante `raise CustomError(...) from exc`

- **Surface:** `core/style`
- **Rule:** Encadenar siempre las excepciones causadas por dependencias faltantes o fallos externos mediante `raise CustomError(...) from exc`.

### [INVARIANT:b4] [B4] Todas las rutas del sistema de archivos deben manipularse con `pathlib.Path`, resolviendo siempre respecto a `__file__`

- **Surface:** `core/style`
- **Rule:** Todas las rutas del sistema de archivos deben manipularse con `pathlib.Path`, resolviendo siempre respecto a `__file__`.

### [INVARIANT:b5] [B5] Documentación Estricta NumPy

- **Surface:** `qtshadcn/`
- **Rule:** Todos los módulos, clases y funciones públicas del paquete deben incluir docstrings en formato NumPy respetando pydocstyle y reglas `D` de ruff.

### [INVARIANT:b6] [B6] Tipado Estricto con TypeAliases de Dominio

- **Surface:** `qtshadcn/`
- **Rule:** Todas las funciones públicas deben incluir type annotations completos verificables por `ty`. Utilizar alias de dominio (`ColorLike`, `Pixels`) en lugar de repetir uniones primitivas
dispersas (`QColor | str | None`).

### [INVARIANT:b7] [B7] Nomenclatura Qt y Regla de Dos Palabras

- **Surface:** `qtshadcn/`
- **Rule:** Métodos y funciones deben usar `camelCase` descriptivo compuesto por al menos dos palabras (verbo + contexto, ej: `resolveRadius`, `getThemeTokens`). Clases en `PascalCase`.
Constantes y miembros de Enum en `UPPER_SNAKE_CASE`. Signals de Qt en `camelCase` (`themeChanged`) y slots/handlers con prefijo `_on*` o `_handle*`.

## Ask Catalog

### [ASK:b2] [B2] SI se implementa un generador o transformador sintáctico (CSS/XML)

- **Surface:** `general`
- **Trigger:** SI se implementa un generador o transformador sintáctico (CSS/XML)
- **Anti-Trigger:** En llamadas internas o cuando no aplique la condición
- **Prompt:** "separar la lógica pura (sin I/O) en funciones que devuelvan tuplas de resultado `tuple[bool, str]`."
- **Default:** Continuar sin aplicar patrón condicional

## Nunca

- [B6] NUNCA utilizar `os.path` en nuevos módulos (usar `pathlib.Path`).
