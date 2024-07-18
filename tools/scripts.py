import os
import subprocess


def run(args):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bat_path = os.path.join(current_dir, 'script.sh')
    result = subprocess.run([bat_path] + args, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)


def main():
    run(["Java", "Yes"])


if __name__ == '__main__':
    main()
