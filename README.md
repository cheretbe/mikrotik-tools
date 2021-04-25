```batch
:: Windows
subl %APPDATA%\mikrotik-tools\settings.json
```
```shell
# Linux
subl ~/.config/mikrotik-tools/settings.json
```

:warning: Note that both `lib\python\x64\python39._pth` and `lib\python\x64\python39._pth`
contain custom `../packages` entry.

```batch
:: Install/upgrade additional packages
lib\python\x64\python.exe -m pip install --upgrade -t lib\python\packages -r lib\requirements.txt
```

* Initial pip installation
    * download https://bootstrap.pypa.io/get-pip.py
    * run "lib\python\x64\python.exe get-pip.py" (this will create `lib\python\x64\Lib` and `lib\python\x64\Scripts` directories)
    * copy `lib\python\x64\Lib\site-packages` contents to `lib\python\packages`
    * make sure `lib\python\packages` contains `.gitignore` file with the following entry: `__pycache__/`
    * now pip could be run like this: `lib\python\x64\python.exe -m pip`
    * remove `lib\python\x64\Lib` and `lib\python\x64\Scripts`
