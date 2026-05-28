"""Command-line interface for Rewind."""

import sys
import click
from pathlib import Path

from rewind import __version__
from rewind.recorder import Recorder
from rewind.player import Player
from rewind.tui import DebuggerTUI
from rewind.exceptions import RewindError


@click.group()
@click.version_option(version=__version__)
def cli():
    """Rewind - Time-travel debugging for Python.

    Record program execution and travel back in time to fix bugs.
    """
    pass


@cli.command()
@click.argument('script', type=click.Path(exists=True))
@click.option('--output', '-o', default='trace.db', help='Output trace file')
@click.option('--args', '-a', default='', help='Arguments to pass to script')
def record(script: str, output: str, args: str) -> None:
    """Record execution of a Python script.

    Example:
        rewind record my_script.py -o bug.trace
    """
    click.echo(f"🎬 Recording: {script} -> {output}")

    recorder = Recorder(output)

    try:
        recorder.start()

        with open(script, 'r') as f:
            code = f.read()

        exec_globals = {'__name__': '__main__', '__file__': script}
        exec(code, exec_globals)

        recorder.stop()
        click.echo(f"✅ Trace saved to {output}")

    except Exception as e:
        click.echo(f"❌ Recording failed: {e}", err=True)
        sys.exit(1)
    finally:
        recorder.stop()


@cli.command()
@click.argument('trace', type=click.Path(exists=True))
@click.option('--frame', '-f', type=int, help='Start at specific frame')
def replay(trace: str, frame: int) -> None:
    """Replay a recorded trace.

    Example:
        rewind replay trace.db
    """
    click.echo(f"🎮 Replaying: {trace}")

    try:
        tui = DebuggerTUI(trace)

        if frame is not None:
            tui.current_index = frame

        tui.run()

    except RewindError as e:
        click.echo(f"❌ Replay failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('trace', type=click.Path(exists=True))
@click.argument('frame_a', type=int)
@click.argument('frame_b', type=int)
def diff(trace: str, frame_a: int, frame_b: int) -> None:
    """Show differences between two frames.

    Example:
        rewind diff trace.db 5 10
    """
    with Player(trace) as player:
        try:
            diff_result = player.diff_frames(frame_a, frame_b)

            click.echo(f"\n📊 Diff: Frame {frame_a} → Frame {frame_b}\n")

            if diff_result['added']:
                click.echo(f"🟢 Added: {', '.join(diff_result['added'])}")

            if diff_result['removed']:
                click.echo(f"🔴 Removed: {', '.join(diff_result['removed'])}")

            if diff_result['modified']:
                click.echo("🟡 Modified:")
                for var, changes in diff_result['modified'].items():
                    click.echo(f"    {var}: {changes['before']} → {changes['after']}")

            if not any(diff_result.values()):
                click.echo("No changes between frames")

        except RewindError as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)


@cli.command()
@click.argument('trace', type=click.Path(exists=True))
@click.argument('var_name')
def search(trace: str, var_name: str) -> None:
    """Search for a variable across all frames.

    Example:
        rewind search trace.db user_id
    """
    with Player(trace) as player:
        results = player.search_variable(var_name)

        click.echo(f"\n🔍 Searching for '{var_name}' in {trace}\n")

        if not results:
            click.echo(f"❌ Variable '{var_name}' not found in any frame")
        else:
            click.echo(f"Found in {len(results)} frame(s):\n")
            for idx, value in results[:20]:
                click.echo(f"  Frame {idx:4d}: {repr(value)[:100]}")

            if len(results) > 20:
                click.echo(f"\n  ... and {len(results) - 20} more")


@cli.command()
def info():
    """Show information about Rewind."""
    click.echo(f"""
╭──────────────────────────────────╮
│  Rewind v{__version__} - Time-Travel Debugger  │
╰──────────────────────────────────╯

📦 Installation: pip install rewind
📖 Documentation: https://github.com/rewind/rewind
💬 Issues: https://github.com/rewind/rewind/issues

Commands:
  record    Record program execution
  replay    Open TUI debugger
  diff      Compare two frames
  search    Find variable across frames
""")


def main():
    """Entry point for console script."""
    cli()


if __name__ == '__main__':
    main()