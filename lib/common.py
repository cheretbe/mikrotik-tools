import sys
import os
import datetime
import pathlib
import paramiko
import humanfriendly.prompts
if sys.platform == 'win32':
    import ctypes.wintypes

class SSHCommandStatusError(Exception):
    """Custom exception class for SSH command returning non-zero exit status"""


def ssh_connect(ssh_host, credentials):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=ssh_host, username=credentials["username"], password=credentials["password"]
    )
    return ssh_client


def exec_ssh_command(ssh_client, cmd, echo=True):
    result = []
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    stdin.close()
    while True:
        line = stdout.readline()
        if not line:
            break
        result += [line.rstrip()]
        if echo:
            print("  " + line, end="")
    if stdout.channel.recv_exit_status() != 0:
        raise SSHCommandStatusError(
            "SSH command returned non-zero exit status " +
            str(stdout.channel.recv_exit_status())
        )
    return result

def unique_file(file_names, template, extension):
    c_date = datetime.datetime.now().strftime("%Y-%m-%d")
    file_counter = 0
    while True:
        file_name = template.format(c_date) + "_" + str(file_counter) + extension
        if file_name not in file_names:
            break
        file_counter += 1
    return file_name

def get_backup_file_names(ssh_client):
    file_names = []
    for line in exec_ssh_command(ssh_client, "/file print terse", echo=False):
        if line.strip():
            file_names += [line.strip().split(" ")[1].split("=")[1]]
    # file_names += ["flash"]
    file_template="flash/{}" if "flash" in file_names else "{}"

    return [
        unique_file(file_names, file_template, ".backup"),
        unique_file(file_names, file_template, ".rsc")
    ]

def get_documents_path():
    if sys.platform == 'win32':
        CSIDL_PERSONAL = 5      # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return(buf.value)
    else:
        return os.path.expanduser('~/Documents')

def get_config_file_path():
    if sys.platform == 'win32':
        config_dir = os.path.expandvars(r"%APPDATA%\mikrotik-tools")
    else:
        config_dir = os.path.expanduser("~/.config/mikrotik-tools")
    os.makedirs(config_dir, exist_ok=True)

    return str(pathlib.Path(config_dir) / "settings.json")

def select_host(recent_hosts):
    selection = "Enter host name"
    if len(recent_hosts) > 0:
        selection = humanfriendly.prompts.prompt_for_choice(
            ["Enter host name"] + recent_hosts + ["Exit"],
            default="Enter host name"
        )
    if selection == "Exit":
        sys.exit("Cancelled by user")
    if selection == "Enter host name":
        selection = humanfriendly.prompts.prompt_for_input("Enter host name: ")
        if not selection:
            sys.exit("ERROR: no host name has been supplied")
    return selection
