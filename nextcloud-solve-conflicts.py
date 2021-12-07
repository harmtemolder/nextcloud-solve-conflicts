#!/usr/bin/env python

from datetime import datetime
import difflib
from pathlib import Path, PurePath
import subprocess
import termios

from colorama import init, Fore, Back
import inquirer

DEFAULT_ROOT = '~/Notes/'
TRASH = '.Trash-1000'


def ensure(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def main():
    # colorama.init
    init()

    # Get git's merge tool so it may be used for conflicts
    merge_tool = get_merge_tool()

    try:
        rootdir = Path(
            inquirer.shortcuts.path(
                message='For what path do you want to solve sync conflicts?',
                default=DEFAULT_ROOT,
                path_type='directory',
                exists=True,
                normalize_to_absolute_path=True
            )
        )
    except termios.error as e:
        rootdir = Path(DEFAULT_ROOT)

    rootdir = rootdir.expanduser()
    trashdir = rootdir / TRASH

    conflict_strings = {
        'Syncthing': '.sync-conflict-',
        'Nextcloud': ' (conflicted copy '
    }

    for conflict_source, conflict_string in conflict_strings.items():
        print(
            '\n[!] Solving {} conflicts in `{}`'.format(
                conflict_source,
                rootdir
            )
        )

        conflicts = rootdir.glob('**/*{}*'.format(conflict_string))

        for conflict in conflicts:
            # Skip items from trash
            if conflict.is_relative_to(trashdir):
                continue

            original = (conflict.parent / Path(
                conflict.stem[:conflict.stem.find(conflict_string)]
                + conflict.suffix
            ))

            if not original.exists():
                conflict.rename(original)
                continue

            conflict_relative = PurePath(conflict).relative_to(rootdir)
            original_relative = PurePath(original).relative_to(rootdir)

            conflict_mtime = datetime.fromtimestamp(conflict.stat().st_mtime)
            original_mtime = datetime.fromtimestamp(original.stat().st_mtime)

            conflict_choice = '{}[{}] {}'.format(
                Fore.RED,
                conflict_mtime.isoformat(timespec='seconds'),
                conflict_relative,
            )
            original_choice = '{}[{}] {}'.format(
                Fore.GREEN,
                original_mtime.isoformat(timespec='seconds'),
                original_relative,
            )

            choices = [conflict_choice, original_choice, 'both', 'quit']

            # Print out the actual differences for plain text files
            if conflict.suffix in ['.txt', '.md', '.json']:
                with conflict.open(mode='r') as conflict_open:
                    with original.open(mode='r') as original_open:
                        diffs = list(
                            difflib.unified_diff(
                                conflict_open.readlines(),
                                original_open.readlines(),
                                str(conflict_relative),
                                str(original_relative),
                            )
                        )
                for diff in diffs:
                    if diff[0:4] == '--- ':
                        print(
                            Back.RED + Fore.WHITE + diff + Back.RESET + Fore.RESET,
                            end=''
                        )
                    elif diff[0:4] == '+++ ':
                        print(
                            Back.GREEN + Fore.WHITE + diff + Back.RESET + Fore.RESET,
                            end=''
                        )
                    elif diff[0:3] == '@@ ':
                        print(Back.RESET + Fore.RESET + diff, end='')
                    elif diff[0] == '-':
                        print(Fore.RED + diff + Fore.RESET, end='')
                    elif diff[0] == '+':
                        print(Fore.GREEN + diff + Fore.RESET, end='')
                print(Fore.RESET + '\n')

                # And add an option to use the merge tool selected for git
                if merge_tool:
                    choices.insert(2, merge_tool)

            keep = inquirer.list_input(
                message='Which file(s) do you want to keep?',
                choices=choices,
                default=original_choice,
                carousel=True
            )

            if keep == conflict_choice:
                original.rename(ensure(trashdir / original_relative))
                conflict.rename(ensure(original))
                print(
                    Fore.BLUE + '[!] Kept local file, moved server file to {}\n'.format(
                        trashdir
                    )
                )
            elif keep == original_choice:
                conflict.rename(
                    ensure(trashdir / conflict_relative.parent / conflict.name)
                )
                print(
                    Fore.BLUE + '[!] Kept server file, moved local file to {}\n'.format(
                        trashdir
                    )
                )
            elif keep == 'quit':
                break
            elif keep == merge_tool:
                subprocess.run([merge_tool, original, conflict])


def get_merge_tool():
    try:
        git_config_merge_tool = subprocess.run(
            ['git', 'config', 'merge.tool'],
            capture_output=True
        )
        return git_config_merge_tool.stdout.decode().strip()
    except:
        return None


if __name__ == '__main__':
    main()
