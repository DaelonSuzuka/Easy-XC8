import yaml
from dotmap import DotMap
import subprocess


def get_commit_hash():
    cmd = 'git describe --always --long --dirty --tags'
    output = subprocess.check_output(cmd, shell=True)
    return output.decode().replace('\n', '').replace('-', ':')


def fix_project(proj):
    # mandatory
    if 'name' not in proj:
        raise Exception('Error: must define name in project.yaml')

    # optional with default values
    def set_default(key, value):
        if key not in proj:
            proj[key] = value

    set_default('src_dir', 'src')
    set_default('obj_dir', 'obj')
    set_default('build_dir', 'build')

    # fix dev and release environments
    def fix_env(env):
        def inherit(key, default=None):
            if key not in env:
                if key in proj:
                    env[key] = proj[key]
                    proj.pop(key)
                else:
                    env[key] = default
            if env[key] is None:
                env[key] = default

        inherit('processor', 'NO_PROCESSOR_SELECTED')
        inherit('toolchain_options', [])
        inherit('defines', [])
        inherit('force_include', [])

    fix_env(proj['development'])
    fix_env(proj['release'])

    return proj


def load_project():
    project = yaml.full_load(open("project.yaml").read())
    project = fix_project(project)
    project['git_hash'] = get_commit_hash()
    
    return DotMap(project)


if __name__ == "__main__":
    project = load_project()
    print(project)