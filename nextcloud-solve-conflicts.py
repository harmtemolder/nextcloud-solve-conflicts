#!/usr/bin/env python

from datetime import datetime
from pathlib import Path, PurePath
import termios

import inquirer

def ensure(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == '__main__':
    default_rootdir = '~/Nimbus/'
    try:
        rootdir_question = inquirer.Path(
            'rootdir',
            message='For what path do you want to solve sync conflicts?',
            default=default_rootdir,
            path_type='directory',
            exists=True,
            normalize_to_absolute_path=True
        )
        rootdir = Path(inquirer.prompt([rootdir_question])['rootdir'])
    except termios.error as e:
        rootdir = Path(default_rootdir)
    trashdir = rootdir / '.Trash-1000'

    conflicts = rootdir.glob('**/* (conflicted copy *')

    for conflict in conflicts:
        original = (conflict.parent / Path(
            conflict.stem[:conflict.stem.find(" (conflicted copy ")]
            + conflict.suffix))

        if not original.exists():
            conflict.rename(original)
            continue

        conflict_relative = PurePath(conflict).relative_to(rootdir)
        original_relative = PurePath(original).relative_to(rootdir)

        conflict_mtime = datetime.fromtimestamp(conflict.stat().st_mtime)
        original_mtime = datetime.fromtimestamp(original.stat().st_mtime)

        conflict_choice = 'Local  ({}): {}'.format(
            conflict_mtime.isoformat(timespec='seconds'),
            conflict_relative,
        )
        original_choice = 'Server ({}): {}'.format(
            original_mtime.isoformat(timespec='seconds'),
            original_relative,
        )

        questions = [inquirer.List(
            'keep',
            message='Which file(s) do you want to keep?',
            choices=[conflict_choice, original_choice, 'both', 'quit']
        )]

        answers = inquirer.prompt(questions)

        if answers['keep'] == conflict_choice:
            original.rename(ensure(trashdir / original_relative))
            conflict.rename(ensure(original))
            print(' = Kept local file, moved server file to {}'.format(trashdir))
        elif answers['keep'] == original_choice:
            conflict.rename(ensure(trashdir / conflict_relative.parent / original.name))
            print(' = Kept server file, moved local file to {}'.format(trashdir))
        elif answers['keep'] == 'quit':
            break
