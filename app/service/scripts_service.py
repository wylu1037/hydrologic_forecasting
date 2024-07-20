import os
import subprocess

from manage import project_root_dir


class ScriptsService:

    @staticmethod
    def run(req):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bat_path = os.path.join(project_root_dir(), 'script.sh')
        result = subprocess.run([bat_path] + req.args, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        else:
            return result.stdout
