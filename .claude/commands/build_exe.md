# Build Standalone Executable

Build the application into a single `.exe` file using PyInstaller.

## Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Build: `pyinstaller --onefile --console --uac-admin delete_old_messages_mirth.py`
3. Output: `dist/delete_old_messages_mirth.exe`
4. Copy `.env` alongside the `.exe` before running
