import os
import sys
import pathlib
import json
import base64
import argparse

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2] / "lib"))
import common

parser = argparse.ArgumentParser()
parser.add_argument("host", help="Router name or IP address")
options = parser.parse_args()

credentials = json.loads(base64.b64decode(os.environ["AO_MIKROTIK_CREDENTIALS"]).decode("utf-16"))
ssh_client = common.ssh_connect(options.host, credentials)
common.reboot_host(ssh_client, options.host, credentials)

# print(f"there you go: {os.environ['AO_MIKROTIK_CREDENTIALS']}")
