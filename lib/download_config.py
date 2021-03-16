# No shebang as this script is intended to be run via bash or batch wrapper

import sys
import colorama


colorama.init()

print(colorama.Fore.RED + 'some red text')

print(colorama.Fore.CYAN + 'cyan ' + colorama.Style.BRIGHT + 'bright ' + colorama.Style.NORMAL + 'test')
print(colorama.Fore.MAGENTA + 'magenta ' + colorama.Style.BRIGHT + 'bright ' + colorama.Style.NORMAL + 'test')

print(colorama.Style.RESET_ALL)

sys.exit(0)