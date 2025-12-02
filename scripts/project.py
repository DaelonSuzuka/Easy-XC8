import yaml
import json
import subprocess


def get_commit_hash():
    cmd = 'git describe --always --long --dirty --tags'
    output = subprocess.check_output(cmd, shell=True)
    return output.decode().replace('\n', '').replace('-', ':')


def fix_project(proj):
    if 'build_settings' in proj:
        for key, value in proj['build_settings'].items():
            proj[key] = value
        proj.pop('build_settings')

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
    set_default('compiler', 'legacy') # legacy or clang
    set_default('skip_rules', [])

    # fix dev and release environments
    pop_list = set()

    def fix_env(env):
        def inherit(key, default=None):
            pop_list.add(key)
            if key not in env:
                if key in proj:
                    env[key] = proj[key]
                else:
                    env[key] = default
            if env[key] is None:
                env[key] = default

        inherit('processor', None)
        if env['processor'] is None:
            raise Exception('Error: must define processor in project.yaml')

        inherit('toolchain_options', [])
        inherit('defines', [])
        inherit('skip_rules', [])
        inherit('compiler', 'legacy')
        inherit('standard', 'c89')

    # make sure the environment definitions exist
    set_default('development', {})
    set_default('release', {})

    fix_env(proj['development'])
    fix_env(proj['release'])

    # remove variables aren't inside one of the environments
    for key in pop_list:
        if key in proj:
            proj.pop(key)

    return proj


def load_project():
    project = yaml.full_load(open('project.yaml').read())
    project = fix_project(project)
    project['git_hash'] = get_commit_hash()
    project['hexname'] = f'{project["build_dir"]}/{project["name"]}.hex'
    return project


if __name__ == '__main__':
    project = load_project()
    print(json.dumps(project, indent=4, sort_keys=True))
