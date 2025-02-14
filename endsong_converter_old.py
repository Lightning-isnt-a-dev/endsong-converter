from os import listdir, mkdir, replace, system, name
from os.path import exists, splitext
from json import load, dump
from datetime import datetime, timedelta
from tkinter.filedialog import askdirectory


def cls() -> None:
    if name == "nt":
        system("cls")
        return
    
    system("clear")
    return


def GetDir() -> str:
    DIR = ""
    print("Please select the directory of your streaming history files.\n")

    while True:
        DIR = askdirectory()

        if DIR != "":
            return DIR
        
        print("Bad directory. Please try again.")
        continue


def GetFileList(DIR: str) -> list: 
    print("Getting file list...")
    files = []

    for file in listdir(DIR):
        if splitext(file)[1] == ".json" and "Audio" in file:
            AUDIOIDX = file.find("Audio_")+6
            date = file[AUDIOIDX:AUDIOIDX+4]

            files.append((file, date))

    if files == []:
        cls()
        print("You have selected a bad directory with no streaming history files. Please try again.\n")
        Main()
        
    files.sort(key=lambda x: x[1])

    print("Got list of files!\n")
    return files


def MakeConverionDir(DIR: str) -> None:
    print("Checking for conversion directory...")
    CONVERSIONDIR = f"{DIR}/Converted"

    if not exists(CONVERSIONDIR):
        print("Made conversion directory!\n")
        mkdir(CONVERSIONDIR)
    else:
        print("Conversion directory already exists!\n")
    
    return CONVERSIONDIR


def RenameFile(CONVERSIONDIR: str, FILENAME: str, PREVIOUSFILENAME: str) -> None:
    replace(f"{CONVERSIONDIR}\\{PREVIOUSFILENAME}.json", f"{CONVERSIONDIR}\\{FILENAME.replace(":", "_")}.json")


def Convert(FILELIST: list, DIR: str, CONVERSIONDIR: str, NAMEBYLISTENDATE: bool) -> None:
    print("\nConverting to endsong... (this might take a while)")

    future = 0
    for file, _ in FILELIST:
        if NAMEBYLISTENDATE and future != 0:
            RenameFile(CONVERSIONDIR, FILENAME, ImportDay)


        DUMPLIST = []
        ImportDay = (datetime.now() + timedelta(days=future)).strftime("%d-%m")
        future += 1

        with open(f"{DIR}/{file}", "r", encoding=("utf-8")) as HISTORY:
            with open(f"{CONVERSIONDIR}/{ImportDay}.json", "w", encoding=("utf-8")) as endsong:
                FIRSTLINE = True

                for DICT in load(HISTORY):
                    if FIRSTLINE == True:
                        FILENAME = DICT["ts"]
                        FIRSTLINE = False

                    if DICT["master_metadata_track_name"] is not None or DICT["master_metadata_album_album_name"] is not None or DICT["master_metadata_album_artist_name"] is not None:
                        F_dict = dict()
                        F_dict["datetime"] = DICT["ts"]
                        F_dict["trackName"] = DICT["master_metadata_track_name"]
                        F_dict["artistName"] = DICT["master_metadata_album_artist_name"]
                        F_dict["albumName"] = DICT["master_metadata_album_album_name"]
                        DUMPLIST.append(F_dict)

                dump(DUMPLIST, endsong, indent=4, ensure_ascii=False)

    if NAMEBYLISTENDATE:
        RenameFile(CONVERSIONDIR, FILENAME, ImportDay)
    print("Converted files!\n")


def Main() -> None:
    DIR = GetDir()
    FILELIST = GetFileList(DIR)
    CONVERSIONDIR = MakeConverionDir(DIR)

    NameByListenDate = False
    
    while True:
        q = input("Before we convert, would you like to name the file by song listen date, or the date of conversion? (s/d)\n\n:").lower()

        if q == "s":
            NameByListenDate = True
            break

        elif q == "d":
            break

        else:
            print("Your input was incorrect! Please try again.\n")

    Convert(FILELIST, DIR, CONVERSIONDIR, NameByListenDate)

    input("Done! Thank you for using this converter :) press enter to leave!")

if __name__ == "__main__":
    Main()