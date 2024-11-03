import sys
from typing import Optional, Union

import typer
from .folio import Folio
import os
from rich.console import Console
from rich.table import Table

app = typer.Typer()

FOLIO_DIR = "folio"
FOLIO_DB_PATH = 'folio/folio.db'


def get_folio_object() -> Folio:
    if not os.path.exists(FOLIO_DIR):
        raise Exception(f'Cannot find directory {FOLIO_DIR}')

    if not os.path.exists(FOLIO_DB_PATH):
        raise Exception(f'Cannot find folio database at {FOLIO_DB_PATH}')

    folio_obj = Folio(FOLIO_DIR)
    return folio_obj


@app.command()
def list_prompts():
    folio_obj = get_folio_object()
    console = Console()
    prompts = folio_obj.list_prompts()

    if len(prompts) > 0:
        table = Table("Id", "Prompt Name", "Versions", show_header=True, header_style="bold magenta")
        idx = 1
        for prompt in prompts:
            table.add_row(str(idx), prompt.name, str(prompt.num_versions))
            idx += 1
        console.print(table)
    else:
        console.print(f"No prompts found !")


@app.command()
def list_versions(prompt_name: str):
    folio_obj = get_folio_object()
    console = Console()
    prompts = folio_obj.list_versions_by_prompt(prompt_name)

    if (not prompts) or (len(prompts) < 1):
        console.print(f"No versions for this prompt found !")
        sys.exit(1)

    table = Table("Id", "Prompt Name", "Version", "Created At", show_header=True,
                  header_style="bold magenta")  # Add Date Added here
    idx = 1
    for prompt in prompts:
        table.add_row(str(idx), prompt.name, str(prompt.version), prompt.created_at)
        idx += 1
    console.print(table)


@app.command()
def show(prompt_name: str, version: Optional[int] = None):
    folio_obj = get_folio_object()
    prompt = folio_obj.get_prompt(prompt_name, version)
    console = Console()
    if prompt is None:
        console.print(f"Cannot find prompt = {prompt_name} / version = {version}")
        return None

    console.print(prompt.text)


@app.command("init")
def create_project():
    project_id = Folio.init()
    console = Console()
    console.print(f"Initialized folio project under folio/")


@app.command()
def add(prompt_name: str,
        filename: Optional[str] = typer.Option(None, "--file", help="Read prompt from file")):
    prompt_text = None
    if filename:
        prompt_text = open(filename).read()
    elif not sys.stdin.isatty():
        prompt_text = sys.stdin.read()
    else:
        raise typer.BadParameter("Provide input either as --file or from stdin")

    folio_obj = get_folio_object()

    console = Console()

    prompt = folio_obj.add_prompt(prompt_name, prompt_text)
    console.print(f"Created prompt {prompt_name} with version={prompt.version}")


@app.command()
def delete_version(prompt_name: str, version: Optional[int] = None, latest: Optional[bool] = None):
    if latest is None and version is None:
        raise typer.BadParameter("Either --latest or --version must be provided")

    if ( latest is not None ) and (version is not None):
        raise typer.BadParameter("Either --latest or --version must be provided, not both")

    if version is None:
        version = "latest"

    folio_obj = get_folio_object()
    console = Console()
    try:
        folio_obj.delete_version(prompt_name, version)
        console.print(f"Deleted prompt {prompt_name} with version={version}")

        prev_prompt = folio_obj.get_latest_prompt(prompt_name)
        if prev_prompt is not None:
            console.print(f"Latest version of the prompt now is {prev_prompt.version}")
        else:
            console.print(f"No existing versions of the prompt remain. Hence prompt deleted")

    except Exception as e:
        console.print(f"Unable to delete prompt={prompt_name} / version={version}")
        console.print(e)
