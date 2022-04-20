"""Reads VMU dumps and creates Python variables"""
import os
import unicodedata


def filter_non_printable(text):
    """Filters text to printable unicode"""
    return ''.join(c for c in text if not unicodedata.category(c).startswith('C'))


class Vmu:
    """Get data from VMS file"""

    def binary_read(self, offset, length):
        """Reads binary from file offset"""
        self.vmu.seek(int(offset, 16))
        return self.vmu.read(length)

    def text_read(self, text):
        """Converts binary to text cp932"""
        text = text.decode('cp932', errors='replace')
        text = filter_non_printable(text)
        return text

    def block_read(self, block, offset, length):
        """Reads specific offset from input block"""
        block = self.blocks[str(block )]
        offset = int(offset, base=16)
        length = offset + length
        return block[offset:length]

    def directory_read(self, size):
        """Creates a dictionary of every block in the directory"""
        directory = {}
        for block in range(size):
            directory[str(block)] = self.block_read(self.directory_location - block, "0", 512)
        return directory

    def directory_parse(self, entry, offset, length):
        """Reads specific offset from directory entry"""
        offset = int(offset, base=16)
        length = offset + length
        return entry[offset:length]

    def directory_entry_read(self, entry):
        """Outputs all relevant directory info to a dictionary"""
        directory = {"fileType": self.directory_parse(entry, "0", 1),
                     "copyProtect": self.directory_parse(entry, "1", 1),
                     "firstBlock": int.from_bytes(self.directory_parse(entry, "2", 2), "little"),
                     "fileName": self.directory_parse(entry, "4", 12),
                     "creationTime": self.directory_parse(entry, "10", 8).hex(),
                     "fileSize": int.from_bytes(self.directory_parse(entry, "18", 2), "little"),
                     "headerOffset": int.from_bytes(self.directory_parse(entry, "1a", 2), "little")}
        return directory

    def block_grab(self):
        """Creates dictionary for every block"""
        count = 0
        for i in range(0, self.file_size, 512):
            count += 1
            self.blocks[f"{count-1}"] = self.binary_read(hex(i), 512)

    def fat_grab(self, fat_block):
        """Creates dictionary for the FAT table"""
        self.fat_table = {}
        block_count = 0
        for index in range(0, 512, 2):
            self.fat_table[f"{block_count}"] = fat_block[index:index + 2]
            block_count += 1
        return self.fat_table

    def directory_grab(self, directory, size):
        """Creates dictionary for directory table"""
        self.directory_table = {}
        entry = 0
        for block in directory:
            for index in range(0, 32 * size * 16, 32):
                self.directory_table[f"{entry}"] = directory[f"{block}"][index:index + 32]
                entry += 1
        return self.directory_table

    def vms_extract(self, filename, first_block, blocks):
        """Creates a VMS file from directory blocks"""
        vms_file = bytearray()
        # use text read
        filename = self.text_read(filename)
        # use text read
        new_file = open(f"{filename}.vms", "wb")
        next_block = first_block
        while next_block != 65530:
            vms_file += blocks[f"{next_block}"]
            next_block = int.from_bytes(cat.fat_table[str(next_block)], "little")
        new_file.write(vms_file)

    def __init__(self, file):
        self.vmu = open(file, 'rb')
        self.file_size = os.path.getsize(file)
        self.blocks = {}
        self.custom_color = 0
        self.block_grab()

        # Root block
        self.custom_color = self.block_read(255, "10", 1).hex()
        self.vmu_blue = self.block_read(255, "11", 1).hex()
        self.vmu_green = self.block_read(255, "12", 1).hex()
        self.vmu_red = self.block_read(255, "13", 1).hex()
        self.vmu_alpha = self.block_read(255, "14", 1).hex()
        self.bcd_time_stamp = self.block_read(255, "30", 8).hex()
        self.fat_location = int.from_bytes(self.block_read(255, "46", 1), "little")
        self.fat_size = int.from_bytes(self.block_read(255, "48", 1), "little")
        self.directory_location = int.from_bytes(self.block_read(255, "4a", 1), "little")
        self.directory_size = int.from_bytes(self.block_read(255, "4c", 1), "little")
        self.icon_shape = int.from_bytes(self.block_read(255, "4e", 1), "little")
        self.user_block_count = int.from_bytes(self.block_read(255, "50", 1), "little")

        # FAT Block
        self.fat_block = self.block_read(self.fat_location, "0", 512)
        self.fat_table = self.fat_grab(self.fat_block)

        # Directory Block
        self.directory = self.directory_read(self.directory_size)
        self.directory_table = self.directory_grab(self.directory, self.directory_size)

        # self.directoryEntryRead(self.directoryTable["0"])["fileName"])

cat = Vmu('star.bin')
catfat = cat.fat_table
catDir = cat.directory_entry_read(cat.directory_table["0"])
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
