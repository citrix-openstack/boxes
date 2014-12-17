import subprocess
import boxes
import os
import sys


def main():
    boxes_path = os.path.dirname(os.path.abspath(boxes.__file__))
    pdu_requirements_path = os.path.join(boxes_path, "pdu-requirements.txt")
    sys.exit(subprocess.call(["pip", "install", "-r", pdu_requirements_path]))

