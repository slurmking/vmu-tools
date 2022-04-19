import image_gen
import os
import unicodedata

def filter_non_printable(s):
    return ''.join(c for c in s if not unicodedata.category(c).startswith('C'))

class VMS:
    """Get data from VMS file"""

    def binaryRead(self, offset, length):
        self.VMS.seek(int(offset, 16))
        return self.VMS.read(length)

    def validate(self):
        if self.iconCount > 3:
            self.invalid = True
        elif self.animationSpeed > 65535:
            self.invalid = True

    def textRead(self, text):
        text = text.decode('cp932', errors='replace')
        text = filter_non_printable(text)
        return text

    def gamesaveRead(self):
        self.description = self.textRead(self.binaryRead("10", 32))
        self.creatingApp = self.textRead(self.binaryRead("30", 16))
        self.iconCount = int.from_bytes(self.binaryRead("40", 2), "little")
        self.animationSpeed = int.from_bytes(self.binaryRead("42", 2), "little")
        self.eyecatchType = int.from_bytes(self.binaryRead("44", 2), "little")
        self.crc = int.from_bytes(self.binaryRead("46", 2), "little")
        self.dataSize = int.from_bytes(self.binaryRead("48", 4), "little")
        self.iconPalette = self.binaryRead("60", 32)
        self.iconBitmaps = self.binaryRead("80", 512 * self.iconCount)

    def icondataRead(self):
        self.monoOffset = hex(int.from_bytes(self.binaryRead("10", 4), "little"))
        self.iconOffset = int.from_bytes(self.binaryRead("14", 4), "little")
        self.title = self.binaryRead("00", 16)
        self.monoBitmap = self.binaryRead(self.monoOffset, 128)
        self.iconPalette = self.binaryRead(hex(self.iconOffset), 32)
        self.iconBitmaps = self.binaryRead(hex(self.iconOffset + 32), 512)
        self.iconCount = 1
        self.animationSpeed = 1
        self.description = "ICONDATA"

    def gameRead(self):
        self.title = self.textRead(self.binaryRead("200", 16))
        self.description = self.textRead(self.binaryRead("210", 32))
        self.iconCount = int.from_bytes(self.binaryRead("240", 2), "little")
        self.animationSpeed = int.from_bytes(self.binaryRead("242", 2), "little")
        self.dataSize = int.from_bytes(self.binaryRead("48", 4), "little")
        self.iconPalette = self.binaryRead("260", 32)
        self.iconBitmaps = self.binaryRead("280", 512 * self.iconCount)

    def iconGen(self):
        save = self.description
        if self.filetype == 2:
            save = self.title
        image_gen.animatedGen(self.iconBitmaps, self.iconPalette, self.iconCount, save,self.animationSpeed)
        if self.filetype == 1:
            ''' Keeps leading zeros from monoBitmap bytes'''
            image_gen.bnwGen((bin(int('1' + self.monoBitmap.hex(), 16))[3:]), save)

    def info(self):
        info = {"title": self.title,
                "description": self.description,
                "creatingApp": self.creatingApp,
                "IconCount": self.iconCount,
                "Animation Speed": self.animationSpeed,
                "CRC": self.crc,
                "Data Size": self.dataSize,
                "Type": self.filetype,
                "invalid": self.invalid,
                "fileSize": self.vmsFileSize,
                "vmsName": self.vmsName}
        return info

    def imageData(self):
        imageData = {"iconBitmap": self.iconBitmaps,
                     "iconPalette": self.iconPalette,
                     "IconCount": self.iconCount, }
        if self.filetype == 1:
            ''' Keeps leading zeros from monoBitmap bytes'''
            imageData["monoBitmap"] = (bin(int('1' + self.monoBitmap.hex(), 16))[3:])
        return imageData

    def __init__(self, file):
        self.VMS = open(file, 'rb')
        self.title = ''
        self.description = ''
        self.creatingApp = ''
        self.iconCount = 0
        self.animationSpeed = 0
        self.eyecatchType = 0
        self.crc = 0
        self.dataSize = 0
        self.iconPalette = []
        self.iconBitmaps = 0
        self.invalid = False
        self.vmsFileSize = os.path.getsize(file)
        self.vmsName = os.path.basename(self.VMS.name)


        ''' Check filetype '''
        ''' gamesave = 0 ICONDATA = 1 Game = 2'''
        'only way I could check not sure if there is a better method'
        if self.binaryRead("E0", 16).hex() == "00000000000000000000000000000000" or self.binaryRead("E0",16).hex() == "ffffffffffffffffffffffffffffffff":
            self.filetype = 2
            self.gameRead()
            self.validate()
        elif "ICONDATA.VMS" in file:
            self.filetype = 1
            self.icondataRead()
            self.validate()
        else:
            self.filetype = 0
            self.gamesaveRead()
            self.validate()