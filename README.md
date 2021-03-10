:warning: Note that both `python\x64\python39._pth` and `python\x64\python39._pth`
contain custom `../packages` entry.

```batch
:: Install/upgrade additional packages
python\x64\python.exe -m pip install --upgrade -t python\packages -r requirements.txt
```

* Initial pip installation
    * download https://bootstrap.pypa.io/get-pip.py
    * run "python\x64\python.exe get-pip.py" (this will create `python\x64\Lib` and `python\x64\Scripts` directories)
    * copy `python\x64\Lib\site-packages` contents to `python\packages`
    * make sure `python\packages` contains `.gitignore` file with the following entry: `__pycache__/`
    * now pip could be run like this: `python\x64\python.exe -m pip`
    * remove `python\x64\Lib` and `python\x64\Scripts`
