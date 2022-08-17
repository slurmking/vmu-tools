"""Toolset for reading and modifying VMS files """
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from .icon import Img


# Static functions

def text_read(text):
    """Decodes binary to cp932 text and removes non unicode characters"""
    text = text.decode('cp932', errors='replace')
    # Removes non printable Ascii
    text = ''.join(c for c in text if not unicodedata.category(c).startswith('C'))
    return text


def int_read(number, endian):
    """Converts bytes to INT"""
    number = int.from_bytes(number, endian)
    return number


def binary_read(file, offset, length):
    """reads binary from given offset"""
    file.seek(offset)
    return file.read(length)


def pad(string, max_length):
    """Pads data with 00s """
    out = string.ljust(max_length, '\x00')
    return out.encode('cp932')


def vmi_checksum_gen(resource_checksum):
    """Generates checksum"""
    sega_csum = int.from_bytes(bytes.fromhex('53454741'), "little")
    return resource_checksum & sega_csum


def vmi_iso_date(year, month, day, hour, minute, second):
    """Converts vmi date data to readable string"""
    # dateString = f"{year}-{month}-{day} {hour:02d}:{minute:02d)}:{second:02d}.0"
    date_string = f'{year}-{month}-{day} {hour:02d}:{minute:02d}:{second:02d}.0'
    return date_string


def identify_type(file, name):
    """Identifies VMS file type"""
    zero_null = "00000000000000000000000000000000"
    f_null = "ffffffffffffffffffffffffffffffff"
    file_type = 1
    if binary_read(file, 0xe0, 16).hex() == zero_null or binary_read(file, 0xe0, 16).hex() == f_null:
        file_type = 2
    elif name == "ICONDATA.VMS":
        file_type = 3
    return file_type


def vms_data(game, vms_type):
    # TODO Implament eyecatch reading
    """Dumps vms data to dictionary"""
    game_offset = 0x200
    # for ICONDATA
    # 3 ICONDATA, 2 Minigame , 1 Gamesave
    if vms_type == 3:
        monochrome_offset = (Vmu_data(game, 0x10, 4), "little")
        icon_offset = (Vmu_data(game, 0x14, 4), "little")
        data = {"description": (Vmu_data(game, 0x00, 16), "text"),
                "monochrome_offset": (Vmu_data(game, 0x10, 4), "hex"),
                "icon_offset": (Vmu_data(game, 0x14, 4), "hex"),
                "first_padding": (Vmu_data(game, 0x18, 8), "hex"),
                "monochrome_bitmap": (Vmu_data(game, monochrome_offset[0].little_int, 128), "hex"),
                "icon_palette": (Vmu_data(game, icon_offset[0].little_int, 32), "bytes"),
                "icon_bitmaps": (Vmu_data(game, icon_offset[0].little_int + 32, 512), "hex"),
                "second_padding": (Vmu_data(game, 0x2c0, 320), "hex")}
        return data
    # Minigames are offset by 0x200
    elif vms_type == 1:
        game_offset = 0
    icon_count = Vmu_data(game, 0x40 + game_offset, 2).little_int
    data_size = Vmu_data(game, 0x48 + game_offset, 4).little_int
    data = {"vms_description": (Vmu_data(game, 0x0 + game_offset, 16), "text"),
            "description": (Vmu_data(game, 0x10 + game_offset, 32), "text"),
            "creating_app": (Vmu_data(game, 0x30 + game_offset, 16), "text"),
            "icon_count": (Vmu_data(game, 0x40 + game_offset, 2), "little"),
            "animation_speed": (Vmu_data(game, 0x42 + game_offset, 2), "little"),
            "eyecatch_type": (Vmu_data(game, 0x44 + game_offset, 2), "little"),
            "crc": (Vmu_data(game, 0x46 + game_offset, 2), "hex"),
            "data_size": (Vmu_data(game, 0x48 + game_offset, 4), "little"),
            "reserved": (Vmu_data(game, 0x4c + game_offset, 20), "bytes"),
            "icon_palette": (Vmu_data(game, 0x60 + game_offset, 32), "bytes"),
            "icon_bitmaps": (Vmu_data(game, 0x80 + game_offset, 512 * icon_count), "hex"),
            "data": (Vmu_data(game, (512 * icon_count + (0x80 + game_offset)), data_size), "bytes"),
            "padding": (Vmu_data(game, (512 * icon_count + (0x80 + game_offset)) + data_size, 99999), "bytes")}
    return data


def vmi_data(vmi_file):
    data = {"vms_checksum": (Vmu_data(vmi_file, 0x0, 4), "hex"),
            "description": (Vmu_data(vmi_file, 0x04, 32), "text"),
            "copyright": (Vmu_data(vmi_file, 0x24, 32), "text"),
            "creation_year": (Vmu_data(vmi_file, 0x44, 2), "little"),
            "creation_month": (Vmu_data(vmi_file, 0x46, 1), "little"),
            "creation_day": (Vmu_data(vmi_file, 0x47, 1), "little"),
            "creation_hour": (Vmu_data(vmi_file, 0x48, 1), "little"),
            "creation_minute": (Vmu_data(vmi_file, 0x49, 1), "little"),
            "creation_second": (Vmu_data(vmi_file, 0x4A, 1), "little"),
            "creation_weekday": (Vmu_data(vmi_file, 0x4B, 1), "little"),
            "vmi_version": (Vmu_data(vmi_file, 0x4C, 2), "little"),
            # todo: check version errors on sonic file
            "vmi_file_number": (Vmu_data(vmi_file, 0x4E, 2), "little"),
            "vms_resource_name": (Vmu_data(vmi_file, 0x50, 8), "text"),
            "vms_file_name": (Vmu_data(vmi_file, 0x58, 12), "text"),
            "vms_file_mode": (Vmu_data(vmi_file, 0x64, 2), "bytes"),
            "unknown": (Vmu_data(vmi_file, 0x66, 2), "bytes"),
            "vms_file_size": (Vmu_data(vmi_file, 0x68, 4), "little")}
    return data


def data_read(data):
    """reads game type info"""
    info = {}

    for key, value in data.items():
        if value[1] == "text":
            info[key] = value[0].text
        elif value[1] == "little":
            info[key] = value[0].little_int
        elif value[1] == "bytes":
            info[key] = value[0].bytes
        elif value[1] == "hex":
            info[key] = value[0].hex
    return info


def load_vms(file):
    """Loads VMS file"""
    return Vms_file(file)


def load_vmi(file):
    """Loads VMS file"""
    return Vmi_file(file)


# Classes


class Vmi_file:
    """Class to read and create VMI files"""

    def __init__(self, file):
        self.vmi_file = open(file, 'rb')
        self.data = vmi_data(self.vmi_file)
        self.info = data_read(self.data)
        self.creation_string = (
            vmi_iso_date(self.info["creation_year"], self.info["creation_month"], self.info["creation_day"],
                         self.info["creation_hour"],
                         self.info["creation_minute"], self.info["creation_second"]))


class Vmu_data:
    """Creates a data object to read VMU info"""

    def __init__(self, file, offset, length):
        file.seek(offset)
        binary_data = file.read(length)
        self.bytes = binary_data
        self.hex = binary_data.hex()
        self.text = text_read(binary_data)
        self.little_int = int_read(binary_data, "little")
        self.big_int = int_read(binary_data, "big")


class Vms_file:
    """VMS file object"""

    def update_file(self, output_location):
        """Creates VMS file from the self.data dictionary"""
        with open(f"{output_location}", "wb", buffering=0) as vms_file:
            for key, value in self.data.items():
                if type(value) is tuple:
                    vms_file.write(value[0].bytes)
                else:
                    vms_file.write(value)

    def generated_crc(self):
        """Generates new crc"""
        game_data = bytearray()
        for key, value in self.data.items():
            if key == "crc":
                game_data.extend(b'\x00\x00')
            elif key == "padding":
                continue
            else:
                game_data.extend(value[0].bytes)
        xored_byte = 0
        for bit in game_data:
            xored_byte ^= (bit << 8)
            byte_steps = 0
            while byte_steps < 8:
                if xored_byte & 0x8000:
                    xored_byte = ((xored_byte << 1) ^ 4129)
                else:
                    xored_byte = (xored_byte << 1)
                byte_steps += 1
        return (xored_byte & 0xffff).to_bytes(2, "little")

    def fix_crc(self):
        self.data["crc"] = self.generated_crc()
        self.update_file(self.vms_file.name)

    def image_save(self, save, mono=False):
        """Saves vms icon to file output"""
        if self.vms_type == 3:
            if not mono:
                Img.gen_img(self.info["icon_bitmaps"], self.info["icon_palette"], 1, 1, mono=False, save=save)
            else:
                Img.gen_img(self.info["monochrome_bitmap"], self.info["icon_palette"], 1, 1, mono=True, save=save)
        else:
            Img.gen_img(self.info["icon_bitmaps"], self.info["icon_palette"], self.info["icon_count"],
                        self.info["animation_speed"], mono=False, save=save)

    def vmi_gen(self, save, copyright_message, description):
        """generates VMI from VMS class info"""
        copyright_message = copyright_message[:32]
        description = description[:32]
        if self.vms_type == 2:
            file_mode = '0010'
        else:
            file_mode = '0000'
        year = int(datetime.today().strftime('%Y'))
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        hour = int(datetime.today().strftime('%H'))
        minute = int(datetime.today().strftime('%M'))
        second = int(datetime.today().strftime('%S'))
        weekday = 0
        vmi_version = 0
        file_number = 1
        vms_resource_name = os.path.basename(self.vms_file.name).replace('.VMS', '')
        vms_file_name = os.path.basename(self.vms_file.name)
        unknown_value = 0
        file_size = os.path.getsize(self.file)
        checksum = int.from_bytes(bytes.fromhex(vms_resource_name.encode().hex()[0:8]), "little")

        with open(save, "wb", buffering=0) as file:
            file.write(vmi_checksum_gen(checksum).to_bytes(4, 'little'))
            file.write(pad(description, 32))
            file.write(pad(copyright_message, 32))
            file.write(year.to_bytes(2, 'little'))
            file.write(month.to_bytes(1, 'little'))
            file.write(day.to_bytes(1, 'little'))
            file.write(hour.to_bytes(1, 'little'))
            file.write(minute.to_bytes(1, 'little'))
            file.write(second.to_bytes(1, 'little'))
            file.write(weekday.to_bytes(1, 'little'))
            file.write(vmi_version.to_bytes(2, 'little'))
            file.write(file_number.to_bytes(2, 'little'))
            file.write(pad(vms_resource_name, 8))
            file.write(pad(vms_file_name, 12))
            file.write(bytearray.fromhex(file_mode))
            file.write(unknown_value.to_bytes(2, 'little'))
            file.write(file_size.to_bytes(4, 'little'))

    def __init__(self, file):
        self.file = file
        self.vms_file = open(file, 'rb')
        self.vms_type = identify_type(self.vms_file, Path(self.vms_file.name).name)
        self.data = vms_data(self.vms_file, self.vms_type)
        self.info = data_read(self.data)
        self.file_size = os.path.getsize(self.vms_file.name)
