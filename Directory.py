import os
import shutil
from termcolor import colored

def directory_name_changer(directory_name):
    new_name = input("Enter new name for the directory: ")
    try:
        os.rename(directory_name, new_name)
        print(colored("<Directory's name has been updated successfully!>", color="green", attrs=["bold", "underline"]))
    except Exception as e:
        print(colored(f"An error has occurred: {e}", "red"))

def directory_checker(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        print(colored("<<Directory created successfully!>>", color="green", attrs=["bold", "underline"]))
    else:
        print(colored("Directory is already existing.", "yellow"))
        name_changer = input("Do you want to change its name with the current one? Type Yes or press Enter: ")
        if name_changer.strip().lower() == "yes":
            directory_name_changer(directory_name)

def directory_deleter(directory_name):
    if not os.path.exists(directory_name) or not os.path.isdir(directory_name):
        print(colored(f"Directory '{directory_name}' does not exist.", color="yellow", attrs=["bold", "underline"]))
        return

    print(colored(f"Do you want to delete {directory_name} named directory?", color='red', attrs=['underline']))
    wish = input('Type "yes" if you agree: ')
    try:
        if wish.lower() == "yes":
            shutil.rmtree(directory_name)
            print(colored("<Directory Deleted successfully!>", color="cyan", attrs=["bold", "underline"]))
    except Exception as e:
        print(colored(f"Can't delete this directory! Reason: {e}", color="red", attrs=['bold', 'underline']))

def file_creater(directory_name):
    if not os.path.exists(directory_name):
        print("Directory doesn't exist")
        return
    
    file_name = input("Enter name for the file (with extension): ")
    file_path = os.path.join(directory_name, file_name)

    if os.path.exists(file_path):
        print(colored("File already exists", color='cyan', attrs=['underline']))
        return

    try:
        open(file_path, 'w').close()
        print(colored(f"File created in {directory_name} successfully", color='green'))
    except Exception as e:
        print(colored(f"<-......Error in creating the file!.......-> Reason: {e}", color='red'))

def file_deleter(directory_name):
    if not os.path.exists(directory_name):
        print(colored("Directory doesn't exist", color='yellow'))
        return

    file_name = input("Enter name for the file (with extension): ")
    file_path = os.path.join(directory_name, file_name)

    if not os.path.exists(file_path):
        print(colored("File doesn't exist", color='cyan'))
        return

    try:
        os.remove(file_path)
        print(colored(f"File deleted successfully", color='green'))
    except Exception as e:
        print(colored(f"<-......Error in deleting the file!.......-> Reason: {e}", color='red'))


def directory_manager():
    wants = input('Type "create_d" to create or "delete_d" to delete a directory, or "create_f"/"delete_f" for files: ')
    try:
        if wants == "create_d":
            directory_name = input("Enter name for directory: ")
            directory_checker(directory_name)
        elif wants == "delete_d":
            directory_name = input("Enter name of the directory: ")
            directory_deleter(directory_name)
        elif wants == 'create_f':
            directory_name = input("Enter the directory to add file: ")
            file_creater(directory_name)
        elif wants == 'delete_f':
            directory_name = input("Enter directory to delete file from: ")
            file_deleter(directory_name)
        else:
            print(colored("Invalid option. Please type 'create_d', 'delete_d', 'create_f', or 'delete_f'.", color="red", attrs=["bold", "underline"]))
    except Exception as e:
        print(colored(f"An error occurred: {e}", color="red", attrs=["bold", "underline"]))

if __name__ == "__main__":
    while True:
        wish = input(colored('Type "Y" to continue else "N" to exit: ', color='magenta'))

        if wish.strip().lower() == 'y':
            directory_manager()
        else:
            print("Exiting.....")
            break
