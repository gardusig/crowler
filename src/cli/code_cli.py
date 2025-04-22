import typer
from util.ai_util import get_ai_client, send_message

from util.instruction_util import load_instructions

code_app = typer.Typer(help="📁 Code management CLI")


@code_app.command()
def evaluate():
    instructions = load_instructions("instructions/code.json")
    if not instructions:
        print("⚠️ No instructions were loaded.")
        return
    ai_client = get_ai_client()
    response = send_message(ai_client, instructions)
    print(response)
