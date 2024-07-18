import os
import subprocess


def run(args):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bat_path = os.path.join(current_dir, 'script.sh')
    result = subprocess.run([bat_path] + args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    else:
        return result.stdout


def main():
    run(["Java", "Yes"])


if __name__ == '__main__':
    main()
