```bash
pyinstaller --onefile --windowed --name=PU_Inventory inventory_app.py
```

```bash
pyinstaller --noconsole --onefile --icon=PULogo.ico --name=PU_Inventory inventory_app.py
```

```bash
pyinstaller --onefile --windowed --icon=PULogo.ico --name=PU_Inventory inventory_app.py
```

```bash
pyinstaller --noconsole --onefile --icon=PULogo.ico --name=PU_Inventory inventory_app.py --exclude-module matplotlib
```
