import yaml
from dotmap import DotMap
import subprocess


def get_commit_hash():
    cmd = 'git describe --always --long --dirty --tags'
    output = subprocess.check_output(cmd, shell=True)
    return output.decode().replace('\n', '').replace('-', ':')


def load_project():
    project = DotMap(yaml.full_load(open("project.yaml").read()))
    project.git_hash = get_commit_hash()
    return project