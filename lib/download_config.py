# No shebang as this script is intended to be run via bash or batch wrapper only

import os
import sys
import pathlib
import base64
import json
import argparse
import datetime
import colorama
sys.path.append(os.path.dirname(__file__))
import common


colorama.init()


def main():
    parser = argparse.ArgumentParser(description="Config backup utility for Mikrotik routers")
    parser.add_argument(
        "hosts", metavar="host_name", nargs="*", default="", help="Router name or IP address"
    )
    options = parser.parse_args()

    credentials = json.loads(base64.b64decode(os.environ["AO_MIKROTIK_CREDENTIALS"]).decode("utf-16"))
    if not credentials["username"]:
        sys.exit("ERROR: Empty user name has been provided")

    dest_path = (
        pathlib.Path(common.get_documents_path()) / "mikrotik-tools" /
        datetime.datetime.now().strftime("%Y-%m-%d")
    )

    config_file_name = common.get_config_file_path()
    if os.path.isfile(config_file_name):
        with open(config_file_name) as conf_f:
            config = json.load(conf_f)
    else:
        config = {"recent_hosts": []}

    if not options.hosts:
        # [!] Saving user selection as list
        options.hosts = [common.select_host(config["recent_hosts"])]

    for host in options.hosts:
        print(
            colorama.Fore.CYAN + colorama.Style.BRIGHT +
            f"=== Saving configuration for '{host}' ===" +
            colorama.Style.RESET_ALL
        )

        # Saving host before connecting to save some typing in case something
        # went wrong
        try:
            config["recent_hosts"].pop(config["recent_hosts"].index(host))
        except ValueError:
            pass
        config["recent_hosts"].insert(0, host)
        with open(config_file_name, "w", encoding="utf-8") as conf_f:
            json.dump(config, conf_f, ensure_ascii=False, indent=4)

        bin_backup_dst = host + "_old.backup"
        config_backup_dst = host + "_old.rsc"
        if (pathlib.Path(dest_path) / config_backup_dst).is_file():
            print("  Old configuration exists. Creating an update")
            bin_backup_dst = host + "_new.backup"
            config_backup_dst = host + "_new.rsc"


        ssh_client = common.ssh_connect(host, credentials)

        bin_backup, config_backup = common.get_backup_file_names(ssh_client)

        print(f"  Creating '{bin_backup}'")
        common.exec_ssh_command(ssh_client, "/system backup save name=" + bin_backup)

        print(f"  Creating '{config_backup}'")
        common.exec_ssh_command(ssh_client, "/export terse file=" + config_backup)

        print(f"  Saving config to '{str(dest_path)}'")
        os.makedirs(dest_path, exist_ok=True)

        sftp_client = ssh_client.open_sftp()

        print(f"  Downloading '{bin_backup}' as '{bin_backup_dst}'")
        sftp_client.get(bin_backup, str(pathlib.Path(dest_path) / bin_backup_dst))
        print(f"  Removing '{bin_backup}'")
        sftp_client.remove(bin_backup)

        print(f"  Downloading '{config_backup}' as '{config_backup_dst}'")
        sftp_client.get(config_backup, str(pathlib.Path(dest_path) / config_backup_dst))
        print(f"  Removing '{config_backup}'")
        sftp_client.remove(config_backup)

        sftp_client.close()

        print(
            colorama.Fore.GREEN + colorama.Style.BRIGHT +
            f"{host}: done" +
            colorama.Style.RESET_ALL
        )

if __name__ == "__main__":
    main()
