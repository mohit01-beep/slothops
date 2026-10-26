import sys
import os
from pathlib import Path
import click
import uvicorn

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .config import HOST, PORT, DEFAULT_MODEL
from .engine.llm_client import LLMClient
from .engine.summarizer import MorningBriefEngine
from .engine.sorter import ClutterSorter
from .engine.winddown import WindDownEngine

@click.group()
def cli():
    """🦥 SlothOps: Slow & Steady Local-First AI Agent for Effortless Workspace & Life Hygiene."""
    pass

@cli.command()
def status():
    """Check connection to local open-source models (Ollama / LocalAI)."""
    client = LLMClient()
    info = client.check_availability()
    click.echo("\n🦥 SlothOps System Status:")
    click.echo(f"  • Provider: {info.get('provider')}")
    click.echo(f"  • Endpoint: {info.get('endpoint')}")
    click.echo(f"  • Available Models: {', '.join(info.get('models', [])) or 'None (using fallback)'}")
    click.echo(f"  • Active Model: {info.get('active_model')}")
    if info.get("available"):
        click.secho("  ✓ Open-Weight Local Inference is Ready!", fg="green", bold=True)
    else:
        click.secho("  ! Running in Zero-Config Fallback mode (No Ollama daemon needed).", fg="yellow")
    click.echo()

@cli.command()
@click.option("--notes", "-n", default="", help="Raw notes, to-dos, or thought dump")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read notes from a text file")
def brief(notes: str, file: str):
    """Generate a calm, slow-and-steady morning brief."""
    content = notes
    if file:
        content = Path(file).read_text(encoding="utf-8", errors="ignore")

    if not content:
        click.echo("Paste your raw messy to-dos or thoughts (Press Ctrl+D or Ctrl+Z then Enter to finish):")
        content = sys.stdin.read()

    client = LLMClient()
    engine = MorningBriefEngine(client)
    res = engine.generate_brief(content)

    click.secho("\n═════════════════════════════════════════════════════════════════", fg="cyan")
    click.secho("               🦥  YOUR MORNING SLOTH BRIEFING                  ", fg="cyan", bold=True)
    click.secho("═════════════════════════════════════════════════════════════════", fg="cyan")
    click.secho(f"Engine: {res.get('engine_used')} | Minutes Saved: ~{res.get('time_saved_minutes')}m\n", fg="bright_black")

    click.secho("🎯 TOP HIGH-IMPACT PRIORITIES (Do these calmly):", fg="green", bold=True)
    for idx, item in enumerate(res.get("high_impact", []), 1):
        click.echo(f"   {idx}. {item}")

    click.secho("\n🦥 PERMISSION TO PROCRASTINATE (Leave these for tomorrow):", fg="yellow", bold=True)
    for idx, item in enumerate(res.get("safe_to_ignore", []), 1):
        click.echo(f"   {idx}. {item}")

    click.secho("\n🧘 SLOTH WISDOM OF THE DAY:", fg="magenta", bold=True)
    click.echo(f"   \"{res.get('wisdom')}\"\n")

@cli.command()
@click.argument("directory", type=click.Path(exists=True), default=".")
@click.option("--execute", is_flag=True, help="Actually move files instead of dry-run preview")
def tidy(directory: str, execute: bool):
    """Scan and organize cluttered folders into neat semantic categories."""
    client = LLMClient()
    sorter = ClutterSorter(client)
    scan = sorter.scan_directory(directory)

    items = scan.get("items", [])
    if not items:
        click.echo(f"No loose files found in {directory} to organize. Already clean!")
        return

    click.echo(f"\nFound {len(items)} file(s) in {directory}:\n")
    for it in items:
        click.echo(f"  • {it['filename']}  ──>  [{it['suggested_category']}]")

    if not execute:
        click.secho("\n[Dry Run] No files moved. Run with --execute to apply changes.", fg="yellow")
    else:
        click.secho("\nOrganizing files now...", fg="cyan")
        result = sorter.execute_tidy(items)
        click.secho(f"✓ Moved {result['moved_count']} files safely into organized folders!", fg="green", bold=True)

@cli.command()
@click.option("--wins", "-w", default="", help="What you completed today")
def unwind(wins: str):
    """Generate an evening wind-down reflection and release work anxiety."""
    if not wins:
        click.echo("What did you work on or finish today? (Press Ctrl+D or Ctrl+Z then Enter to finish):")
        wins = sys.stdin.read()

    client = LLMClient()
    engine = WindDownEngine(client)
    res = engine.generate_winddown(wins)

    click.secho("\n🌙 EVENING SLOTH WIND-DOWN", fg="blue", bold=True)
    click.echo(f"Recap: {res.get('recap')}")
    click.secho(f"\n{res.get('permission_to_rest')}", fg="green")
    click.secho(f"Mantra: \"{res.get('tomorrow_mantra')}\"", fg="cyan", bold=True)
    soundscape = res.get("soundscape", {})
    click.echo(f"\nRecommended Soundscape: {soundscape.get('name')} ({soundscape.get('description')})\n")

@cli.command()
@click.option("--host", default=HOST, help="Host to bind")
@click.option("--port", default=PORT, type=int, help="Port to bind")
def serve(host: str, port: int):
    """Launch the SlothOps Web Dashboard."""
    click.secho(f"\n🦥 Launching SlothOps Dashboard on http://{host}:{port}", fg="cyan", bold=True)
    click.echo("Press Ctrl+C to stop.\n")
    uvicorn.run("slothops.server:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    cli()
