#This is all the required libraries for this program
from asyncio.windows_events import NULL
from cgitb import text
from textwrap import fill
from urllib import response
from pdf2image import convert_from_path
import pytesseract
import re
import os
import sys
import tkinter
from tkinter import messagebox
from tkinter import ttk
import shutil
from tkinter.filedialog import askdirectory
from tkinter import filedialog as fd
import fitz
from turtle import width
from PIL import Image, ImageTk
import time


############################# Possbile Methods for the Back End class ########################################################
###This method will get the bate stamps as a list
#Input parameter: pdf file path
#Return: a list contains all the bate stamps retrieve from the file
def getStamps(path):
    stamps = []
    stamps = textStamps(path)
    if stamps:
        return stamps
    else:
        stamps = imageStamps(path)
    return stamps


###This method will get the bate stamps of a text pdf file
#Input parameter: pdf file path
#Return: a list contains all the bate stamps retrieve from the text pdf file
def textStamps(path):
    page_count = 0;
    doc = fitz.open(path)
    regex= " (\\d{6}) "
    result = []
    for page in doc:
        page_count = page_count+1;
        words = page.get_text().split()
        for st in words:
            if re.match(regex, ' ' + st + ' '):
                result.append(st)
    return refinedStamps(result, page_count)


###This method is a filter to find all the correct bate stamps
#Input parameter: all the possible bate stamps
#Return: a list contains the correct bate stamps
def refinedStamps(result, page_count):
    refinedStamp = []
    for string in result:
        if string[0] == '0' and string[1] == '0':
            refinedStamp.append(string)
    if page_count == 1 and len(refinedStamp) > 0:
        oneRefinedStamp = []
        oneRefinedStamp.append(refinedStamp[(len(refinedStamp)-1)])
        return oneRefinedStamp
    else:
        return refinedStamp

###This method will get the bate stamps of a image pdf file
#Input parameter: pdf file path
#Return: a list contains all the bate stamps retrieve from the file 
def imageStamps(path):
    page_count = 0;
    images = convert_from_path(path, 
                           poppler_path=r".\\env\\Scripts\\Release-22.01.0-0\\poppler-22.01.0\\Library\\bin")
    regex= " (\\d{6}) "
    result = []
    for i in range(len(images)):
        page_count = page_count+1;
        text = pytesseract.image_to_string(images[i])
        words = text.split()
        for st in words:
            if re.match(regex, ' ' + st + ' '):
                result.append(st)
    return refinedStamps(result,page_count)


###This method will format the name of the pdf copy in a specific way
#Input parameter:
         #stamps   :  a list contains all the bate stamps
         #filename :  the name of the original pdf file
#Return: formatted file name
def formatFileName(stamps, filename):
    if len(stamps) > 1 :
        name = '\\' + stamps[0]+ "-" + stamps[-1] + "_" + disc + filename
    elif len(stamps) == 1:
        name = '\\' + stamps[0]+ "_" + disc + filename
    else:
        name = '\\' + "000000" + "_" + disc + filename
    return name


###This method will perfom following tasks:
    #1: make a copy of pdf files in given a folder or pdf files selected by the user
    #2: rename all the pdf files by a given naming convention
    #3: store the renamed copies in a given folder chose by the user
#Input parameter: None
#Return: None


def writeToDirectory():
    global disc
    global inDirectory
    global outDirectory
    global dic
    global processLabel


    #prevents complete and error logs from rendering if user input is found
    inputError = start_popup()
    dic = {}
    disc = disc_var.get()
    if disc:
        disc = disc + "_"
    stamps = []
    error = False;
    if not inputError:
        if filenames_path:
            for file in filenames_path:
                try:
                    file_path = open(file)
                    stamps = getStamps(file)
                    if not stamps:
                        dic[file] = "No Bate Stamps"
                        error = True
                    filename = os.path.basename(file_path.name)
                    shutil.copyfile(file, outDirectory+formatFileName(stamps,filename))
                except:
                    dic[file] = "Wrong File Type"
                    error = True
            
            del file
        if inDirectory:
            for file in os.listdir(inDirectory):
                try:
                    stamps = getStamps(inDirectory +"\\" + file)
                    if not stamps:
                        dic[file] = "No Bate Stamps"
                        error = True
                    shutil.copyfile(inDirectory +"\\" + file, outDirectory+formatFileName(stamps, file) )
                except:
                    dic[file] = "Wrong File Type"
                    error = True
            
            del file
    print("Log: ", dic)
    if error:
        doneWithLog(dic)
    elif not inputError:
        done_popup()


### This method will popup to let user know files are being parsed
#Input parameter: Nonemy_
#Result: None
def start_popup():
    global outDirectory
    global inDirectory
    global filenames_path
    if not inDirectory and not filenames_path:
       response = messagebox.showinfo("Error Found", "Must have input directory.")
       return True;
    elif not outDirectory:
       response = messagebox.showinfo("Error Found", "Must have output directory.")
       return True;
    messagebox.showinfo("Process Started", "Process started, click ok to continue")
    return False;

def done_popup():
    response = messagebox.showinfo("Parsing Complete", "File(s) were parsed!")
    if response == "ok":
        clear_variables()
        directory_text_box.delete(1.0, tkinter.END)
        output_text_box.delete(1.0, tkinter.END)
        filesTextBox.delete(1.0, tkinter.END)
        discNum.delete(0, tkinter.END)
   
def doneWithLog(dic):
    global logPopUp
    logPopUp = tkinter.Toplevel(root)
    logPopUp.title("Completion Log")
    logPopUp.geometry("400x400");
    
    logList = tkinter.Listbox(logPopUp)
    logList.insert(1, "Log format 'Filename: Issue Encountered'")
    for num, key in enumerate(dic):
        entry = str(key) + "     " + str(dic[key])
        logList.insert(num+1, entry)
    #generates a list and scroll bar component in case list is very long
    scrollBar = tkinter.Scrollbar(logPopUp)
    scrollBar.pack(side=tkinter.RIGHT, fill = tkinter.Y)
    logButton = tkinter.Button(logPopUp, text="Close", command=lambda:closeLog())
    logButton.pack(side=tkinter.BOTTOM, padx=3, fill=tkinter.BOTH)   
    logList.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    logList.config(yscrollcommand = scrollBar.set)
    scrollBar.config(command = logList.yview)
    logFrame = tkinter.Frame(logPopUp)   
    logFrame.pack(pady=5)

#helper for doneWithLog function
def closeLog():
    logPopUp.destroy() 
    clear_variables()


############################# Possbile Methods for the UI class ########################################################
###This method will assign the input directory to a given global variable
#Input parameter: None
#Return: None
def inputDirectory():
    global inDirectory
    directory_text_box.delete("1.0", "end")
    inDirectory =  askdirectory(title = 'Select Folder')

    if inDirectory:
        directory_text_box.insert(1.0, inDirectory)


###This method will assign the output directory to a given global variable
#Input parameter: None
#Return: None
def outputDirectory():
    global outDirectory
    output_text_box.delete("1.0", "end")
    outDirectory = askdirectory(title = 'Select Folder')

    if outDirectory:
        output_text_box.insert(1.0, outDirectory)


###This method will allow the user to select the pdf files they want to rename
#Input parameter: None
#Return: None
def selectFiles():
    #return value doesn't work when using buttons so I mad filenames_path global
    global filenames_path
    filesTextBox.delete("1.0", "end")
    filetypes = (
        ('pdf files', '*.pdf'),
        ('text files', '*.txt'),
        ('All files', '*.*')
    )

    #filenames_path is a tuple containing paths of the files we selected
    filenames_path = fd.askopenfilenames(
        title='Select Files to be renamed',
        initialdir='/',
        filetypes=filetypes)
    if filenames_path:
        filesTextBox.insert(1.0, filenames_path)


### This method will clear all variables, its called after parsing
#Input parameter: None
#Return: None
def clear_variables():
    global filenames_path
    global inDirectory
    global disc
    global outDirectory
    inDirectory = ""
    outDirectory = ""
    filenames_path = ""
    disc = ""
    directory_text_box.delete(1.0, tkinter.END)
    output_text_box.delete(1.0, tkinter.END)
    filesTextBox.delete(1.0, tkinter.END)
    disc_var.set(" ")

###This method will destroy the Ui
#Input parameter: None
#Return: None
def close():
    root.destroy()

###This method will set up the Ui for the user to interact
#Input parameter: None
#Return: None
def Ui():

    # Button used to obtain input file directory
    imgBttn = tkinter.PhotoImage(file = f"assets/imgBttn.png")
    inputButton = tkinter.Button(canvas, command=inputDirectory,
                         image= imgBttn, highlightthickness=0, borderwidth=0, relief="flat")
    inputButton.place(
    x = 487, y = 244,
    width = 128,
    height = 44)

    # Button used to select output file directory
    outputButton = tkinter.Button(canvas, command=outputDirectory,
                          image= imgBttn, highlightthickness=0, borderwidth=0, relief="flat")
    outputButton.place(
    x = 487, y = 315,
    width = 128,
    height = 44)

    # Button used to select files
    selectFile = tkinter.Button(canvas, command=selectFiles,
                        image= imgBttn, highlightthickness=0, borderwidth=0, relief="flat")
    selectFile.place(
    x = 487, y = 388,
    width = 128,
    height = 44)

    # Entry used to obtain disc number from the user
    entry3_img = tkinter.PhotoImage(file = f"assets/img_textBox1.png")
    entry3_bg = canvas.create_image(347.5, 493.5,image = entry3_img)
    global discNum
    discNum = tkinter.Entry(canvas, textvariable=disc_var, bd = 0,
    bg = "#c4c4c4",
    highlightthickness = 0)
    discNum.insert(tkinter.END, '')
    discNum.place(
    x = 274.0, y = 477,
    width = 147.0,
    height = 31)

    # Button used to process the user request
    imgProcess = tkinter.PhotoImage(file = f"assets/imgProcess.png")
    processButton = tkinter.Button(canvas,command=writeToDirectory,image = imgProcess,
    borderwidth = 0,
    highlightthickness = 0,
    relief = "flat")
    processButton.place(
    x = 487, y = 481,
    width = 163,
    height = 66)





    root.mainloop()


############################################## Driver Class #############################################################
#Start and set the size of the Ui
root = tkinter.Tk()
root.title('CSULA File Parser')
root.geometry("750x750")
root.config(background='#d4dbe9')
root.iconbitmap(f'assets/fileicon.ico')

contentFrame = tkinter.Frame(root)
contentFrame.pack(padx = 5, expand=True)

canvas = tkinter.Canvas(
    contentFrame,
    bg = "#d4dbe9",
    height = 750,
    width = 750,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas.pack(fill="both", expand=True)

background_img = tkinter.PhotoImage(file = f"assets/background.png")
background = canvas.create_image(
    406.0, 364.5,
    image=background_img)

disc_var = tkinter.StringVar()

# Text box to display directory chosen
entry0_img = tkinter.PhotoImage(file = f"assets/img_textBox0.png")
entry0_bg = canvas.create_image(
    280.0, 267.5,
    image = entry0_img)
directory_text_box = tkinter.Text(canvas,bd = 0,
    bg = "#c4c4c4",
    highlightthickness = 0)

directory_text_box.place(
    x = 139.0, y = 251,
    width = 282.0,
    height = 31)
# Text box to display output directory
entry1_img = tkinter.PhotoImage(file = f"assets/img_textBox0.png")
entry1_bg = canvas.create_image(
    280.0, 338.5,
    image = entry1_img)
output_text_box = tkinter.Text(canvas, bd = 0,bg = "#c4c4c4",highlightthickness = 0)
output_text_box.place(
    x = 139.0, y = 322,
    width = 282.0,
    height = 31)

# Text box to display selected files
entry2_img = tkinter.PhotoImage(file = f"assets/img_textBox0.png")
entry2_bg = canvas.create_image(
    280.0, 409.5,
    image = entry2_img)
filesTextBox = tkinter.Text(canvas, bd = 0,
    bg = "#c4c4c4",
    highlightthickness = 0)
filesTextBox.place(
    x = 139.0, y = 393,
    width = 282.0,
    height = 31)

#Global variables use in this program
filenames_path= ""
inDirectory= ""
disc= ""
outDirectory= ""

###Method call to start the program
Ui()



