import sys
import os
import importlib.util

# Get the directory where passenger_wsgi.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# DIAGNOSTIC: Log passenger_wsgi.py loading
print("[DIAGNOSTIC] passenger_wsgi.py loading started")

# Explicitly load app.py by file path (not the app package)
app_path = os.path.join(current_dir, 'app.py')
print(f"[DIAGNOSTIC] Loading app.py from: {app_path}")
spec = importlib.util.spec_from_file_location("app_module", app_path)
app_module = importlib.util.module_from_spec(spec)
print("[DIAGNOSTIC] About to execute app_module")
spec.loader.exec_module(app_module)
print("[DIAGNOSTIC] app_module executed, getting app object")
application = app_module.app
print(f"[DIAGNOSTIC] Application object retrieved: {application}")
print(f"[DIAGNOSTIC] Application has url_map: {hasattr(application, 'url_map')}")
if hasattr(application, 'url_map'):
    print(f"[DIAGNOSTIC] Number of routes in url_map: {len(list(application.url_map.iter_rules()))}")
print("[DIAGNOSTIC] passenger_wsgi.py loading completed")

if __name__ == "__main__":
    application.run()
