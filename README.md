![logo](assets/logo.png)

**xDFM (Xeyossr Dotfiles Manager)** is a CLI Dotfiles Management tool for Linux. This way, you can manage your dotfiles and share them on github with a single command. In short, our goal is to reduce 10 lines of code to 1 line.

## Installing

To install **xDFM**, simply use the following command:

```bash
sudo curl -L -o /usr/local/bin/xdfm https://raw.githubusercontent.com/xeyossr/xDFM/refs/heads/main/dist/xdfm
sudo chmod +x /usr/local/bin/xdfm
```

### Compile yourself

First you need to set up the requirements:

```bash
# Debian/Ubuntu-based distributions
sudo apt install python python-pip

# Redhat/CentOS
sudo dnf install python python-pip

# Arch
sudo pacman -S python python-pip
```

Compile with:

```bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
pyinstaller --onefile xdfm.py
```

and copy `xdfm` to path (optional):

```bash
chmod +x dist/xdfm
sudo cp dist/xdfm /usr/local/bin
```

## Usage

```
Usage: xdfm.py [OPTIONS] COMMAND [ARGS]...

  xdfm - Xeyossr Dotfiles Manager.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  add         Add a new dot folder path to the config file.
  remove      Remove an existing dot folder path from the config file.
  list        List all dot folder paths present in the config file
  edit        Edit the path of an existing dot folder in the config.
  editconfig  Edit the config file with the specified editor (default: nano)
  create      Create the dotfiles directory
  update      Update the dotfiles directory
  info        Some important information.
  github      Commands related to GitHub operations
```

## Changelog

All notable changes to this project will be documented in this file.

See the [CHANGELOG](./CHANGELOG.md) for full version history.

## License

This project is licensed under the [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.html). For more details, please see the [LICENSE file](./LICENSE).

## Contribution

If you encounter any bugs or have suggestions for new features, we encourage you to open an [issue](https://github.com/xeyossr/xDFM/issues) or submit a [pull request](https://github.com/xeyossr/xDFM/pulls). We welcome contributions from the community and appreciate any improvements to the project. Please ensure that your contributions adhere to the project's guidelines and follow best practices.
