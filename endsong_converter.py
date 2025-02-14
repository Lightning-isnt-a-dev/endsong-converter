from os import listdir, mkdir, replace, system, name, remove
from os.path import exists, splitext
from json import load, dump
from datetime import datetime, timedelta
from tkinter.filedialog import askdirectory


def cls() -> None:
    if name == "nt":
        system("cls")
        return 
    system("clear")


def GetImportDay(FUTURE: int) -> str:
    return (datetime.now() + timedelta(days=FUTURE)).strftime("%m-%d")


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


def Convert(FILELIST: list, DIR: str, CONVERSIONDIR: str, NAMEBYLISTENDATE: bool, SONGSPERFILE: int) -> None:
    print("\nConverting to endsong... (this might take a while)")

    future = 0
    RESET = True
    for file, _ in FILELIST:
        if RESET:
            DUMPLIST = []

        with open(f"{DIR}/{file}", "r", encoding=("utf-8")) as HISTORYFILE:
            HISTORYLIST = load(HISTORYFILE)
            if RESET:
                FIRSTLINE = True
            FIRSTFILE = True
            NEWFILE = False
            BadDict = False
            previous = 0

            while True:
                if BadDict:
                    dics += 1
                
                else:
                    dics = len(DUMPLIST)

                BadDict = False

                if dics == SONGSPERFILE or FIRSTFILE or NEWFILE:
                    if NEWFILE and not FIRSTFILE and dics not in range(SONGSPERFILE-25, SONGSPERFILE+1):
                        RESET = False
                        break

                    FIRSTFILE = False

                    if dics == SONGSPERFILE or NEWFILE:
                        FIRSTLINE = True
                        dump(DUMPLIST, endsong, indent=4, ensure_ascii=False)
                        endsong.close()
                        DUMPLIST = []

                        if NAMEBYLISTENDATE:
                            RenameFile(CONVERSIONDIR, FILENAME, ImportDay)
                        future += 1

                        if NEWFILE:
                            RESET = True
                            break


                    ImportDay = GetImportDay(future)
                    endsong = open(f"{CONVERSIONDIR}/{ImportDay}.json", "w", encoding=("utf-8"))
                    previous += dics
                
                try:
                    DICT = HISTORYLIST[dics+previous]
                except IndexError:
                    NEWFILE = True
                    continue

                if DICT["master_metadata_track_name"] is None or DICT["master_metadata_album_album_name"] is None or DICT["master_metadata_album_artist_name"] is None:
                    BadDict = True
                    continue

                if FIRSTLINE:
                    FILENAME = DICT["ts"]
                    FIRSTLINE = False

                F_dict = dict()
                F_dict["datetime"] = DICT["ts"]
                F_dict["trackName"] = DICT["master_metadata_track_name"]
                F_dict["artistName"] = DICT["master_metadata_album_artist_name"]
                F_dict["albumName"] = DICT["master_metadata_album_album_name"]
                DUMPLIST.append(F_dict)

          
    endsong.close()
    remove(f"{CONVERSIONDIR}/{ImportDay}.json")
    print("Converted files!\n")


def Main() -> None:
    DIR = GetDir()
    FILELIST = GetFileList(DIR)
    CONVERSIONDIR = MakeConverionDir(DIR)

    ans = {"s": "song listen date", "d": "date of import (M-D)"}
    while True:
        q = input("Before I convert your history, would you like me to name the file by song listen date, or by the date of importing? (s/d)\n\n:").lower()

        if q == "s":
            NameByListenDate = True

        elif q == "d":
            NameByListenDate = False

        else:
            print("Your input was incorrect! Please try again.\n")
            continue
        
        print(f"Alright, I will convert by {ans[q]}.\n")
        break


    while True:
        try:
            SongsPerFile = int(input("How many songs would you like there to be per file? (1-3000)\n\n:"))

        except TypeError:
            print("Please input a number.\n")
            continue

        if SongsPerFile > 3000:
            print("Please enter a number lower than 3000.\n")
            continue

        if SongsPerFile <= 0:
            print("Please enter a number lower higher than 0.\n")
            continue
        
        print(f"There will be {SongsPerFile} songs in every file!")
        break
    Convert(FILELIST, DIR, CONVERSIONDIR, NameByListenDate, SongsPerFile)

    input("Done! Thank you for using this converter :) press enter to leave!")

if __name__ == "__main__":
    Main()