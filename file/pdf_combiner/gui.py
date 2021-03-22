import os
import sys
from tkinter import *
from tkinter import filedialog
from PyPDF2 import PdfFileMerger

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def open_pdf():
    root.pdfs = filedialog.askopenfilenames(
        initialdir = "/",
        title = "Select file",
        filetypes = (("pdf files","*.pdf"),
        ("all files","*.*")))
    pdf_string = ""
    for pdf in root.pdfs:
        pdf_string += pdf + "\n"
    var.set(pdf_string)

    #print(root.pdfs)

def save_pdf():
    if not root.pdfs:
        print("Empty list")
    else:
        root.filename = filedialog.asksaveasfilename(
            initialdir = "/",
            title = "Select file",
            filetypes = (("pdf files","*.pdf"),
            ("all files","*.*")))
        if root.filename:
            combine_pdf()
            # write merger object to output pdf file
            with open(root.filename, 'wb') as fout:
                merger.write(fout)
            #print(root.filename)

def combine_pdf():
    # combine pdf files in list
    for pdf in root.pdfs:
        merger.append(open(pdf, 'rb'))

root = Tk()
root.title("PDF Combiner")
#root.iconbitmap(resource_path("pdf.ico"))
root.minsize(750,500)
root.geometry("750x500")
# initialize and assign PdfFileMerger object
merger = PdfFileMerger(strict=False)

#img = PhotoImage(file=resource_path("logo.png"))
#panel = Label(root, image = img)
#panel.pack()

var = StringVar()
pdf_text = Label(root, textvariable = var)

open_button = Button(root, text = "Open PDF", command = open_pdf, height = 1, width = 15)
save_button = Button(root, text = "Combine", command = save_pdf, height = 1, width = 15)

open_button.place(x = 250, y = 250)
save_button.place(x = 400, y = 250)

pdf_text.place(x = 250, y = 300)

root.mainloop()