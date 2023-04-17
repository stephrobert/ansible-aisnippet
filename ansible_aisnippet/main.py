from pathlib import Path
from re import template
from ansible_aisnippet import __version__
from ansible_aisnippet.aisnippet import aisnippet
from typing import Optional
from ansible_aisnippet.helpers import load_yaml
from ansible_aisnippet.helpers import save_yaml_to_file
from rich.console import Console

from .helpers import convert_to_yaml

import typer
import os
import sys
import shutil


app = typer.Typer()

def _version_callback(value: bool) -> None:
    if value:
        versionText = typer.style(
            f"ansible-aisnippet v{__version__}",
            fg=typer.colors.RED,
            bg=typer.colors.WHITE,
        )
        typer.echo(versionText)
        raise typer.Exit()

@app.command()
def generate(
    text: Optional[str] = typer.Argument(default="Install package htop", help="A description of task to get"),
    verbose: Optional[bool] = typer.Option(
        False, "--verbose", "-v", help="verbose mode"
    ),
    filetasks: Optional[Path] = typer.Option(None, "--filetasks", "-f", exists=True),
    outputfile: Optional[Path] = typer.Option(None, "--outputfile", "-o", exists=False),
    playbook: Optional[bool] = typer.Option(
        False, "--playbook", "-p", help="Create a playbook"
    )
):
    """
    Ask ChatGPT to write an ansible task using a template
    """
    # Generate tasks from a file os tasks (yaml)
    if filetasks is not None:
        assistant = aisnippet(verbose=verbose)
        tasks = load_yaml(filetasks)
        output_tasks = assistant.generate_tasks(tasks)
        if playbook:
            output = [
                    {
                        "name": "Playbook generated with chatgpt",
                        "hosts": "all",
                        "gather_facts": True,
                        "tasks": output_tasks
                    }
            ]
        else:
            output = output_tasks
        if outputfile is not None:
            save_yaml_to_file(outputfile,output)
        else:
            console = Console()
            console.print("Result: \n", style="red")
            console.print(convert_to_yaml(output))
    # Generate a single task from an sentence
    else:
        console = Console()
        assistant = aisnippet(verbose=verbose)
        task = assistant.generate_task(text)
        console.print("Result: \n", style="red")
        console.print(convert_to_yaml(task))


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    return


if __name__ == "__main__":
    app()
