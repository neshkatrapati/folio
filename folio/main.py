import sys
from typing import Optional

import typer
from .folio import Folio
import os
from rich.console import Console
from rich.table import Table

app = typer.Typer()

FOLIO_DB_PATH = 'FOLIO_DB_PATH'

def get_folio_object():
    if FOLIO_DB_PATH not in os.environ:
        raise Exception('FOLIO_DB_PATH environment variable has not been set')

    db_path = os.environ['FOLIO_DB_PATH']
    folio_obj = Folio(db_path)
    return folio_obj

@app.command()
def list_projects():
    folio_obj = get_folio_object()
    projects = folio_obj.list_projects()
    console = Console()
    if len(projects) > 0:
        table = Table("Id", "Project Name", "Created At", show_header=True, header_style="bold magenta")
        for project in projects:
            table.add_row(project.id, project.name, project.created_at)
        console.print(table)
    else:
        console.print("No Projects Found")

@app.command()
def list_prompts(project_name:str):
    folio_obj = get_folio_object()
    console = Console()
    prompts = folio_obj.list_prompts_by_project_name(project_name)
    if prompts is None:
        console.print(f"No such project called {project_name}")
        return None
    if len(prompts) > 0:
        table = Table("Id", "Prompt Name", "Versions", show_header=True, header_style="bold magenta")
        idx = 1
        for prompt in prompts:
            table.add_row( str(idx),prompt.name, str(prompt.num_versions))
            idx += 1
        console.print(table)
    else:
        console.print(f"No prompts found under project={project_name}")

@app.command()
def list_versions(project_name:str, prompt_name:str):
    folio_obj = get_folio_object()
    console = Console()
    prompts = folio_obj.list_versions_by_prompt(project_name, prompt_name)
    if prompts is None:
        console.print(f"No such project called {project_name}")
        return None

    table = Table("Id", "Prompt Name", "Version", "Created At", show_header=True, header_style="bold magenta") # Add Date Added here
    idx = 1
    for prompt in prompts:
        table.add_row( str(idx),prompt.name, str(prompt.version), prompt.created_at)
        idx += 1
    console.print(table)


@app.command()
def show_prompt(project_name:str, prompt_name:str, version:Optional[int]=None):
    folio_obj = get_folio_object()
    prompt = folio_obj.get_prompt(project_name, prompt_name, version)
    console = Console()
    if prompt is None:
        console.print(f"Cannot find project = {project_name} / prompt = {prompt_name} / version = {version}")
        return None
    
    console.print(prompt.text)

@app.command()
def create_project(project_name:str):
    folio_obj = get_folio_object()
    project_id = folio_obj.create_project(project_name)
    console = Console()
    console.print(f"Created a new project with id={project_id}")

@app.command()
def add_prompt(project_name:str, prompt_name:str, filename: Optional[str] = typer.Option(None, "--file", help="Read prompt from file")):
    prompt_text = None
    if filename:
        prompt_text = open(filename).read()
    elif not sys.stdin.isatty():
        prompt_text = sys.stdin.read()
    else:
        raise typer.BadParameter("Provide input either as --file or from stdin")

    folio_obj = get_folio_object()
    project = folio_obj.find_project_by_name(project_name)
    console = Console()
    if project is None:
        console.print(f"No such project called {project_name}")
        return None

    prompt = folio_obj.add_prompt(project_name, prompt_name, prompt_text)
    console.print(f"Created prompt {prompt_name} under project {project_name} with version={prompt.version}")


