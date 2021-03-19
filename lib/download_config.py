# No shebang as this script is intended to be run via bash or batch wrapper

import os
import sys
import base64
import json
import colorama


colorama.init()

print(colorama.Fore.RED + 'some red text')

print(colorama.Fore.CYAN + 'cyan ' + colorama.Style.BRIGHT + 'bright ' + colorama.Style.NORMAL + 'test')
print(colorama.Fore.MAGENTA + 'magenta ' + colorama.Style.BRIGHT + 'bright ' + colorama.Style.NORMAL + 'test')

print(colorama.Style.RESET_ALL)

credentials = json.loads(base64.b64decode(os.environ["AO_MIKROTIK_CREDENTIALS"]).decode("utf-16"))
print(credentials)

sys.exit(0)