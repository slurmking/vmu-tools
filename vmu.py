import os
import unicodedata


def filter_non_printable(s):
    return ''.join(c for c in s if not unicodedata.category(c).startswith('C'))


class Vmu:
    """Get data from VMS file"""

    def binary_read(self, offset, length):
        self.VMU.seek(int(offset, 16))
        return self.VMU.read(length)

    def text_read(self, text):
        text = text.decode('cp932', errors='replace')
        text = filter_non_printable(text)
        return text

    def block_read(self, block, offset, length):
        block = self.blocks[str(block )]
        offset = int(offset, base=16)
        length = offset + length
        return block[offset:length]

    def directory_read(self, size):
        directory = {}
        for block in range(size):
            directory[str(block)] = self.block_read(self.directoryLocation - block, "0", 512)
        return directory

    def directory_parse(self, entry, offset, length):
        offset = int(offset, base=16)
        length = offset + length
        return entry[offset:length]

    def directory_entry_read(self, entry):
        directory = {"fileType": self.directory_parse(entry, "0", 1),
                     "copyProtect": self.directory_parse(entry, "1", 1),
                     "firstBlock": int.from_bytes(self.directory_parse(entry, "2", 2), "little"),
                     "fileName": self.directory_parse(entry, "4", 12),
                     "creationTime": self.directory_parse(entry, "10", 8).hex(),
                     "fileSize": int.from_bytes(self.directory_parse(entry, "18", 2), "little"),
                     "headerOffset": int.from_bytes(self.directory_parse(entry, "1a", 2), "little")}
        return directory

    def block_grab(self):
        count = 0
        for i in range(0, self.fileSize, 512):
            count += 1
            self.blocks[f"{count-1}"] = self.binary_read(hex(i), 512)

    def fat_grab(self, fat_block):
        self.fatTable = {}
        blockCount = 0
        for index in range(0, 512, 2):
            self.fatTable[f"{blockCount}"] = fat_block[index:index + 2]
            blockCount += 1
        return self.fatTable

    # def directoryGrab(self,directory,size):
    #     self.directoryTable = {}
    #     entry = 0
    #     for index in range(0,32*size*16,32):
    #         self.directoryTable[f"{entry}"] = directory[index:index+32]
    #         entry+=1
    #     return self.directoryTable

    def directory_grab(self, directory, size):
        self.directoryTable = {}
        entry = 0
        for block in directory:
            for index in range(0, 32 * size * 16, 32):
                self.directoryTable[f"{entry}"] = directory[f"{block}"][index:index + 32]
                entry += 1
        return self.directoryTable

    def vms_extract(self, filename, first_block, blocks):
        vms_file = bytearray()
        # use text read
        filename = self.text_read(filename)
        # use text read
        newFile = open(f"{filename}.vms", "wb")
        next_block = first_block
        while next_block != 65530:
            vms_file += blocks[f"{next_block}"]
            next_block = int.from_bytes(cat.fatTable[str(next_block)], "little")
        newFile.write(vms_file)

    def __init__(self, file):
        self.VMU = open(file, 'rb')
        self.fileSize = os.path.getsize(file)
        self.blocks = {}
        self.customColor = 0
        self.block_grab()

        # Root block
        self.customColor = self.block_read(255, "10", 1).hex()
        self.vmuBlue = self.block_read(255, "11", 1).hex()
        self.vmuGreen = self.block_read(255, "12", 1).hex()
        self.vmuRed = self.block_read(255, "13", 1).hex()
        self.vmuAlpha = self.block_read(255, "14", 1).hex()
        self.bcdTimeStamp = self.block_read(255, "30", 8).hex()
        self.fatLocation = int.from_bytes(self.block_read(255, "46", 1), "little")
        self.fatSize = int.from_bytes(self.block_read(255, "48", 1), "little")
        self.directoryLocation = int.from_bytes(self.block_read(255, "4a", 1), "little")
        self.directorySize = int.from_bytes(self.block_read(255, "4c", 1), "little")
        self.iconShape = int.from_bytes(self.block_read(255, "4e", 1), "little")
        self.userBlockCount = int.from_bytes(self.block_read(255, "50", 1), "little")

        # FAT Block
        self.fatBlock = self.block_read(self.fatLocation, "0", 512)
        self.fatTable = self.fat_grab(self.fatBlock)

        # Directory Block
        self.directory = self.directory_read(self.directorySize)
        self.directoryTable = self.directory_grab(self.directory, self.directorySize)

        # self.directoryEntryRead(self.directoryTable["0"])["fileName"])

cat = Vmu('star.bin')
catfat = cat.fatTable
catDir = cat.directory_entry_read(cat.directoryTable["0"])
# print(catDir)
# print(f'{cat.blocks["0"]}')
# print(catDir["fileSize"])
# print(catDir["firstBlock"])
# print(int.from_bytes(cat.fatTable["182"], "little"))

# def vms_from_blocks(filename,size,first_block,blocks):
#     vms_file = bytearray()
#     #use text read
#     filename = filename.decode('cp932', errors='replace')
#     filename = filter_non_printable(filename)
#     #use text read
#     newFile = open(f"{filename}.vms", "wb")
#     next_block = first_block
#     while next_block != 65530:
#         vms_file += blocks[f"{next_block}"]
#         next_block = int.from_bytes(cat.fatTable[str(next_block)], "little")
#     newFile.write(vms_file)


    # for block in range (size):
    #     print(block+first_block)
        # print(int.from_bytes(cat.fatTable[str(block+first_block)], "little"))
cat.vms_extract(catDir["fileName"],199,cat.blocks)
# vms_from_blocks(catDir["fileName"],18,199,cat.blocks)
# trying to read an entry from the directory table
