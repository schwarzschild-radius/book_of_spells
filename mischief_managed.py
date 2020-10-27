import subprocess

def decrypt_blob(blob_file, private_key_file):
    command = "openssl rsautl -decrypt -inkey {}  -in {}".format(private_key_file, blob_file).split()
    out = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if out.returncode == 0:
        return out.stdout.decode().strip()
    return ""
