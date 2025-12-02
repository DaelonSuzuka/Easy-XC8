import re


def apply_skip_rules(project, env, sources):
    skipped = []
    
    rules = [re.compile(r) for r in env.skip_rules]

    def check_skip_rules(f):
        # print(f)
        for rule in rules:
            # print(f'\t{skip}')
            if rule.search(f):
                skipped.append(f)
                # print('\tskipping')
                return True
        return False

    sources = [f for f in sources if not check_skip_rules(f)]
    with open(f'{project.build_dir}/skipped_files.txt', 'w') as out:
        out.write('\n'.join(skipped))

    return sources
