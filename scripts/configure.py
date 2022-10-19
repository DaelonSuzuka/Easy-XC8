import yaml
import json
from pathlib import Path
from InquirerPy import prompt
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator


processors = {
    'K42': [
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
    ],
    'Q43': [
        '18F24Q43 - 20 pins, 1K RAM, 16K ROM',
        '18F25Q43 - 20 pins, 2K RAM, 32K ROM',
        '18F26Q43 - 20 pins, 4K RAM, 64K ROM',
        '18F27Q43 - 20 pins, 8K RAM, 128K ROM',
        Separator(),
        '18F45Q43 - 40 pins, 2K RAM, 32K ROM',
        '18F46Q43 - 40 pins, 4K RAM, 64K ROM',
        '18F47Q43 - 40 pins, 8K RAM, 128K ROM',
        Separator(),
        '18F55Q43 - 48 pins, 2K RAM, 32K ROM',
        '18F56Q43 - 48 pins, 4K RAM, 64K ROM',
        '18F57Q43 - 48 pins, 8K RAM, 128K ROM',
    ],
}


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
        'name': 'processor_family',
        'message': 'Processor Family:',
        'choices': processors,
    },
    {
        'type': 'list',
        'name': 'processor',
        'message': 'Processor:',
        'choices': lambda answers: processors[answers['processor_family']],
        'filter': lambda answer: answer.split(' ')[0],
    },
    {
        'type': 'list',
        'name': 'programmer',
        'message': 'Programmer:',
        'choices': programmer_list,
    },
    {
        'type': 'checkbox',
        'name': 'options',
        'message': 'Other options:',
        'choices': [
            Separator('> core features'),
            Choice("DEVELOPMENT", name="DEVELOPMENT", enabled=True),
            Choice("LOGGING_ENABLED", name="LOGGING_ENABLED", enabled=True),
            Separator(' '),
            Separator('> shell features'),
            Choice("SHELL_ENABLED", name="SHELL_ENABLED", enabled=True),
            Choice("SHELL_HISTORY_ENABLED", name="SHELL_HISTORY_ENABLED", enabled=True),
            Separator(' '),
            Separator('> JUDI features '),
            Choice("USB_ENABLED", name="USB_ENABLED", enabled=False),
        ],
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

        # copy config into results
        # this lets us control the order
        result = {}
        result['name'] = config['name']
        result['hw_version'] = '0.0.1'
        result['sw_version'] = '0.0.1'
        result['processor'] = config['processor']
        result['dev_processor'] = config['processor']
        result['release_processors'] = [config['processor']]
        result['programmer'] = config['programmer']

        result['src_dir'] = 'src'
        result['build_dir'] = 'build'
        result['obj_dir'] = 'obj'
        result['defines'] = []
        result['linker_flags'] = []

        if 'DEVELOPMENT' in config['options']:
            result['defines'].append('DEVELOPMENT')

        if 'SHELL_ENABLED' in config['options']:
            result['defines'].append('SHELL_ENABLED')
            result['linker_flags'].append('-Pshell_cmds')

        if 'SHELL_HISTORY_ENABLED' in config['options']:
            result['defines'].append('SHELL_HISTORY_ENABLED')

        if 'USB_ENABLED' in config['options']:
            result['defines'].append('USB_ENABLED')

        if 'LOGGING_ENABLED' in config['options']:
            result['defines'].append('LOGGING_ENABLED')

        # write the config to file
        with open(file_path, 'w') as f:
            f.write(yaml.dump(result, sort_keys=False))


if __name__ == "__main__":

    project_config_wizard()
