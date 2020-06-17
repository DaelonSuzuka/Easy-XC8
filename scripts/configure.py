import yaml
import json
from pathlib import Path
from PyInquirer import prompt, print_json, Separator


processors = [ 
    '18F24K42 - 20 pins, 1K RAM, 16K ROM',
    '18F25K42 - 20 pins, 2K RAM, 32K ROM',
    '18F26K42 - 20 pins, 4K RAM, 64K ROM',
    '18F27K42 - 20 pins, 8K RAM, 128K ROM',
    Separator(),
    '18F45K42 - 40 pins, 2K RAM, 32K ROM',
    '18F46K42 - 40 pins, 4K RAM, 64K ROM',
    '18F47K42 - 40 pins, 8K RAM, 128K ROM',
    Separator(),
    '18F55K42 - 48 pins, 2K RAM, 32K ROM',
    '18F56K42 - 48 pins, 4K RAM, 64K ROM',
    '18F57K42 - 48 pins, 8K RAM, 128K ROM',
]


programmers = json.loads(open(Path(Path(__file__).parent, "upload.json")).read())
programmer_list = [p for p in programmers.keys() if p != 'default']


def validate_name(answer):
    if len(answer) == 0:
        return "Project name can't be empty"
    if " " in answer:
        return "Project name can't contain spaces"
    return True


new_config_file_questions = [
    {
        'type': 'input',
        'name': 'name',
        'message': 'Project name:',
        'validate': validate_name,
    },
    {
        'type': 'list',
        'name': 'processor',
        'message': 'PIC:',
        'choices': processors,
        'filter': lambda answer: answer.split(' ')[0],
    },
    {
        'type': 'list',
        'name': 'programmer',
        'message': 'Programmer:',
        'choices': programmer_list,
    },
]

def project_config_wizard():
    file_path = Path("project.yaml")

    if file_path.exists():
        print("A project configuration file already exists.")
    else:
        print("No project configuration found, creating a new one:")
        config = prompt(new_config_file_questions)
        
        # if the user hits ctrl+c to cancel, prompt() returns an empty dict
        if not config:
            return

        # add other elements that aren't worth asking the user about
        config['src_dir'] = 'src'
        config['build_dir'] = 'build'
        config['obj_dir'] = 'obj'
        config['defines'] = ['DEVELOPMENT']
        config['linker_flags'] = []

        # write the config to file
        with open(file_path, 'w') as f:
            f.write(yaml.dump(config, sort_keys=False))

if __name__ == "__main__":

    project_config_wizard()
