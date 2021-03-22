from PyPDF2 import PdfFileMerger
from functions import validPDF

# declare and initialize empty variables
pdfs = []
file = ''

while(True):
    file = input('Enter PDF name (0 to finish):')
    if (file == '0'):
        break
    if (validPDF(file)):
        pdfs.append(file)
    else:
        print('ERROR - File not found')
        continue

# initialize and assign PdfFileMerger object
merger = PdfFileMerger()

# combine pdf files in list
for pdf in pdfs:
    merger.append(open(pdf, 'rb'))

# write merger object to output pdf file
with open('out.pdf', 'wb') as fout:
    merger.write(fout)
