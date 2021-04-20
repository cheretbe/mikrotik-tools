# No shebang as this script is intended to be run via bash or batch wrapper only

import os
import sys
import pathlib
import base64
import json
import argparse
import time
import datetime
import distutils.version
import colorama
import humanfriendly.prompts
sys.path.append(os.path.dirname(__file__))
import common


colorama.init()

def upgrade_firmware(host, ssh_client, credentials):
    print("  Checking firmware version")
    firmware_data = common.exec_ssh_command(
        ssh_client,
        (
            ":put [/system resource get architecture-name];" +
            ":put [/system routerboard get upgrade-firmware];" +
            ":put [/system routerboard get current-firmware]"
        ),
        echo=False
    )
    if firmware_data[0] in ["x86", "x86_64"]:
        print(f"  Skipping firmware upgrade for {firmware_data[0]} platform")
    else:
        if firmware_data[1] == firmware_data[2]:
            print(f"  Firmware {firmware_data[2]} doesn't need an upgrade")
        else:
            if (
                    distutils.version.LooseVersion(firmware_data[1]) <
                    distutils.version.LooseVersion(firmware_data[2])
                ):
                operation = "a DOWNGRADE"
            else:
                operation = "an upgrade"
            print(
                f"  Firmware needs {operation} from version {firmware_data[2]} "
                f"to version {firmware_data[1]}"
            )
            if humanfriendly.prompts.prompt_for_confirmation(
                    f"Continue with {operation}?", default=True
            ):
                common.exec_ssh_command(ssh_client, "/system routerboard upgrade")
                wait_for_firmware_upgrade(ssh_client)
                common.reboot_host(ssh_client, host)
                # TODO: Wait for reboot

def upgrade_ros(host, ssh_client, credentials):
    print("  Getting current release channel")
    channel = common.exec_ssh_command(
        ssh_client,
        ":put [/system package update get channel]",
        echo=False
    )[0]
    print(f"  Release channel: {channel}")
    if channel not in ["stable", "long-term"]:
        sys.exit("ERROR: unsupported release channel: " + channel)

    if channel == "stable":
        if humanfriendly.prompts.prompt_for_confirmation(
                (
                    "Would you like to change 'stable' release channel " +
                    f"to 'long-term' on router '{host}'?"
                ),
                default=False
        ):
            print("  Changing release channel to 'long-term'")
            common.exec_ssh_command(ssh_client, "/system package update set channel=long-term")

    print("  Checking for packages upgrade")
    upgrade_data = common.exec_ssh_command(
        ssh_client,
        (
            "/system package update check-for-updates as-value;" +
            ":put [/system package update get]"
        ),
        echo=False
    )[0]
    # "Name1=Value1;Name2=Value2" ==> {"Name1": "Value1", "Name2": "Value2"}
    upgrade_data = dict(item.split("=") for item in upgrade_data.split(";"))
    if "latest-version" not in upgrade_data:
        sys.exit(f"ERROR: Couldn't get packages upgrade status ({upgrade_data['status']})")
    if upgrade_data["installed-version"] == upgrade_data["latest-version"]:
        print(f"  System is up to date ({upgrade_data['installed-version']})")
    else:
        if (
                distutils.version.LooseVersion(upgrade_data["installed-version"]) <
                distutils.version.LooseVersion(upgrade_data["latest-version"])
            ):
            print("  New version is available")
            operation = "upgrade"
            default_answer = True
        else:
            operation = "downgrade"
            print(
                colorama.Fore.YELLOW + colorama.Style.BRIGHT +
                "WARNING: installed version is greater than latest released one" +
                colorama.Style.RESET_ALL
            )
            default_answer = False
        if humanfriendly.prompts.prompt_for_confirmation(
                (
                    f"Would you like to {operation} RouterOS from version " +
                    f"{upgrade_data['installed-version']} to version "
                    f"{upgrade_data['latest-version']} on router '{host}'?"
                ),
                default=default_answer
        ):
            common.save_backup(host, ssh_client)

            print("  Downloading update")
            common.exec_ssh_command(ssh_client, "/system package update download as-value")
            common.reboot_host(ssh_client, host, credentials)
            version_after_update = common.exec_ssh_command(
                ssh_client,
                cmd=":put [/system package update get installed-version]",
                echo=False
            )[0]
            print(f"  Version after upgrade: {version_after_update}")
            if version_after_update != upgrade_data["latest-version"]:
                raise Exception(
                    f"RouterOS version {version_after_update} differs "
                    f"from expected version {upgrade_data['latest-version']}"
                )
            common.save_backup(host, ssh_client)

def wait_for_firmware_upgrade(ssh_client):
    print("  Waiting for firmware upgrade to finish")
    for i in range(4):
        log_lines = common.exec_ssh_command(
            ssh_client,
            '/log print where topics="system;info;critical"',
            echo=False
        )
        if any("Firmware upgraded successfully" in line for line in log_lines):
            return
        time.sleep(2)
    sys.exit("ERROR: timeout waiting for upgrade")

def main():
    parser = argparse.ArgumentParser(description="Config backup utility for Mikrotik routers")
    parser.add_argument(
        "hosts", metavar="host_name", nargs="*", default="", help="Router name or IP address"
    )
    options = parser.parse_args()

    credentials = json.loads(base64.b64decode(os.environ["AO_MIKROTIK_CREDENTIALS"]).decode("utf-16"))
    if not credentials["username"]:
        sys.exit("ERROR: Empty user name has been provided")

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
            f"=== Upgrading RouterOS and firmware on '{host}' ===" +
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

        ssh_client = common.ssh_connect(host, credentials)

        upgrade_firmware(host, ssh_client, credentials)

        upgrade_ros(host, ssh_client, credentials)

        ssh_client.close()

        print(
            colorama.Fore.GREEN + colorama.Style.BRIGHT +
            f"{host}: done" +
            colorama.Style.RESET_ALL
        )

if __name__ == "__main__":
    main()
