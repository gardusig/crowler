from dotenv import load_dotenv
from crowler.cli.app import app


def main():
    load_dotenv()
    app()


if __name__ == "__main__":
    main()
