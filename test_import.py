import os
import sys

# Set up the path to the current project
sys.path.append(os.getcwd())

try:
    import reports_export.urls
    print("SUCCESS: reports_export.urls is importable!")
except ModuleNotFoundError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"ANOTHER ERROR: {e}")
