


def scan_dependencies(project, files):
    deps = {f: [] for f in files}

    def strip_name(name):
        return name.split('/')[-1][:-2]

    names = {strip_name(f): f for f in files}

    for f in files:
        with open(f) as file:
            for line in file.readlines():
                if line.startswith('#include "'):
                    name = strip_name(line[len('#include "'): -2])
                    deps[f].append(name)

    checked = []

    def walk_dep_tree(file):
        if file in checked:
            return []
        checked.append(file)

        used = [strip_name(file)]
        for dep in deps[file]:
            used.append(dep)
            if dep != strip_name(file) and dep in names:
                used.extend(walk_dep_tree(names[dep]))
        return used

    used_files = walk_dep_tree('src/main.c')
    # used_files.append('ui_func_button')
    # used_files.append('ui_relay_button')
    # used_files.append('ui_submenus')
    # used_files.append('ui_tune_button')


    # fix special cases
    if 'uart' in used_files:
        used_files.append('uart1')
        used_files.append('uart2')
        used_files.append('uart3')
        used_files.append('uart4')
        used_files.append('uart5')

    if 'hash' in used_files:
        used_files.append('hash_function')

    if 'shell' in used_files:
        used_files.extend(walk_dep_tree(names['shell_builtin_commands']))
        used_files.extend(walk_dep_tree(names['all_shell_commands']))

    for f in files:
        if strip_name(f).startswith('sh_'):
            used_files.append(strip_name(f))

    # swap back to full file names
    result = [names[f] for f in set(used_files) if f in names]

    # write the results to file
    with open(f'{project.build_dir}/skipped_files.txt', 'w') as out:
        out.write('\n'.join([f for f in files if f not in result]))

    return result 