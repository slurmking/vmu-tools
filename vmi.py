"""Reads and creates vmi files"""
import unicodedata
from datetime import datetime


def filter_non_printable(text):
    """Filters text to printable unicode"""
    return ''.join(c for c in text if not unicodedata.category(c).startswith('C'))


def vmi_iso_date(year, month, day, hour, minute, second):
    """Converts vmi date data to readable string"""
    # dateString = f"{year}-{month}-{day} {hour:02d}:{minute:02d)}:{second:02d}.0"
    date_string = f'{year}-{month}-{day} {hour:02d}:{minute:02d}:{second:02d}.0'
    return date_string


def pad(string, max_length):
    """Pads data with 00s """
    out = string.ljust(max_length, '\x00')
    return out.encode('cp932')


def checksum_gen(resource_checksum):
    """Generates checksum"""
    sega_csum = int.from_bytes(bytes.fromhex('53454741'), "little")
    return resource_checksum & sega_csum


class VMI:
    """VMI object class"""

    def binary_read(self, offset, length):
        """reads binary from given offset"""
        self.vmi.seek(int(offset, 16))
        return self.vmi.read(length)

    def text_read(self, text):
        """converts text to cp932"""
        text = text.decode('cp932', errors='replace')
        text = filter_non_printable(text)
        return text

    def vmi_read(self):
        """reads VMI file"""
        self.checksum = int.from_bytes(self.binary_read("0", 4), "little")
        self.description = self.text_read(self.binary_read("04", 32))
        self.copyright = self.text_read(self.binary_read("24", 32))
        self.creation_year = int.from_bytes(self.binary_read("44", 2), "little")
        self.creation_month = int.from_bytes(self.binary_read("46", 1), "little")
        self.creation_day = int.from_bytes(self.binary_read("47", 1), "little")
        self.creation_hour = int.from_bytes(self.binary_read("48", 1), "little")
        self.creation_minute = int.from_bytes(self.binary_read("49", 1), "little")
        self.creation_second = int.from_bytes(self.binary_read("4A", 1), "little")
        self.creation_weekday = int.from_bytes(self.binary_read("4B", 1), "little")
        self.vmi_version = int.from_bytes(self.binary_read("4C", 2), "little")
        self.file_number = int.from_bytes(self.binary_read("4E", 2), "little")
        self.vms_resource_name = self.text_read(self.binary_read("50", 8))
        self.vms_file_name = self.text_read(self.binary_read("58", 12))
        self.file_mode = self.binary_read("64", 2).hex()
        self.file_size = int.from_bytes(self.binary_read("68", 4), "little")
        self.resource_checksum = int.from_bytes(self.binary_read("50", 4), "little")
        self.date_string = vmi_iso_date(self.creation_year, self.creation_month, self.creation_day, self.creation_hour,
                                        self.creation_minute, self.creation_second)

    @staticmethod
    def vmi_gen(info, copyright_message, description):
        """generates VMI from VMS class info"""
        copyright_message = copyright_message[:32]
        description = description[:32]
        if info['Type'] == 2:
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
        vms_resource_name = info['vmsName'].replace('.VMS', '')
        vms_file_name = info['vmsName']
        unknown_value = 0
        file_size = info['fileSize']
        checksum = int.from_bytes(bytes.fromhex(vms_resource_name.encode().hex()[0:8]), "little")

        with open(f"{vms_resource_name}.VMI", "wb", buffering=0) as file:
            file.write(checksum_gen(checksum).to_bytes(4, 'little'))
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

    def info(self):
        """Generates info dictionary"""
        self.vmi_read()
        info = {"checksum": self.checksum,
                "description": self.description,
                "copyright": self.copyright,
                "creationYear": self.creation_year,
                "creationMonth": self.creation_month,
                "creationDay": self.creation_day,
                "creationHour": self.creation_hour,
                "creationMinute": self.creation_minute,
                "creationSecond": self.creation_second,
                "creationWeekday": self.creation_weekday,
                "vmiVersion": self.vmi_version,
                "fileNumber": self.file_number,
                "vmsResourceName": self.vms_resource_name,
                "vmsFileName": self.vms_file_name,
                "fileMode": self.file_mode,
                "fileSize": self.file_size,
                "dateString": self.date_string}
        return info

    def __init__(self, file=None):
        if file is not None:
            self.vmi = open(file, 'rb')
        self.checksum = 0
        self.description = ""
        self.copyright = ""
        self.creation_year = 0
        self.creation_month = 0
        self.creation_day = 0
        self.creation_hour = 0
        self.creation_minute = 0
        self.creation_second = 0
        self.creation_weekday = 0
        self.vmi_version = 0
        self.file_number = 0
        self.vms_resource_name = ""
        self.vms_file_name = ""
        self.file_mode = 0
        self.file_size = 0
