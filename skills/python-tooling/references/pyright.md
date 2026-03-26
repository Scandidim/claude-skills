# Pyright — Python Type Checker

Pyright is Microsoft's fast, feature-complete Python type checker. It's the engine behind Pylance (VS Code) and runs significantly faster than mypy on large codebases.

## Installation

```bash
pip install pyright           # project dependency
npm install -g pyright        # global via npm (same binary)
uv add --dev pyright          # with uv
pipx install pyright          # isolated global install
```

## pyrightconfig.json

```json
{
  "pythonVersion": "3.11",
  "pythonPlatform": "Linux",
  "typeCheckingMode": "basic",

  "include": ["src", "scripts"],
  "exclude": [
    "**/node_modules",
    "**/__pycache__",
    "**/migrations",
    ".venv"
  ],
  "ignore": [
    "src/legacy"
  ],

  "venvPath": ".",
  "venv": ".venv",

  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "reportUnusedImport": "warning",
  "reportUnusedVariable": "warning",
  "reportPrivateUsage": "warning"
}
```

## Type Checking Modes

| Mode | Use Case |
|------|----------|
| `"off"` | Disable (useful per-file) |
| `"basic"` | Balanced — catches common errors, allows untyped code |
| `"standard"` | Stricter — recommended for typed codebases |
| `"strict"` | Maximum — requires full annotations everywhere |

Start with `"basic"`, graduate to `"standard"` when the codebase is mostly typed.

## pyproject.toml Configuration

```toml
[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "basic"
venvPath = "."
venv = ".venv"
include = ["src"]
exclude = ["**/migrations", "**/__pycache__"]

# Granular rule overrides
reportMissingImports = true
reportMissingTypeStubs = false
reportUnusedImport = "warning"
reportPrivateUsage = "warning"
reportUnnecessaryTypeIgnoreComment = "warning"
```

## CLI Usage

```bash
# Check all files
pyright

# Check specific file or directory
pyright src/mymodule/

# Output as JSON (for tooling)
pyright --outputjson

# Show statistics
pyright --stats

# Verify type stub packages
pyright --verifytypes mypackage

# Watch mode
pyright --watch
```

## Type Annotations — Common Patterns

### Basic Annotations

```python
from __future__ import annotations  # Enable PEP 604 | syntax in older Python

def greet(name: str, repeat: int = 1) -> str:
    return (f"Hello, {name}! " * repeat).strip()

# Variables
count: int = 0
mapping: dict[str, list[int]] = {}
optional: str | None = None      # Python 3.10+ syntax
```

### Collections (Modern Syntax)

```python
# Python 3.9+ — use built-in generics (no need for typing imports)
items: list[str] = []
lookup: dict[str, int] = {}
pair: tuple[str, int] = ("key", 1)
unique: set[str] = set()

# Fixed-length tuple
point: tuple[float, float] = (1.0, 2.0)

# Variable-length tuple
coords: tuple[float, ...] = (1.0, 2.0, 3.0)
```

### Union Types

```python
# Python 3.10+
def process(value: str | int | None) -> str:
    ...

# Older Python (3.8+)
from typing import Optional, Union
def process(value: Union[str, int, None]) -> str:
    ...
```

### TypedDict

```python
from typing import TypedDict, NotRequired

class UserConfig(TypedDict):
    name: str
    email: str
    role: NotRequired[str]  # Optional key

config: UserConfig = {"name": "Alice", "email": "alice@example.com"}
```

### Protocol (Structural Typing)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict[str, object]: ...
    def to_json(self) -> str: ...

def save(obj: Serializable) -> None:
    data = obj.to_dict()
    ...
```

### Generic Functions and Classes

```python
from typing import TypeVar, Generic

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()
```

### Overloads

```python
from typing import overload

@overload
def process(value: str) -> str: ...
@overload
def process(value: int) -> int: ...
def process(value: str | int) -> str | int:
    if isinstance(value, str):
        return value.upper()
    return value * 2
```

### ParamSpec and TypeVarTuple (3.10+)

```python
from typing import ParamSpec, Callable, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def logged(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

## Type Stubs

### Installing Stubs for Third-Party Libraries

```bash
pip install pandas-stubs       # pandas
pip install types-requests     # requests
pip install types-PyYAML       # PyYAML
pip install types-redis        # redis
pip install boto3-stubs        # AWS boto3
```

### Writing Inline Stubs

```python
# mypackage/py.typed  — marker file, enables PEP 561
# (empty file, just needs to exist)
```

### Stub Files (.pyi)

```python
# mypackage/utils.pyi
from typing import overload

@overload
def parse(data: str) -> dict[str, object]: ...
@overload
def parse(data: bytes) -> dict[str, object]: ...

def merge(*dicts: dict[str, object]) -> dict[str, object]: ...
```

## Suppressing Errors

```python
x: int = "not an int"  # type: ignore[assignment]

# Multiple errors on one line
y = complex_call()  # type: ignore[no-any-return, return-value]

# Suppress all errors in file (add at top)
# pyright: basic
```

**Document suppressions:**

```python
# type: ignore[attr-defined]  — third-party lib missing stubs (PIL)
img.save(path, format="PNG")  # type: ignore[attr-defined]
```

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `reportMissingImports` | Missing type stubs | Install `types-*` package or add stubs |
| `reportGeneralTypeIssues` | Type mismatch | Fix annotation or add cast |
| `reportOptionalMemberAccess` | `None` dereference | Add `if x is not None:` guard |
| `reportAttributeAccessIssue` | Missing attribute | Check class definition, add stub |
| `reportArgumentType` | Wrong arg type | Fix call site or widen annotation |
| `reportReturnType` | Return type mismatch | Fix return or update annotation |
| `reportUnknownVariableType` | Untyped third-party code | Install stubs, use `cast()`, or ignore |

## Gradual Typing Strategy

```
1. Start: typeCheckingMode = "off" → no errors
2. Basic: typeCheckingMode = "basic" → catch null errors, missing attrs
3. Standard: typeCheckingMode = "standard" → full annotation enforcement
4. Strict: typeCheckingMode = "strict" → every arg and return annotated
```

Per-file strictness upgrade:

```python
# pyright: strict  ← Add at top of fully-typed files
from __future__ import annotations
...
```

## CI Integration

```yaml
- name: Pyright type check
  run: pyright --outputjson | python scripts/pyright-summary.py
  # Or simply:
- name: Pyright
  run: pyright
```

```bash
# Exit code 0 = no errors, 1 = errors found
pyright; echo "Exit: $?"
```
