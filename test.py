import EVIFile as EVI
from EVIFile import EVIread

filename = '/Users/wangzhentian/Desktop/test1_TE.EVI'
fEVI = EVI.EVIFile(filename)
#fEVI.read(filename)
fEVI.shape()
#fEVI.print_header()
fEVI.show()

data, headers = EVIread(filename)