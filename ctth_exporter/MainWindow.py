from nwcsafExporter import CtthNwcsafExporter
from tkinter import Label, Entry, StringVar, IntVar, Tk, messagebox
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from threading import Thread

import pandas as pd
import datetime
import time
import os
import re


# Format of the NWCSAF file in order to check if the file already exitsts using Regular Expresions
nwcsaf_format = r"^S_NWC_CTTH_MSG4_MSG-N-VISIR_\d{8}T\d{6}Z.nc$"

def check_files(path):
    """
    Returns files in directory in a list
    """
    files_in_dir = []
    for file in os.listdir(path):
        files_in_dir.append(file)
    
    return set(files_in_dir)


def init_file(path):
    """
    Initialize log file in order to be made in a csv format
    """
    with open(path, "w") as log:
        log.write("INPUT, DATE, TIME\n")


def write_in_file(filename_input, output):
    """
    Write in log file a report of exported nwcsaf files
    """
    with open(f"{output}/log.csv", "a") as log:
        date_time = datetime.datetime.now()
        format_date = date_time.strftime("%x, %X")
        msg = f"{filename_input}, {format_date}"
        print(msg)
        log.write(msg + "\n")


def checkTimerVal():
    if int(Minutes.get()) <= 0:
        print("INVALID VALUE: Value should be larger than 0 (sec)")
        messagebox.showinfo("INVALID VALUE", "Value should be larger than 0 (sec)")
        return False
    else:
        return True


def checkPaths():
    if str(Input_path.get()) == "" or str(Output_path.get()) == "":
        print("INVALID PATH: Check if you have entered a valid Input/Output Path")
        messagebox.showinfo("INVALID PATH", "Check if you have entered a valid Input/Output Path")
        return False
    else:
        return True


def wrongCoords():
    print("CRITICAL ERROR: Coordinates are not valid\nRestart the app")
    messagebox.showinfo("CRITICAL ERROR",  "Coordinates are not valid\nRestart the app")

# ------------------------------ Exporter ------------------------------------- #
def exporter(input, output):
    Image = CtthNwcsafExporter(input)
    clouds, selected_channels = Image.load_image()
    y_pixels, x_pixels = Image.get_resolution(clouds, selected_channels)
    data = Image.data_dict(clouds, y_pixels, x_pixels, selected_channels)
    
    if (float(lat1Entry.get()) != float(lat2Entry.get())) and (float(lon1Entry.get()) != float(lon2Entry.get())):
        lat1 = float(lat1Entry.get())
        lat2 = float(lat2Entry.get())
        lon1 = float(lon1Entry.get())
        lon2 = float(lon2Entry.get())

        data = Image.slice_data(data, lon1, lon2, lat1, lat2)
    
    Image.export_data(clouds, data, selected_channels, output)
    df = pd.DataFrame(data)


# ------------------------------ Main Function ----------------------------------#
def main(input, output, n, time_format):
    
    # Check if file already exists
    if not isinstance(input, str) :
        input = input.get()
    
    if not isinstance(output, str):
        output = output.get()

    if not isinstance(n, int):
        n = n.get()

    if not os.path.exists(f"{output}/log.csv"):
        init_file(f"{output}/log.csv")
    
    files = check_files(input)
    df = pd.read_csv(f'{output}/log.csv')

    # Check every file every n seconds, check if there is already exported. If 
    # not, then export its data with CtthnwcsafExporter and write it in log file
    for file in files:
        if re.match(nwcsaf_format, file):
            try:
                if not df['INPUT'].str.contains(file).any():
                    data_folder = Path(input)
                    file_to_open = data_folder / file
                    file_to_open = str(file_to_open).replace("\\", "/")
                    exporter(file_to_open, output)
                    write_in_file(file, output)
            except IndexError:
                wrongCoords()

    if time_format.get() == "min":
        time.sleep(n * 60)
    elif time_format.get() == "hr":
        time.sleep(n * 3600)
    else:
        time.sleep(n)


    main(input, output, n, time_format)


# ----------------------- GUI -----------------------#
def getInputFolderPath():
    folder_selected = filedialog.askdirectory()
    Input_path.set(folder_selected)


def getOutputFolderPath():
    folder_selected = filedialog.askdirectory()
    Output_path.set(folder_selected)


def doDisable():
    In.configure(state="disabled")
    Out.configure(state="disabled")
    btnSelectIn.configure(state="disabled")
    btnSelectOut.configure(state="disabled")
    timerEntry.configure(state="disabled")
    lat1Entry.configure(state="disabled")
    lat2Entry.configure(state="disabled")
    lon1Entry.configure(state="disabled")
    lon2Entry.configure(state="disabled")
    buttonExport.configure(state="disabled")

if __name__ == "__main__":
    
    # Window format
    gui = Tk()
    gui.geometry("550x450")
    gui.resizable(False, False)
    gui.title("NWCSAF Exporter")
    icon = 'nwcsaf_icon_no_background.ico'
    png = 'nwcsaf_icon_no_background.png'
    gui.iconbitmap(icon)

    img = Image.open(png)
    photo = ImageTk.PhotoImage(img)
    panel = Label(gui, image=photo).grid(columnspan=4, sticky='we')
    creator = Label(gui, text="Created by Angelos Motsios, aggelosmots@gmail.com").grid(row=10, column=0, columnspan=2, sticky='sw')

    gui.grid_columnconfigure(0, weight=1)
    gui.grid_columnconfigure(1, weight=1)
    gui.grid_columnconfigure(2, weight=1)

    # Tk variables
    Input_path = StringVar()
    Output_path = StringVar()
    Minutes = IntVar()
    Latitude1 = IntVar()
    Latitude2 = IntVar()
    Longtitude1 = IntVar()
    Longtitude2 = IntVar()
    TimerFormatEntry = StringVar()

    # Input row customization
    a = Label(gui ,text="Input Folder")
    a.grid(row=1, column = 0, sticky="w")
    In = Entry(gui, textvariable=Input_path)
    In.grid(row=2, column=0, sticky='we', columnspan=4)
    btnSelectIn = ttk.Button(gui, text="Browse Folder", command=getInputFolderPath)
    btnSelectIn.grid(row=2, column=3, sticky="E")

    # Output row customization
    b = Label(gui ,text="Ouput Folder")
    b.grid(row=3,column = 0, sticky="W")
    Out = Entry(gui,textvariable=Output_path)
    Out.grid(row=4,column=0,  sticky='we', columnspan=4)
    btnSelectOut = ttk.Button(gui, text="Browse Folder",command=getOutputFolderPath)
    btnSelectOut.grid(row=4,column=3, sticky="E")

    # Timer Label, Entry and Combomenu
    timer = Label(gui, text="Timer")
    timer.grid(row=5)
    timerEntry = Entry(gui,textvariable=Minutes)
    timerEntry.grid(row=6)

    selectTimeFormat = ttk.Combobox(gui, textvariable=TimerFormatEntry)
    selectTimeFormat.grid(row=6, column=1, sticky='w')
    selectTimeFormat['values'] = ['sec', 'min', 'hr']
    selectTimeFormat['state'] = 'readonly'
    selectTimeFormat.set("sec")

    # Lat and Lon Inputs
    lat1 = Label(gui, text="Latitude 1")
    lat1.grid(row=5, column=2)
    lat1Entry = Entry(gui, textvariable=Latitude1)
    lat1Entry.grid(column=2, row=6)

    lon1 = Label(gui, text="Longtitude 1")
    lon1.grid(row=5, column=3)
    lon1Entry = Entry(gui, textvariable=Longtitude1)
    lon1Entry.grid(column=3, row=6)

    lat2 = Label(gui, text="Latitude 2")
    lat2.grid(row=7, column=2)
    lat2Entry = Entry(gui, textvariable=Latitude2)
    lat2Entry.grid(column=2, row=8)

    lon2 = Label(gui, text="Longtitude 2")
    lon2.grid(row=7, column=3)
    lon2Entry = Entry(gui, textvariable=Longtitude2)
    lon2Entry.grid(column=3, row=8)

    coordNote = Label(gui, text = "Coordinates System Decimal Degrees")
    coordNote.grid(row=9, column=2, columnspan=2, sticky='n')

    # Thread Creation
    thread = Thread(target=main, args=[Input_path, Output_path, Minutes, TimerFormatEntry])
    thread.daemon = True

    # Execution button customization
    buttonExport = ttk.Button(gui, text="Export", command= lambda: checkPaths() and (checkTimerVal() and (doDisable() or thread.start())))
    buttonExport.grid(row=8, column=0, sticky="we", padx=16, columnspan=2)

    gui.mainloop()