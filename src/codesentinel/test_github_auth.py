import os

from dotenv import load_dotenv

from codesentinel.github.auth import create_installation_token


load_dotenv()


def main():
    installation_id = int(
        os.environ["GITHUB_INSTALLATION_ID"]
    )

    token = create_installation_token(
        installation_id
    )

    print("GitHub App authentication successful.")
    print("Installation token received.")


if __name__ == "__main__":
    main()
