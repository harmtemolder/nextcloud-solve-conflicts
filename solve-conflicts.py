#!/usr/bin/env python

from datetime import datetime
import difflib
from pathlib import Path, PurePath
import subprocess
import sys
import termios

from colorama import init, Fore, Back
import inquirer

DEFAULT_ROOT_DIR = '~/Notes/'
DEFAULT_TRASH_DIR = '.Trash-1000'


def ensure(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def main(
    default_root_dir=DEFAULT_ROOT_DIR,
    default_trash_dir=DEFAULT_TRASH_DIR
):
    # colorama.init
    init()

    # Get git's merge tool so it may be used for conflicts
    merge_tool = get_merge_tool()

    # Set the full paths to root and trash
    root_dir = get_root_dir(default_root_dir)
    trash_dir = root_dir / default_trash_dir

    conflict_strings = {
        'Syncthing': '.sync-conflict-',
        'Nextcloud': ' (conflicted copy '
    }

    for conflict_source, conflict_string in conflict_strings.items():
        print(
            '[!] Solving {} conflicts in `{}`\n'.format(
                conflict_source,
                root_dir
            )
        )

        success = solve_conflicts(
            conflict_string,
            merge_tool,
            root_dir,
            trash_dir
        )

        if not success:
            return False

    return True


def solve_conflicts(conflict_string, merge_tool, root_dir, trash_dir):
    conflicts = root_dir.glob('**/*{}*'.format(conflict_string))

    for conflict in conflicts:
        success = solve_conflict(
            conflict,
            conflict_string,
            merge_tool,
            root_dir,
            trash_dir
        )

        if not success:
            return False

    return True


def solve_conflict(conflict, conflict_string, merge_tool, root_dir, trash_dir):
    # Skip items from trash
    if conflict.is_relative_to(trash_dir):
        return True

    original = (conflict.parent / Path(
        conflict.stem[:conflict.stem.find(conflict_string)]
        + conflict.suffix
    ))

    # Automatically fix conflicts where the original is missing
    if not original.exists():
        conflict.rename(original)
        return True

    conflict_relative = PurePath(conflict).relative_to(root_dir)
    original_relative = PurePath(original).relative_to(root_dir)

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

    if conflict.suffix in ['.txt', '.md', '.json']:
        # Print out the actual differences for plain text files
        print_diffs(conflict, conflict_relative, original, original_relative)

        # And add an option to use the merge tool selected for git
        if merge_tool:
            choices.insert(2, merge_tool)

    # Up until here debugging in PyCharm works
    keep = inquirer.list_input(
        message='Which file(s) do you want to keep?',
        choices=choices,
        default=original_choice,
        carousel=True
    )

    if keep == conflict_choice:
        original.rename(ensure(trash_dir / original_relative))
        conflict.rename(ensure(original))
        print(
            Fore.BLUE + '[!] Kept local file, moved server file to `{}`\n'.format(
                trash_dir
            )
        )
    elif keep == original_choice:
        conflict.rename(
            ensure(trash_dir / conflict_relative.parent / conflict.name)
        )
        print(
            Fore.BLUE + '[!] Kept server file, moved local file to `{}`\n'.format(
                trash_dir
            )
        )
    elif keep == merge_tool:
        subprocess.run([merge_tool, original, conflict])
    elif keep == 'both':
        pass
    elif keep == 'quit':
        return False

    return True


def print_diffs(conflict, conflict_relative, original, original_relative):
    diffs = get_diffs(conflict, conflict_relative, original, original_relative)

    for diff in diffs:
        print_diff(diff)

    print(Fore.RESET + '\n')


def print_diff(diff):
    if diff[0:4] == '--- ':
        # Conflict file
        print(
            Back.RED + Fore.WHITE + diff + Back.RESET + Fore.RESET,
            end=''
        )
    elif diff[0:4] == '+++ ':
        # Original file
        print(
            Back.GREEN + Fore.WHITE + diff + Back.RESET + Fore.RESET,
            end=''
        )
    elif diff[0:3] == '@@ ':
        # Context
        print(Back.RESET + Fore.RESET + diff, end='')
    elif diff[0] == '-':
        # In conflict, not in original
        print(Fore.RED + diff + Fore.RESET, end='')
    elif diff[0] == '+':
        # In original, not in conflict
        print(Fore.GREEN + diff + Fore.RESET, end='')


def get_diffs(conflict, conflict_relative, original, original_relative):
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

    return diffs


def get_root_dir(default=DEFAULT_ROOT_DIR):
    try:
        root_dir = Path(
            inquirer.shortcuts.path(
                message='For what path do you want to solve sync conflicts?',
                default=default,
                path_type='directory',
                exists=True,
                normalize_to_absolute_path=True
            )
        )
    except termios.error as e:
        root_dir = Path(default)

    print()

    root_dir = root_dir.expanduser()

    return root_dir


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
    success = main()

    if not success:
        sys.exit(1)

    sys.exit()
