# Solve Nextcloud conflicts

This script searches the local [Nextcloud](https://nextcloud.com/) folder for sync conflicts and asks how to resolve each of these. It assumes that the local file is the one renamed to `(conflicted copy)` and the server file is the one with the original filename.

## Credits

- Uses [inquirer](https://python-inquirer.readthedocs.io/en/latest/) (`conda install inquirer`) for the prompts;
- [pathlib](https://docs.python.org/3/library/pathlib.html) for file path operations;
- and [datetime](https://docs.python.org/3/library/datetime.html) to display file modification times in a readable format
