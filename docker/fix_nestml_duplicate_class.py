#!/usr/bin/env python3
"""
Workaround for a NESTML >= 8.3.0 code-generation bug: every generated
neuron header that has vector-valued state variables re-emits a full
copy of the helper class

    namespace nest {
    template < typename HostNode >
    class DataAccessFunctorForInlineExpressions : public DataAccessFunctor< HostNode > { ... };
    }

with no header guard shared across files. When several such headers are
included together in one translation unit (our controller_neurons_module.cpp,
which registers all neurons in a single NEST module), the compiler sees the
class defined more than once and aborts with:

    error: redefinition of 'class nest::DataAccessFunctorForInlineExpressions<HostNode>'

This script wraps that one class definition (only that class -- the
surrounding `namespace nest { ... }` is left untouched, since reopening a
namespace multiple times is legal C++) in a project-wide, shared
#ifndef/#define/#endif guard, so only the first included header actually
defines it and subsequent ones are skipped by the preprocessor.

Usage: fix_nestml_duplicate_class.py <header_file> [<header_file> ...]
Idempotent: running it again on an already-patched file is a no-op.
"""
import re
import sys

GUARD_NAME = "NESTML_DATA_ACCESS_FUNCTOR_FOR_INLINE_EXPRESSIONS_GUARD"

# Matches the class definition, from the `template < typename HostNode >`
# line through the closing `};` of the class body (non-greedy so it stops
# at the *first* `};`, which is the end of the class -- member function
# bodies inside it don't end with `};`).
PATTERN = re.compile(
    r"(template\s*<\s*typename\s+HostNode\s*>\s*\n"
    r"class DataAccessFunctorForInlineExpressions\s*:\s*public\s+DataAccessFunctor\s*<\s*HostNode\s*>.*?\n};\n)",
    re.DOTALL,
)


def patch_file(path: str) -> bool:
    with open(path, "r") as fh:
        content = fh.read()

    if GUARD_NAME in content:
        print(f"[skip] {path}: already patched")
        return False

    def wrap(match: "re.Match[str]") -> str:
        return (
            f"#ifndef {GUARD_NAME}\n"
            f"#define {GUARD_NAME}\n"
            f"{match.group(1)}"
            f"#endif // {GUARD_NAME}\n"
        )

    new_content, n = PATTERN.subn(wrap, content, count=1)

    if n == 0:
        print(f"[----] {path}: class definition not found (nothing to patch)")
        return False

    with open(path, "w") as fh:
        fh.write(new_content)
    print(f"[fix ] {path}: guarded {n} class definition")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: fix_nestml_duplicate_class.py <header_file> [...]", file=sys.stderr)
        return 1

    for path in sys.argv[1:]:
        patch_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
