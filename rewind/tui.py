"""Terminal UI for time-travel debugging."""

from typing import Optional, List
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from rewind.player import Player, FrameInfo


class DebuggerTUI:
    """Terminal-based debugger interface."""

    def __init__(self, trace_path: str):
        self.player = Player(trace_path)
        self.current_index = 0
        self.console = Console()
        self.running = True

    def run(self) -> None:
        """Start the TUI main loop."""
        self.render()

        while self.running:
            try:
                key = self.console.input("[dim]Press key: [/]").strip().lower()
                
                if key == '' or key == 'right' or key == 'd':
                    if self.current_index < self.player.frame_count - 1:
                        self.current_index += 1
                        self.render()
                elif key == 'left' or key == 'a':
                    if self.current_index > 0:
                        self.current_index -= 1
                        self.render()
                elif key == 'g':
                    self._prompt_goto()
                elif key == 'd':
                    if self.current_index > 0:
                        self._show_diff(self.current_index - 1, self.current_index)
                elif key == 's':
                    self._prompt_search()
                elif key == 'q':
                    self.running = False
                elif key == 'h':
                    self._show_help()
            except KeyboardInterrupt:
                break
            except EOFError:
                break

        self.player.close()

    def render(self) -> None:
        """Render the current debugger view."""
        self.console.clear()

        frame = self.player.get_frame(self.current_index)

        progress = f"Frame {self.current_index + 1} / {self.player.frame_count}"
        self.console.print(Panel(progress, title="Rewind Debugger", border_style="cyan"))

        self._render_location(frame)
        self._render_variables(frame)
        self._render_help_bar()

    def _render_location(self, frame: FrameInfo) -> None:
        """Render current file and line location."""
        location_text = f"{frame.filename}:{frame.line_no} in {frame.function_name}()"

        self.console.print(Panel(
            location_text,
            title="Location",
            border_style="green",
        ))

    def _render_variables(self, frame: FrameInfo) -> None:
        """Render local variables table."""
        if not frame.locals:
            self.console.print("[dim]No local variables[/dim]")
            return

        table = Table(title="Local Variables", box=box.ROUNDED)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Type", style="dim")

        for name, value in list(frame.locals.items())[:20]:
            value_str = str(value)
            if len(value_str) > 60:
                value_str = value_str[:57] + "..."

            table.add_row(
                name,
                value_str,
                type(value).__name__,
            )

        self.console.print(table)

    def _render_help_bar(self) -> None:
        """Render keyboard shortcuts help."""
        help_text = (
            "[cyan]← or A[/] Prev  "
            "[cyan]→ or D[/] Next  "
            "[cyan]G[/] Goto  "
            "[cyan]D[/] Diff  "
            "[cyan]S[/] Search  "
            "[cyan]H[/] Help  "
            "[cyan]Q[/] Quit"
        )
        self.console.print(Panel(help_text, title="Shortcuts", border_style="dim"))

    def _prompt_goto(self) -> None:
        """Prompt user for frame number to jump to."""
        try:
            target = int(self.console.input(f"\n[yellow]Enter frame number (0-{self.player.frame_count - 1}): [/]"))
            if 0 <= target < self.player.frame_count:
                self.current_index = target
                self.render()
            else:
                self.console.print("[red]Invalid frame number[/]")
        except ValueError:
            self.console.print("[red]Please enter a valid number[/]")

    def _show_diff(self, index_a: int, index_b: int) -> None:
        """Show diff between two frames."""
        diff = self.player.diff_frames(index_a, index_b)

        self.console.clear()
        self.console.print(f"[bold cyan]Diff: Frame {index_a} → Frame {index_b}[/]\n")

        if diff['added']:
            self.console.print("[green]Added:[/]")
            for var in diff['added']:
                self.console.print(f"  + {var}")

        if diff['removed']:
            self.console.print("[red]Removed:[/]")
            for var in diff['removed']:
                self.console.print(f"  - {var}")

        if diff['modified']:
            self.console.print("[yellow]Modified:[/]")
            for var, changes in diff['modified'].items():
                before = repr(changes['before'])
                after = repr(changes['after'])
                self.console.print(f"  {var}: {before} → {after}")

        if not any([diff['added'], diff['removed'], diff['modified']]):
            self.console.print("[dim]No changes between frames[/]")

        self.console.input("\n[dim]Press Enter to continue...[/]")
        self.render()

    def _prompt_search(self) -> None:
        """Search for variable across all frames."""
        var_name = self.console.input("[yellow]Variable name to search: [/]").strip()

        if not var_name:
            return

        results = self.player.search_variable(var_name)

        self.console.clear()
        self.console.print(f"[bold]Search results for '{var_name}':[/]\n")

        if not results:
            self.console.print("[dim]Not found in any frame[/]")
        else:
            for idx, value in results[:50]:
                self.console.print(f"  Frame {idx}: {repr(value)[:80]}")

        self.console.input("\n[dim]Press Enter to continue...[/]")
        self.render()

    def _show_help(self) -> None:
        """Show full help screen."""
        help_content = """
Rewind Debugger - Commands

Navigation:
  → or D   Next frame
  ← or A   Previous frame
  G        Go to specific frame number

Analysis:
  D        Show diff with previous frame
  S        Search for variable across all frames

General:
  H        Show this help screen
  Q        Quit debugger

Tips:
  - Variables are captured at each line of execution
  - Use diff to quickly find what changed
  - Search helps locate when a variable appears
"""
        self.console.clear()
        self.console.print(Panel(help_content.strip(), title="Help", border_style="cyan"))
        self.console.input("\n[dim]Press Enter to continue...[/]")
        self.render()