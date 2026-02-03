# ADVANCED-BOT Standalone Executable Guide

## 🎯 Overview

This guide explains how to create and use a standalone executable version of ADVANCED-BOT that runs with just **one click** on any system without requiring Python or dependency installation.

## 🚀 Creating the Standalone Executable

### Prerequisites

Before building the standalone executable, you need:
- Python 3.8 or higher installed
- pip package manager
- Internet connection (for downloading dependencies)

### Build Instructions

#### Windows

1. Open Command Prompt or PowerShell
2. Navigate to the ADVANCED-BOT directory
3. Run the build script:
```cmd
build_standalone.bat
```

The script will:
- Install PyInstaller if not already installed
- Install all required dependencies
- Download Playwright browsers
- Build the standalone executable
- Create `dist/ADVANCED-BOT.exe`

#### Linux / macOS

1. Open Terminal
2. Navigate to the ADVANCED-BOT directory
3. Run the build script:
```bash
./build_standalone.sh
```

The script will:
- Install PyInstaller if not already installed
- Install all required dependencies
- Download Playwright browsers
- Build the standalone executable
- Create `dist/ADVANCED-BOT`

### Build Time

The build process typically takes:
- **First time**: 5-10 minutes (includes downloading Playwright browsers)
- **Subsequent builds**: 2-3 minutes

## 📦 What Gets Created

After a successful build, you'll find:

```
dist/
└── ADVANCED-BOT(.exe)    # Your standalone executable (200-300 MB)
```

This single file contains:
- Python runtime
- All Python dependencies (PySide6, Playwright, etc.)
- Application code
- Required data files

## 🖥️ Running the Standalone Executable

### Windows
Simply **double-click** `dist/ADVANCED-BOT.exe`

Or from command line:
```cmd
dist\ADVANCED-BOT.exe
```

### Linux / macOS
From terminal:
```bash
./dist/ADVANCED-BOT
```

Or make it double-clickable:
1. Right-click the file
2. Properties → Permissions
3. Check "Allow executing file as program"
4. Double-click to run

## ✅ First Run

On first run, the application will:
1. Check if Playwright browsers are installed
2. Automatically download Chromium browser if needed (takes 1-2 minutes)
3. Launch the GUI interface

**Note**: After the first run, all subsequent runs will be instant!

## 📤 Distribution

You can distribute the standalone executable to other users:

1. **Share the executable**: Copy `dist/ADVANCED-BOT(.exe)` to other computers
2. **No installation needed**: Users can run it directly
3. **First-time setup**: The application will automatically download browsers on first run
4. **Cross-platform**: Build on Windows for Windows, Linux for Linux, macOS for macOS

### File Size
- Executable: ~200-300 MB
- First-run download: ~200 MB (Chromium browser)

## 🔧 Advanced Build Options

### Custom Icon (Windows)

To add a custom icon to your executable:

1. Create or obtain an `.ico` file (Windows icon format)
2. Edit `advanced_bot.spec`:
```python
exe = EXE(
    ...
    icon='your_icon.ico',  # Add this line
)
```
3. Rebuild: `pyinstaller advanced_bot.spec --clean`

### Without Console Window (Windows)

To hide the console window:

Edit `advanced_bot.spec`:
```python
exe = EXE(
    ...
    console=False,  # Change True to False
)
```

**Note**: This will hide error messages, so only do this after thorough testing.

### Reducing File Size

To reduce the executable size:

1. Remove UPX compression (if causing issues):
```python
exe = EXE(
    ...
    upx=False,  # Change True to False
)
```

2. Exclude unused modules in the spec file

## 🐛 Troubleshooting

### Build Fails

**Error: "PyInstaller not found"**
```bash
pip install pyinstaller
```

**Error: "Module not found during build"**
```bash
pip install -r requirements.txt
```

**Error: "Playwright browsers not found"**
```bash
playwright install chromium
```

### Runtime Issues

**Error: "Failed to initialize browser"**
- The application will automatically download browsers on first run
- Ensure internet connection is available
- Check antivirus is not blocking the download

**Executable won't run**
- On Linux/macOS: Ensure execute permissions: `chmod +x ADVANCED-BOT`
- Check antivirus/firewall settings
- Try running from terminal to see error messages

**Application crashes immediately**
- Run from terminal to see error messages
- Check if all dependencies are bundled correctly
- Try rebuilding with `--clean` flag

## 🔒 Security Notes

- The standalone executable contains all code and dependencies
- Source code is not easily readable (compiled Python bytecode)
- Digital signing recommended for distribution
- Antivirus may flag unknown executables - sign your build or add exception

## 🆚 Standalone vs Python Version

| Feature | Standalone | Python Version |
|---------|-----------|----------------|
| Installation | None needed | Requires Python + pip packages |
| Startup time | Fast | Fast |
| File size | 200-300 MB | ~100 KB (code only) |
| Updates | Rebuild required | `git pull` + `pip install` |
| Distribution | Single file | Multiple files |
| Best for | End users | Developers |

## 📋 Build Checklist

Before distributing:

- [ ] Test the executable on a clean machine
- [ ] Verify all features work correctly
- [ ] Test browser automation
- [ ] Check GUI rendering
- [ ] Test proxy functionality
- [ ] Verify RPA scripts work
- [ ] Test on target operating system
- [ ] Add custom icon (optional)
- [ ] Sign the executable (recommended)
- [ ] Create user documentation

## 🎓 Tips for Distribution

1. **Compress for transfer**: Use ZIP or 7-Zip to reduce download size
2. **Include README**: Add a simple README.txt with usage instructions
3. **Version numbering**: Include version in filename (e.g., `ADVANCED-BOT-v5.2.exe`)
4. **Checksums**: Provide SHA256 hash for integrity verification
5. **Release notes**: Document what's new in each version

## 🔄 Updating the Executable

When you update the code:

1. Make your changes to `advanced_bot.py`
2. Run the build script again: `build_standalone.bat` or `./build_standalone.sh`
3. Test the new executable
4. Distribute the updated version

## 📞 Support

For issues or questions about the standalone build:
1. Check this guide first
2. Review error messages in the build output
3. Open an issue on GitHub with:
   - Your operating system
   - Python version
   - Error message or description
   - Build log output

---

**Built with PyInstaller for cross-platform standalone distribution.**
