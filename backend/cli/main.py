import typer

from cli.bootstrap.app import bootstrap_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(bootstrap_app, name="bootstrap")

if __name__ == "__main__":
    app()
