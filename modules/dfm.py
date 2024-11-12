import argparse
import argcomplete 
import os
import sys
import click
import configparser
import time
import shutil
import colorama
import filecmp
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

def add_config(config_file, setting, value, key=None):
    # Eğer key verilmemişse, value'nin son klasör adını al
    if key is None:
        key = os.path.basename(os.path.normpath(value))
        
    # Eğer key zaten varsa hata mesajı ver ve fonksiyonu sonlandır
    if key in config[setting]:
        print(f"{colorama.Fore.RED}Error: `{key}` already exists in the config file: '{key}={config[setting][key]}'")
        return
    
    # Yeni key-value çifti ekle ve config'i kaydet
    config[setting][key] = value
    save_config(config_file)


def list(config_file):
    read_config(config_file)

    if 'Dots' in config:
        for key, value in config['Dots'].items():
            print(f"{colorama.Fore.YELLOW}{key}{colorama.Fore.RESET} => {colorama.Fore.GREEN}{value}{colorama.Fore.RESET}")
    else:
        print(colorama.Fore.RED + "Error: '[Dots]' section not found in the config file." + colorama.Style.RESET_ALL)

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
        dots_folders.append((key, expanded_folder))  # key'i de ekliyoruz

    # Hedef dizinde yeni bir klasör oluştur
    target_dir = os.path.join(os.path.expanduser(path), name)
    if os.path.exists(target_dir):
        print(f"{colorama.Fore.RED}Error: dotfiles folder already exists in {path}")
        return
    os.makedirs(target_dir)

    # Her bir klasörü ya da dosyayı kopyala
    for key, folder in dots_folders:
        if os.path.isdir(folder):  # Klasörse
            target_folder = os.path.join(target_dir, os.path.basename(folder))
            try:
                shutil.copytree(folder, target_folder)
                print(f"{colorama.Fore.YELLOW}Copied folder {colorama.Fore.CYAN}{folder}{colorama.Fore.YELLOW} to => {colorama.Fore.GREEN}{target_folder}{colorama.Fore.YELLOW}")
            except Exception as e:
                print(f"{colorama.Fore.RED}Error copying folder {folder}: {e}")
        elif os.path.isfile(folder):  # Dosya ise
            # Eğer key bir uzantıya sahip değilse, key adıyla bir klasör oluştur
            if not os.path.splitext(key)[1] and ' ' not in key:  # Key uzantı içermiyorsa ve boşluk yoksa
                target_folder = os.path.join(target_dir, key)  # Yeni klasör adı olarak key kullanılıyor
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)
                shutil.copy(folder, target_folder)  # Dosyayı key adıyla oluşturulan klasöre kopyala
                print(f"{colorama.Fore.YELLOW}Copied file {colorama.Fore.CYAN}{folder}{colorama.Fore.YELLOW} to => {colorama.Fore.GREEN}{target_folder}{colorama.Fore.YELLOW}")
            else:
                shutil.copy(folder, target_dir)  # Dosyayı doğrudan target_dir'e kopyala
                print(f"{colorama.Fore.YELLOW}Copied file {colorama.Fore.CYAN}{folder}{colorama.Fore.YELLOW} to => {colorama.Fore.GREEN}{target_dir}{colorama.Fore.YELLOW}")
        else:
            print(f"{colorama.Fore.RED}Error: Item {folder} does not exist.{colorama.Fore.RESET}")

def update_dotfiles(config_file, path):
    """Update the existing dotfiles folder by adding missing or updated files and folders."""
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if 'Dots' not in config:
        print(f"{colorama.Fore.YELLOW}Error: No 'Dots' section found in the config file.")
        return

    dots_folders = []
    for key in config['Dots']:
        folder = config['Dots'][key]
        expanded_folder = os.path.expanduser(folder)  # Ev dizini (~) çözülür
        dots_folders.append((key, expanded_folder))  # key ve folderi birlikte tutuyoruz

    target_dir = os.path.expanduser(path)

    # Eğer hedef dizin yoksa oluştur
    if not os.path.exists(target_dir):
        print(f"{colorama.Fore.YELLOW}Creating new dotfiles directory at {target_dir}.")
        os.makedirs(target_dir)

    # Başlangıçta işlemlerin yapılacağı bilgisini gösteriyoruz
    print(f"{colorama.Fore.CYAN}Updating dotfiles, please wait...")

    # Klasörleri ve dosyaları karşılaştır ve güncelle
    for key, folder in dots_folders:
        target_folder = os.path.join(target_dir, os.path.basename(folder))

        if os.path.isdir(folder):  # Eğer kaynak bir klasörse
            if not os.path.exists(target_folder):  # Eğer hedef klasör yoksa
                shutil.copytree(folder, target_folder)
                print(f"{colorama.Fore.YELLOW}Copied folder: {folder}")
            else:
                update_folder(folder, target_folder)
        elif os.path.isfile(folder):  # Eğer kaynak bir dosyaysa
            if not os.path.exists(target_folder) or not filecmp.cmp(folder, target_folder, shallow=False):
                shutil.copy(folder, target_folder)
                print(f"{colorama.Fore.YELLOW}Copied file: {folder}")
    
    # İşlem bitince "Updated" mesajı
    print(f"\r{colorama.Fore.GREEN}Updated.{colorama.Style.RESET_ALL}")

def update_folder(source_folder, target_folder):
    """Güncel olmayan dosyaları veya eksik dosyaları hedef klasöre kopyalar."""
    updated_files = False  # Dosyaların güncellenip güncellenmediğini takip etmek için bir bayrak

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_folder, os.path.relpath(source_file, source_folder))
            
            # Eğer hedef dosya yoksa veya güncel değilse
            if not os.path.exists(target_file) or not filecmp.cmp(source_file, target_file, shallow=False):
                os.makedirs(os.path.dirname(target_file), exist_ok=True)  # Dosya için hedef klasörü oluştur
                shutil.copy(source_file, target_file)  # Dosyayı kopyala
                updated_files = True  # Dosya güncellendi

    if updated_files:
        print(f"{colorama.Fore.YELLOW}Folder updated: {source_folder}")


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
