import difflib
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from rich.console import Console
from rich.text import Text

# import logging
# from rich.logging import RichHandler


TEST_OLD: str = """\
def format_user(name, role):
    return f"{name} ({role})"

def can_access(role, resource):
    if role == "admin":
        return True
    if role == "editor" and resource != "billing":
        return True
    return False

print(format_user("Sam", "editor"))
"""

TEST_NEW: str = """\
def format_user(name: str, role: str) -> str:
    return f"{name} [{role}]"

def can_access(role: str, resource: str) -> bool:
    if role in ("admin", "owner"):
        return True
    if role == "editor" and resource not in ("billing", "secrets"):
        return True
    return False

# demo
print(format_user("Sam", "owner"))
"""


@dataclass(frozen=True)
class DiffTheme:
    # Structural UI
    gutter: str = "dim"     # old/new line numbers
    sep: str = "dim"        # separator "│"
    equal: str = "none"     # unchanged lines

    # Added lines: light blue foreground on deep blue background
    add_line: str = "#b5f5c2 on #163a23"

    # Deleted lines: light red foreground on deep red background
    del_line: str = "#ffb4b4 on #3a1e1e"

    # Inline (character-level) highlights for replacements:
    # slightly stronger backgrounds than the whole-line colors
    add_inline: str = "bold #ffffff on #1f6f3a"
    del_inline: str = "bold #ffffff on #8a2a2a"


# def _inline_highlight(a: str, b: str, base_style: str, change_style: str, mode: str) -> Text:
#     """
#     Highlight changed character spans inside a replaced line.
#     mode: "del" -> show a with deletions highlighted
#           "add" -> show b with insertions highlighted
#     """
#     sm = difflib.SequenceMatcher(a=a, b=b)
#     out = Text()

#     if mode == "del":
#         src = a
#         for tag, i1, i2, j1, j2 in sm.get_opcodes():
#             chunk = src[i1:i2]
#             if not chunk:
#                 continue
#             style = change_style if tag in ("replace", "delete") else base_style
#             out.append(chunk, style=style)
#     else:  # "add"
#         src = b
#         for tag, i1, i2, j1, j2 in sm.get_opcodes():
#             chunk = src[j1:j2]
#             if not chunk:
#                 continue
#             style = change_style if tag in ("replace", "insert") else base_style
#             out.append(chunk, style=style)

#     return out


def _inline_highlight(a: str, b: str, base_style: str, change_style: str, mode: str) -> Text:
    sm = difflib.SequenceMatcher(a=a, b=b)

    if mode == "del":
        text = Text(a, style=base_style)  # base first
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("replace", "delete") and i1 != i2:
                text.stylize(change_style, i1, i2)  # inline on top
        return text

    # mode == "add"
    text = Text(b, style=base_style)  # base first
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "insert") and j1 != j2:
            text.stylize(change_style, j1, j2)  # inline on top
    return text


def print_vscode_like_diff(
    old: str,
    new: str,
    *,
    show_unchanged: bool = True,
    theme: DiffTheme = DiffTheme(),
    console: Optional[Console] = None,
) -> None:
    """
    Print an inline diff reminiscent of VS Code's inline diff view:
    - Two line-number gutters (old/new)
    - +/- markers
    - Colored backgrounds
    - Inline highlights for replaced lines
    """
    console = console or Console()

    print("is_terminal:", console.is_terminal)
    print("color_system:", console.color_system)

    old_lines = old.splitlines()
    new_lines = new.splitlines()

    lw = max(2, len(str(len(old_lines) if old_lines else 1)))
    rw = max(2, len(str(len(new_lines) if new_lines else 1)))

    def emit(lno: str, rno: str, sign: str, content: Text, content_style: str) -> None:
        prefix = Text()
        prefix.append(f"{lno:>{lw}} ", style=theme.gutter)
        prefix.append(f"{rno:>{rw}} ", style=theme.gutter)
        prefix.append(f"{sign} ", style="bold" if sign.strip() else theme.gutter)
        prefix.append("│ ", style=theme.sep)

        # Pad so background fills to the edge (best-effort; depends on terminal width)
        available = max(0, console.width - len(prefix.plain))
        if len(content.plain) < available:
            content.append(" " * (available - len(content.plain)), style=content_style)

        line = Text.assemble(prefix, content)
        console.print(line, overflow="crop", no_wrap=True)

    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            if not show_unchanged:
                continue
            for k in range(i2 - i1):
                ln = i1 + k + 1
                rn = j1 + k + 1
                emit(str(ln), str(rn), " ", Text(old_lines[i1 + k]), theme.equal)

        elif tag == "delete":
            for k in range(i1, i2):
                emit(str(k + 1), "", "-", Text(old_lines[k], style=theme.del_line), theme.del_line)

        elif tag == "insert":
            for k in range(j1, j2):
                emit("", str(k + 1), "+", Text(new_lines[k], style=theme.add_line), theme.add_line)

        elif tag == "replace":
            old_chunk = old_lines[i1:i2]
            new_chunk = new_lines[j1:j2]
            n = max(len(old_chunk), len(new_chunk))

            for k in range(n):
                old_line = old_chunk[k] if k < len(old_chunk) else None
                new_line = new_chunk[k] if k < len(new_chunk) else None

                if old_line is not None:
                    ln = str(i1 + k + 1)
                    # Inline highlight old vs corresponding new (or empty)
                    other = new_line or ""
                    content = _inline_highlight(
                        old_line, other, base_style=theme.del_line, change_style=theme.del_inline, mode="del"
                    )
                    emit(ln, "", "-", content, theme.del_line)

                if new_line is not None:
                    rn = str(j1 + k + 1)
                    other = old_line or ""
                    content = _inline_highlight(
                        other, new_line, base_style=theme.add_line, change_style=theme.add_inline, mode="add"
                    )
                    emit("", rn, "+", content, theme.add_line)

        else:
            raise ValueError(f"Unexpected difflib opcode tag: {tag!r}")


def main():
    # console = Console(color_system="truecolor", force_terminal=True)
    # print_vscode_like_diff(TEST_OLD, TEST_NEW, console=console)
    print_vscode_like_diff(TEST_OLD, TEST_NEW, show_unchanged=True)

