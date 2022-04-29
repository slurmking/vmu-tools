![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vmu-tools)![PyPI - PyPi Version](https://img.shields.io/pypi/v/vmu-tools.svg)

# VMU Tools

This python project is designed to be a fully loaded suite of VMU tools for the dreamcast.

### Features
* Read and extract data from .VMS and  .VMI files
* Generate icons from ICONDATA and VMS files
* Generate VMI files from VMS 
* Read and manipulate VMU dumps files
* Extract and upload savegames from VMU dump files

### Install 
``` python
pip install vmu-tools --upgrade
```

### Example

```python
import vmut

# Load .VMS file
VMS = vmut.vms.load_vms("example_files/SCALIBUR.VMS")

# Print info
print(VMS.info)

# Save icon
VMS.image_save("animaed.gif")

# Generate Checksum
print(VMS.generated_crc())

#Generate VMI
VMS.vmi_gen("test.vmi", "slurmking.com", "test VMI file")

#Fix crc
VMS.fix_crc()
```




### Roadmap
* Create ICONDATA and VMS icons from PNG and JPEG
* Change VMU color
* Convert VMU dumps to and from .DCI files
* Modify VMU ICONDATA from VMU dumps
* Possibly implament a built in webserver for file transfers from Dreamcast




----
##### Special Thanks  to:
* Marcus Comstedt https://mc.pp.se/dc/
	* For providing the best documentation on the Dreamcast 
* [mrneo240](https://github.com/mrneo240)
	* for assistance on creating ICONDATA tools
*  [bucanero](https://github.com/bucanero)
	* For providing a dump of usefull test files
