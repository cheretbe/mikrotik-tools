# No shebang as this script is intended to be run via bash wrapper only

import os
import argparse
import json
import base64
import getpass
import humanfriendly.prompts


def main():

    parser = argparse.ArgumentParser(description="Prompts for credentials")
    parser.add_argument(
        "-p", "--env-var-pipe-handle", type=int, default=-1,
        help="File handle for a named pipe to return AO_MIKROTIK_CREDENTIALS env variable"
    )
    options = parser.parse_args()

    if "AO_MIKROTIK_CREDENTIALS" in os.environ:
        credentials = json.loads(
            base64.b64decode(os.environ["AO_MIKROTIK_CREDENTIALS"]).decode("utf-16")
        )
    else:
        credentials = {"username": "", "password": ""}

    prompt_for_credentials = True
    if credentials["username"]:
        prompt_for_credentials = not humanfriendly.prompts.prompt_for_confirmation(
            f"Use cached credentials for user '{credentials['username']}'?", default=True
        )
    if prompt_for_credentials:
        print("Enter credentials")
        credentials["username"] = humanfriendly.prompts.prompt_for_input(
            f"  User name (default={credentials['username']}): ",
            default=credentials["username"],
            padding=False
        )
        credentials["password"] = getpass.getpass("  Password: ")

    if options.env_var_pipe_handle != -1:
        encoded_credentials = base64.b64encode(json.dumps(credentials).encode("utf-16"))
        with os.fdopen(options.env_var_pipe_handle, "w") as env_var_pipe_fd:
            env_var_pipe_fd.write(f"{encoded_credentials.decode('ascii')}\n")

if __name__ == "__main__":
    main()
