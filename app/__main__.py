import typing as t

import typer
from fastapi_cli.cli import app as fastapi_app

app = typer.Typer(
    name="Youtube-Downloader-API",
    help="Utility commands for Youtube-Downloader-API",
)


@app.command()
def delete_expired_extracts(
    quiet: t.Annotated[bool, typer.Option(help="Do not stdout anything")] = False,
):
    """Delete cached extracted-infos that have expired"""
    from app.events import event_all_delete_expired_extracted_info

    time_offset = event_all_delete_expired_extracted_info()
    if not quiet:
        print(
            "[INFO] Extracts successfully deleted [ Time Offset : "
             f" {time_offset} ]"
        )


fastapi_app.add_typer(app, name="utils")

fastapi_app()
