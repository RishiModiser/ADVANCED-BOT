# ⚡ Quick Start - HumanexBot Version 5.0

## 🚀 Running the Application

### Step 1 – Install Dependencies (optional)

**Windows:**
```bat
INSTALL.bat
```

**Linux/macOS:**
```bash
chmod +x INSTALL.sh && ./INSTALL.sh
```

> `RUN.bat` / `RUN.sh` now performs this setup automatically on first launch, so this step is optional.

### Step 2 – Start the Bot

**Windows:**
```bat
RUN.bat
```

**Linux/macOS:**
```bash
./RUN.sh
```

Or run directly with Python:
```bash
python humanexbot_v5.py
```

---

## 🔨 Build an Executable

To create a single portable executable:

**Windows:**
```bat
build.bat
```

**Linux/macOS:**
```bash
chmod +x build.sh && ./build.sh
```

The resulting executable will be at `dist/humanexbot_v5` (or `dist/humanexbot_v5.exe` on Windows).

> `dist/humanexbot_v5.exe` runs as a desktop app with no terminal window.

---

## 📦 Create a Windows Installer (Optional)

For a full install flow (Next/Next/Finish + shortcut creation):

1. Install Inno Setup 6: https://jrsoftware.org/isinfo.php
2. Run:

```bat
build_installer.bat
```

Installer output:
- `installer/output/HumanexBot-Setup-v5.0.exe`

---

## 🔧 Need Help?

See [README.md](README.md) for full documentation.
