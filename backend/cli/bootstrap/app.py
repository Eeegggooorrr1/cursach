import typer

from .load_seed import load_seed

bootstrap_app = typer.Typer(help="Bootstrap commands")
bootstrap_app.command("load-seed")(load_seed)
