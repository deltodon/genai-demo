import io
import difflib
import logging
from dataclasses import dataclass
from typing import Optional, Sequence

from rich.console import Console, Group
from rich.protocol import is_renderable
from rich.text import Text


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

# ----------------------------
# Theme
# ----------------------------

@dataclass(frozen=True)
class DiffTheme:
    # Structural UI
    gutter: str = "dim"     # old/new line numbers
    sep: str = "dim"        # separator "│"
    equal: str = "none"     # unchanged lines

    # Added lines
    add_line: str = "#c8f6ff on #083246"           # light cyan on deep teal
    # Deleted lines
    del_line: str = "#ffd0d0 on #3a1414"           # light red on deep red

    # Inline highlights (distinct background vs whole-line)
    add_inline: str = "bold #001018 on #00d7ff"    # vivid cyan background
    del_inline: str = "bold #ffffff on #b3263a"    # vivid red background


# ----------------------------
# Inline highlighting
# ----------------------------

def _inline_highlight(a: str, b: str, base_style: str, change_style: str, mode: str) -> Text:
    """
    Build a Text line with base_style on the whole line and change_style
    applied only to changed spans.
    """
    sm = difflib.SequenceMatcher(a=a, b=b)

    if mode == "del":
        text = Text(a, style=base_style)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("replace", "delete") and i1 != i2:
                text.stylize(change_style, i1, i2)
        return text

    # mode == "add"
    text = Text(b, style=base_style)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "insert") and j1 != j2:
            text.stylize(change_style, j1, j2)
    return text


# ----------------------------
# Core diff renderer (returns a single renderable)
# ----------------------------

class RichDiff:
    def __init__(
        self,
        old: str,
        new: str,
        *,
        theme: DiffTheme = DiffTheme(),
        show_unchanged: bool = True,
    ) -> None:
        self.old = old
        self.new = new
        self.theme = theme
        self.show_unchanged = show_unchanged

    def renderable(
        self,
        *,
        console: Optional[Console] = None,
        width: Optional[int] = None,
        pad_to_width: Optional[bool] = None,
    ) -> Group:
        """
        Return a single Rich renderable (Group) containing the full diff.
        - In terminals you typically want pad_to_width=True (full-width bars).
        - In Jupyter you typically want pad_to_width=False (prevents huge blocks / scroll pain).
        """
        console = console or Console()
        if width is None:
            width = console.width
        if pad_to_width is None:
            pad_to_width = console.is_terminal

        old_lines = self.old.splitlines()
        new_lines = self.new.splitlines()

        lw = max(2, len(str(len(old_lines) or 1)))
        rw = max(2, len(str(len(new_lines) or 1)))

        def make_line(lno: str, rno: str, sign: str, content: Text, fill_style: str) -> Text:
            prefix = Text()
            prefix.append(f"{lno:>{lw}} ", style=self.theme.gutter)
            prefix.append(f"{rno:>{rw}} ", style=self.theme.gutter)
            prefix.append(f"{sign} ", style="bold" if sign.strip() else self.theme.gutter)
            prefix.append("│ ", style=self.theme.sep)

            if pad_to_width:
                available = max(0, width - len(prefix.plain))
                if len(content.plain) < available:
                    content = content.copy()
                    content.append(" " * (available - len(content.plain)), style=fill_style)

            return Text.assemble(prefix, content)

        out: list[Text] = []
        sm = difflib.SequenceMatcher(a=old_lines, b=new_lines)

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                if not self.show_unchanged:
                    continue
                for k in range(i2 - i1):
                    ln = i1 + k + 1
                    rn = j1 + k + 1
                    out.append(
                        make_line(str(ln), str(rn), " ", Text(old_lines[i1 + k]), self.theme.equal)
                    )

            elif tag == "delete":
                for k in range(i1, i2):
                    out.append(
                        make_line(str(k + 1), "", "-", Text(old_lines[k], style=self.theme.del_line), self.theme.del_line)
                    )

            elif tag == "insert":
                for k in range(j1, j2):
                    out.append(
                        make_line("", str(k + 1), "+", Text(new_lines[k], style=self.theme.add_line), self.theme.add_line)
                    )

            elif tag == "replace":
                old_chunk = old_lines[i1:i2]
                new_chunk = new_lines[j1:j2]
                n = max(len(old_chunk), len(new_chunk))

                for k in range(n):
                    old_line = old_chunk[k] if k < len(old_chunk) else None
                    new_line = new_chunk[k] if k < len(new_chunk) else None

                    if old_line is not None:
                        ln = str(i1 + k + 1)
                        other = new_line or ""
                        content = _inline_highlight(
                            old_line, other, base_style=self.theme.del_line, change_style=self.theme.del_inline, mode="del"
                        )
                        out.append(make_line(ln, "", "-", content, self.theme.del_line))

                    if new_line is not None:
                        rn = str(j1 + k + 1)
                        other = old_line or ""
                        content = _inline_highlight(
                            other, new_line, base_style=self.theme.add_line, change_style=self.theme.add_inline, mode="add"
                        )
                        out.append(make_line("", rn, "+", content, self.theme.add_line))

            else:
                raise ValueError(f"Unexpected difflib opcode tag: {tag!r}")

        return Group(*out)

    # ----------------------------
    # Output helpers
    # ----------------------------

    def print(self, *, console: Optional[Console] = None) -> None:
        console = console or Console()
        console.print(self.renderable(console=console))

    def to_ansi(self, *, width: int = 120, pad_to_width: bool = True) -> str:
        """
        ANSI-colored string suitable for logging to a normal StreamHandler.
        Uses capture() and force_terminal to ensure ANSI codes are generated.
        """
        c = Console(
            record=True,
            force_terminal=True,
            color_system="truecolor",
            width=width,
        )
        with c.capture() as cap:  # capture() returns what would have been written :contentReference[oaicite:4]{index=4}
            c.print(self.renderable(console=c, width=width, pad_to_width=pad_to_width))
        return cap.get()

    def to_plain(self, *, width: int = 120, pad_to_width: bool = False) -> str:
        buf = io.StringIO()
        c = Console(record=True, width=width, file=buf)  # file=... prevents notebook output :contentReference[oaicite:1]{index=1}
        c.print(self.renderable(console=c, width=width, pad_to_width=pad_to_width))
        return c.export_text(clear=True)

    def to_html(self, *, width: int = 120, pad_to_width: bool = False) -> str:
        buf = io.StringIO()
        c = Console(record=True, width=width, color_system="truecolor", file=buf)  # record=True required :contentReference[oaicite:2]{index=2}
        c.print(self.renderable(console=c, width=width, pad_to_width=pad_to_width))
        html = c.export_html(inline_styles=True, clear=True)
        return f"<div style='overflow-x:auto'>{html}</div>"


    # def to_plain(self, *, width: int = 120, pad_to_width: bool = False) -> str:
    #     """
    #     Plain text (no styles). Good for file logs.
    #     export_text() requires record=True. :contentReference[oaicite:5]{index=5}
    #     """
    #     c = Console(record=True, width=width)
    #     c.print(self.renderable(console=c, width=width, pad_to_width=pad_to_width))
    #     return c.export_text(clear=True)

    # def to_html(self, *, width: int = 120, pad_to_width: bool = False) -> str:
    #     """
    #     HTML for Jupyter display. export_html() requires record=True. :contentReference[oaicite:6]{index=6}
    #     """
    #     c = Console(record=True, width=width, color_system="truecolor")
    #     c.print(self.renderable(console=c, width=width, pad_to_width=pad_to_width))
    #     html = c.export_html(inline_styles=True, clear=True)
    #     # Wrap to make it notebook-friendly
    #     return f"<div style='overflow-x:auto'>{html}</div>"

    def show(self, *, width: int = 120) -> None:
        """
        Auto-display:
        - Terminal: rich print
        - Jupyter: HTML display
        """
        c = Console()
        if c.is_terminal:
            self.print(console=c)
            return

        # Jupyter / non-terminal: render to HTML and display
        try:
            from IPython.display import HTML, display  # type: ignore
        except Exception:
            # Fallback if IPython isn't available
            print(self.to_plain(width=width))
            return

        # display(HTML(self.to_html(width=width)))
        return HTML(self.to_html(width=width, pad_to_width=False))


# ----------------------------
# Logging handler that accepts renderables
# ----------------------------

class RichRenderableHandler(logging.Handler):
    """
    A logging handler that prints Rich renderables directly (including Group/Text).
    If record.msg isn't renderable, it prints record.getMessage().
    """
    def __init__(self, console: Optional[Console] = None, level: int = logging.NOTSET) -> None:
        super().__init__(level)
        self.console = console or Console()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg_obj = record.msg
            if is_renderable(msg_obj):  # Rich renderable protocol check :contentReference[oaicite:7]{index=7}
                renderable = msg_obj
            else:
                renderable = Text(record.getMessage())

            header = Text(f"{record.levelname}: ", style="bold")
            self.console.print(Group(header, renderable))
        except Exception:
            self.handleError(record)


# ----------------------------
# Example usage
# ----------------------------

def main():
    diff = RichDiff(TEST_OLD, TEST_NEW)

    # 1) Terminal
    # diff.print()

    # 2) Logging (renderable-aware handler for rich console logs)
    logger = logging.getLogger("diff")
    logger.setLevel(logging.INFO)
    logger.addHandler(RichRenderableHandler())

    logger.info(diff.renderable())  # logs as a Rich renderable

    # For a plain file handler, use diff.to_plain() (or to_ansi() for ANSI-capable logs)
    # file_logger = logging.getLogger("file")
    # file_logger.addHandler(logging.FileHandler("diff.log"))
    # file_logger.info("\n%s", diff.to_plain())

    # 3) Jupyter
    # diff.show()
