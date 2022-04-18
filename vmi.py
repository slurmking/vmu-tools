import unicodedata
from datetime import datetime


def filter_non_printable(s):
    return ''.join(c for c in s if not unicodedata.category(c).startswith('C'))


def vmiIsoDate(year, month, day, hour, minute, second):
    # dateString = f"{year}-{month}-{day} {hour:02d}:{minute:02d)}:{second:02d}.0"
    dateString = f'{year}-{month}-{day} {hour:02d}:{minute:02d}:{second:02d}.0'
    return dateString


def pad(string, maxLength):
    out = string.ljust(maxLength, '\x00')
    return out.encode('cp932')

def checksumGen(resourceChecksum):
    segaCsum = int.from_bytes(bytes.fromhex('53454741'), "little")
    return resourceChecksum & segaCsum

class VMI:

    def binaryRead(self, offset, length):
        self.VMI.seek(int(offset, 16))
        return self.VMI.read(length)

    def textRead(self, text):
        text = text.decode('cp932', errors='replace')
        text = filter_non_printable(text)
        return text

    def vmiRead(self):
        self.checksum = int.from_bytes(self.binaryRead("0", 4), "little")
        self.description = self.textRead(self.binaryRead("04", 32))
        self.copyright = self.textRead(self.binaryRead("24", 32))
        self.creationYear = int.from_bytes(self.binaryRead("44", 2), "little")
        self.creationMonth = int.from_bytes(self.binaryRead("46", 1), "little")
        self.creationDay = int.from_bytes(self.binaryRead("47", 1), "little")
        self.creationHour = int.from_bytes(self.binaryRead("48", 1), "little")
        self.creationMinute = int.from_bytes(self.binaryRead("49", 1), "little")
        self.creationSecond = int.from_bytes(self.binaryRead("4A", 1), "little")
        self.creationWeekday = int.from_bytes(self.binaryRead("4B", 1), "little")
        self.vmiVersion = int.from_bytes(self.binaryRead("4C", 2), "little")
        self.fileNumber = int.from_bytes(self.binaryRead("4E", 2), "little")
        self.vmsResourceName = self.textRead(self.binaryRead("50", 8))
        self.vmsFileName = self.textRead(self.binaryRead("58", 12))
        self.fileMode = self.binaryRead("64", 2).hex()
        self.fileSize = int.from_bytes(self.binaryRead("68", 4), "little")
        self.resourceChecksum = int.from_bytes(self.binaryRead("50", 4), "little")
        self.dateString = vmiIsoDate(self.creationYear, self.creationMonth, self.creationDay, self.creationHour,
                                     self.creationMinute, self.creationSecond)

    @staticmethod
    def vmiGen(info, copyright, description):
        copyright = copyright[:32]
        description = description[:32]
        if info['Type'] == 2:
            fileMode = '0010'
        else:
            fileMode = '0000'
        year = int(datetime.today().strftime('%Y'))
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        hour = int(datetime.today().strftime('%H'))
        minute = int(datetime.today().strftime('%M'))
        second = int(datetime.today().strftime('%S'))
        weekday = 0
        vmiVersion = 0
        fileNumber = 1
        vmsResouceName = info['vmsName'].replace('.VMS', '')
        vmsFileName = info['vmsName']
        unknownValue = 0
        fileSize = info['fileSize']
        checksum = int.from_bytes(bytes.fromhex(vmsResouceName.encode().hex()[0:8]), "little")

        with open(f"{vmsResouceName}.VMI", "wb", buffering=0) as file:
            file.write(checksumGen(checksum).to_bytes(4, 'little'))
            file.write(pad(description, 32))
            file.write(pad(copyright, 32))
            file.write(year.to_bytes(2, 'little'))
            file.write(month.to_bytes(1, 'little'))
            file.write(day.to_bytes(1, 'little'))
            file.write(hour.to_bytes(1, 'little'))
            file.write(minute.to_bytes(1, 'little'))
            file.write(second.to_bytes(1, 'little'))
            file.write(weekday.to_bytes(1, 'little'))
            file.write(vmiVersion.to_bytes(2, 'little'))
            file.write(fileNumber.to_bytes(2, 'little'))
            file.write(pad(vmsResouceName, 8))
            file.write(pad(vmsFileName, 12))
            file.write(bytearray.fromhex(fileMode))
            file.write(unknownValue.to_bytes(2, 'little'))
            file.write(fileSize.to_bytes(4, 'little'))

    def info(self):
        self.vmiRead()
        info = {"checksum": self.checksum,
                "description": self.description,
                "copyright": self.copyright,
                "creationYear": self.creationYear,
                "creationMonth": self.creationMonth,
                "creationDay": self.creationDay,
                "creationHour": self.creationHour,
                "creationMinute": self.creationMinute,
                "creationSecond": self.creationSecond,
                "creationWeekday": self.creationWeekday,
                "vmiVersion": self.vmiVersion,
                "fileNumber": self.fileNumber,
                "vmsResourceName": self.vmsResourceName,
                "vmsFileName": self.vmsFileName,
                "fileMode": self.fileMode,
                "fileSize": self.fileSize,
                "dateString": self.dateString}
        return info

    def __init__(self, file=None):
        if file != None:
            self.VMI = open(file, 'rb')
        self.checksum = 0
        self.description = ""
        self.copyright = ""
        self.creationYear = 0
        self.creationMonth = 0
        self.creationDay = 0
        self.creationHour = 0
        self.creationMinute = 0
        self.creationSecond = 0
        self.creationWeekday = 0
        self.vmiVersion = 0
        self.fileNumber = 0
        self.vmsResourceName = ""
        self.vmsFileName = ""
        self.fileMode = 0
        self.fileSize = 0
