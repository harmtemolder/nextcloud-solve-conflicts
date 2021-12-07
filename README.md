# Solve Nextcloud and Syncthing conflicts

This script searches a local folder for sync conflicts caused by [Nextcloud](https://nextcloud.com/) or [Syncthing](https://syncthing.net/) and asks how to resolve each of these. In the case of plain text files (based on a `.txt`, `.md` or `.json` file extension) it prints the difference. If you have a merge tool set up for git, it also gives the option to use that to solve the conflict.

## Usage

- Run `pipenv install` to install all dependencies from the `Pipfile`
- Run `pipenv run python solve-conflicts.py` to solve your conflicts
- Feel free to change the defaults at the top of `solve-conflicts.py` to match your system

## Credits

- Based on [iagopinal's `nextcloud_solve_conflicts`](https://github.com/iagopinal/nextcloud_solve_conflicts)
- Uses [`pipenv`](https://github.com/pypa/pipenv#readme) for the virtual environment;
- [`inquirer`](https://python-inquirer.readthedocs.io/en/latest/) for the prompts;
- [`colorama`](https://github.com/tartley/colorama) for colored diffs;
- [`pathlib`](https://docs.python.org/3/library/pathlib.html) for file path operations;
- and [`datetime`](https://docs.python.org/3/library/datetime.html) to display file modification times in a readable format
