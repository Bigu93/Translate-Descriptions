import sys
import os
import importlib.util

# Get the directory where passenger_wsgi.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Explicitly load app.py by file path (not the app package)
app_path = os.path.join(current_dir, 'app.py')
spec = importlib.util.spec_from_file_location("app_module", app_path)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
application = app_module.app

if __name__ == "__main__":
    application.run()
