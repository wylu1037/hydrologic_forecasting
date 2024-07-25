import subprocess

if __name__ == '__main__':
    bat_path = ''
    result = subprocess.run([bat_path], capture_output=True, text=True)
