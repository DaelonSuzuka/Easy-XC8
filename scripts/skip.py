import re

# Always excluded from firmware builds. Host unit tests are co-located as
# foo_test.c next to foo.c and compiled only by scripts/host_test.py (zig cc).
BUILTIN_SKIP_RULES = [
    r'.*_test\.c$',
]


def apply_skip_rules(project, env, sources):
    skipped = []

    project_rules = list(getattr(env, 'skip_rules', None) or [])
    rules = [re.compile(r) for r in BUILTIN_SKIP_RULES + project_rules]

    def check_skip_rules(f):
        for rule in rules:
            if rule.search(f):
                skipped.append(f)
                return True
        return False

    sources = [f for f in sources if not check_skip_rules(f)]
    with open(f'{project.build_dir}/skipped_files.txt', 'w') as out:
        out.write('\n'.join(skipped))

    return sources
