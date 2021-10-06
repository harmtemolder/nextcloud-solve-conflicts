# Solve Nextcloud and Syncthing conflicts

This script searches a local folder for sync conflicts caused by [Nextcloud](https://nextcloud.com/) or [Syncthing](https://syncthing.net/) and asks how to resolve each of these. In the case of plain text files (based on a `.txt` or `.md` file extension) it prints the difference.

## Credits

- Uses [`inquirer`](https://python-inquirer.readthedocs.io/en/latest/) (`conda install inquirer`) for the prompts;
- [`colorama`](https://github.com/tartley/colorama) for colored diffs;
- [`pathlib`](https://docs.python.org/3/library/pathlib.html) for file path operations;
- and [`datetime`](https://docs.python.org/3/library/datetime.html) to display file modification times in a readable format
