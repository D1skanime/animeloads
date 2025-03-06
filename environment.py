import os
import re

def is_docker():
    """
    Überprüft, ob das Skript in einer Docker-Umgebung läuft.
    :return: True, wenn das Skript in Docker läuft, sonst False.
    """
    cgroup_path = f"/proc/{os.getpid()}/cgroup"
    if not os.path.isfile(cgroup_path):
        return False
    
    with open(cgroup_path) as f:
        for line in f:
            if re.match(r"\d+:[\w=]+:/docker(-[ce]e)?/\w+", line):
                return True
    return False

if __name__ == "__main__":
    print("Teste Environment-Modul...")
    print(f"Läuft in Docker: {is_docker()}")