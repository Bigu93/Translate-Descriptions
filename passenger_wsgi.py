import sys
import os
import importlib.util

current_dir = os.path.dirname(os.path.abspath(__file__))

app_path = os.path.join(current_dir, 'app.py')
spec = importlib.util.spec_from_file_location("app_module", app_path)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
application = app_module.app

if __name__ == "__main__":
    application.run()
