import argparse
import argcomplete 
import os
import sys
import click
import configparser
import shutil
import colorama
from git import Repo
from git.exc import GitCommandError
from github import Github
from pathlib import Path


home_dir = Path(os.path.expanduser('~'))
dot_config_dir = Path(os.path.join(home_dir, '.config'))
config_dir = Path(os.path.join(dot_config_dir, 'xdfm'))

colorama.init()

def read_config(configfile):
    global config, dots, pat_token
    if not config_dir.exists():
        config_dir.mkdir(parents=True)

    if not configfile.exists():
        with open(configfile, 'w') as cf:
            cf.write("[Dots]\n\n[GitHub]\npat=undefined\n\n[Settings]\nPAT_Alert=enabled")


    config = configparser.ConfigParser()
    config.read(configfile)
    
    pat_token = config['GitHub']['pat']
    dots = []

    for key in config['Dots']:
        folder = config['Dots'][key]
        folder = os.path.expanduser(folder)
        dots.append(folder)



def save_config(configfile):
    with open(configfile, 'w') as cf:
        config.write(cf)

def patalert(configfile):
    read_config(configfile)
    if config['Settings']['PAT_Alert'] == "enabled":
        print(f"{colorama.Fore.RED}Error: GitHub Personal Access Token (PAT) isn't set in the config file! Please set the PAT using the `{colorama.Fore.GREEN}xdfm github pat YOUR_PAT{colorama.Fore.RED}` command")
        sys.exit(1)

def add_config(config_file, setting, key, value):
    if key in config[setting]:
        print(f"{colorama.Fore.RED}Error: `{key}` already exists in the config file: '{key}={config[setting][key]}'")
        return
    config[setting][key] = value
    save_config(config_file)

def edit_config(config_file, setting, key, newvalue):
    if key not in config[setting]:
        print(f"{colorama.Fore.RED}Error: '{key}' doesn't exist in the config file!")
        return
    config[setting][key] = newvalue
    save_config(config_file)
    

def remove_config(config_file, setting, key):
    read_config(config_file)

    if config.has_option(setting, key):
        # Eğer key'i bulduysak, onu sil
        config.remove_option(setting, key)
        print(f"{colorama.Fore.YELLOW}Removed {key} from {setting} section.")
        save_config(config_file)
    else:
        # Eğer key'i bulamazsak, value kontrolü yapalım
        found = False
        for section_key in config[setting]:
            folder_path = config[setting][section_key]
            expanded_folder = os.path.expanduser(folder_path)  # Ev dizini (~) çözülür
            if folder_path == key:
                config.remove_option(setting, section_key)
                save_config(config_file)
                print(f"{colorama.Fore.YELLOW}Removed folder path {folder_path} from {setting} section.")
                found = True
                break

        if not found:
            # Eğer hiçbir şey bulamazsak, kırmızı renkte hata mesajı
            print(f"{colorama.Fore.RED}{key} not found in {setting} section or no matching folder path found.")


def create_dotfiles(config_file, path, name):
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if 'Dots' not in config:
        print(f"{colorama.Fore.YELLOW}Error: No 'Dots' section found in the config file.")
        return

    dots_folders = []
    for key in config['Dots']:
        folder = config['Dots'][key]
        expanded_folder = os.path.expanduser(folder)  # Ev dizini (~) çözülür
        dots_folders.append(expanded_folder)

    # Hedef dizinde yeni bir klasör oluştur
    target_dir = os.path.join(os.path.expanduser(path), name)
    if os.path.exists(target_dir):
        print(f"{colorama.Fore.RED}Error: dotfiles folder already exists in {path}")
        return
    os.makedirs(target_dir)

    # Her bir klasörü kopyala
    for folder in dots_folders:
        if os.path.exists(folder):  # Klasör var mı diye kontrol et
            target_folder = os.path.join(target_dir, os.path.basename(folder))
            try:
                shutil.copytree(folder, target_folder)
                print(f"{colorama.Fore.YELLOW}Copied {folder} to {target_folder}")
            except Exception as e:
                print(f"{colorama.Fore.RED}Error copying {folder}: {e}")
        else:
            print(f"Folder {folder} does not exist.")


def recreate_dotfiles(config_file, path, name):
    """Mevcut dotfiles klasörünü siler ve ardından yeniden oluşturur."""
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if 'Dots' not in config:
        print(f"{colorama.Fore.YELLOW}Error: No 'Dots' section found in the config file.")
        return

    dots_folders = []
    for key in config['Dots']:
        folder = config['Dots'][key]
        expanded_folder = os.path.expanduser(folder)  # Ev dizini (~) çözülür
        dots_folders.append(expanded_folder)

    # Hedef dizinde yeni bir klasör oluştur
    target_dir = os.path.join(os.path.expanduser(path), name)
    
    # Eğer hedef dizin varsa, içeriğini sil
    if os.path.exists(target_dir):
        print(f"{colorama.Fore.YELLOW}Removing existing 'dotfiles' directory...")
        try:
            shutil.rmtree(target_dir)  # Mevcut dotfiles klasörünü sil
        except Exception as e:
            print(f"{colorama.Fore.RED}Error removing existing 'dotfiles' directory: {e}")
            return
    else:
        print(f"{colorama.Fore.YELLOW}No existing 'dotfiles' directory found, creating a new one.")
    
    # 'create_dotfiles' fonksiyonunu çağırarak yeniden dotfiles oluştur
    create_dotfiles(config_file, path)

def add_remote_if_not_exists(repo, remote_name, remote_url):
    try:
        # Mevcut uzak bağlantıları kontrol et
        remotes = [remote.name for remote in repo.remotes]
        if remote_name not in remotes:
            # Eğer 'origin' yoksa, ekle
            repo.create_remote(remote_name, remote_url)
    except GitCommandError as e:
        print(f"Error adding remote: {e}")

def create_repo(repo_name, config_file, path, commit):
    try:
        # Yerel repo dizini kontrol ediliyor
        local_repo_path = Path(os.path.join(home_dir, 'dotfiles'))
        if not local_repo_path.exists():
            print(f"{colorama.Fore.RED}ERROR: dotfiles does not exist. Please create it using the {colorama.Fore.GREEN}`xdfm create`{colorama.Fore.RED} command")
            return
        
        # Yerel repo başlatılıyor
        local_repo = Repo.init(local_repo_path)

        # GitHub bağlantısı kuruluyor
        g = Github(pat_token)
        user = g.get_user()
        
        # Repo var mı kontrol et
        try:
            repo = user.get_repo(repo_name)
            print(f"{colorama.Fore.YELLOW}Repository '{repo_name}' already exists on GitHub.")
            repo_url = repo.clone_url
        except:
            print(f"{colorama.Fore.YELLOW}Creating repository '{repo_name}' on GitHub.")
            repo = user.create_repo(repo_name, private=True)
            repo_url = repo.clone_url
        
        # Origin remote bağlantısını ekleyelim (varsa eklemeyelim)
        try:
            add_remote_if_not_exists(local_repo, 'origin', repo_url)
        except Exception as e:
            print(f"{colorama.Fore.RED}ERROR: Failed to add remote repository. Details: {str(e)}")
            return

        # Değişiklikleri ekleyip commit yapalım
        try:
            print(f"{colorama.Fore.YELLOW}Adding and committing changes...")
            local_repo.index.add('*')  # Tüm dosyaları ekleyelim
            local_repo.index.commit(commit)  # Commit işlemi yapalım
        except Exception as e:
            print(f"{colorama.Fore.RED}ERROR: Failed to commit changes. Details: {str(e)}")
            return

        # Değişiklikleri GitHub'a push edelim
        try:
            print(f"{colorama.Fore.YELLOW}Pushing changes to GitHub...")
            local_repo.remotes.origin.push('main')  # main branch'ini push edelim
        except Exception as e:
            print(f"{colorama.Fore.RED}ERROR: Failed to push changes to GitHub. Details: {str(e)}")
            return

        print(f"{colorama.Fore.GREEN}Repository '{repo_name}' created and pushed to GitHub!")
        print(f"{colorama.Fore.GREEN}Repository URL: {repo_url}")

    except Exception as e:
        print(f"{colorama.Fore.RED}ERROR: An unexpected error occurred. Details: {str(e)}")
