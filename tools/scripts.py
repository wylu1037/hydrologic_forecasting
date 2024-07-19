import os
import subprocess


def run(model_forecast_request):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bat_path = os.path.join(current_dir, '../app/service/script.sh')
    result = subprocess.run([bat_path] + model_forecast_request.args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    else:
        return result.stdout
