from crowler.instruction.instruction_model import Instruction

README_INSTRUCTION = Instruction(
    instructions=[
        "Craft a detailed and up-to-date README for the project.",
        "Maintain a professional yet approachable tone, with a hint of humor,"
        "focusing on exposed APIs or CLI.",
        "Use headers for each section, enhanced with relevant emojis for improved"
        "readability.",
        "Include usage examples within code blocks using '```'"
        "fences to illustrate commands and expected outputs.",
        "Provide environment setup instructions with clear code snippets,"
        "especially for macOS using Homebrew.",
        "Detail project setup and installation steps for newcomers.",
        "Don't add '---' between sections of the README.",
    ]
)
