import sys
import inspect
from meet.google_integration import GoogleIntegration

print("Verifying GoogleIntegration class...")

# Check if methods exist
methods = [m[0] for m in inspect.getmembers(GoogleIntegration, predicate=inspect.isfunction)]

if 'listar_arquivos_drive' in methods:
    print("listar_arquivos_drive: Present")
else:
    print("listar_arquivos_drive: Missing")

if 'download_arquivo_drive' in methods:
    print("download_arquivo_drive: Present")
else:
    print("download_arquivo_drive: Missing")

# Check dependencies
try:
    import googleapiclient.discovery
    print("google-api-python-client: Installed")
except ImportError:
    print("google-api-python-client: Missing")
