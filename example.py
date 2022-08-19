"""A set of examples for VMS/VMI manipulation"""

import vmut

# tests
# animated VMS render
animated_vms = vmut.vms.load_vms("example_files/SCALIBUR.VMS")
print(animated_vms.info)
animated_vms.image_save("animaed.gif")

# vms_redner
gamesave_vms = vmut.vms.load_vms("example_files/THEME001.VMS")
print(gamesave_vms.info)
gamesave_vms.image_save("gamesave.png")

# vms_fix crc
broken_vms = vmut.vms.load_vms("example_files/broken.VMS")
print(broken_vms.info["crc"])
print(broken_vms.generated_crc())
broken_vms.fix_crc()

# vms_replace icon
old_icon = vmut.vms.load_vms("example_files/THEME001.VMS")
old_icon.update_icon('example_files/ICONDATA.png', 'replaced_icon.vms')
old_icon.image_save("replaced_icon.png")

# VMI generate
gamesave_vms.vmi_gen("test.vmi", "slurmking.com", "test VMI file")

# VMI verify
VMI_read = vmut.vms.Vmi_file("test.vmi")
print(VMI_read.info)
print(VMI_read.creation_string)

# ICONDATA create
vmut.Icon(image="example_files/slurm.png", threshold=160, invert=True).save("example_files/")
# ICONDATA export generated images
vmut.Icon(image="example_files/slurm.png", threshold=160, invert=True, export=True)

# ICONDATA export
ICONDATA_vms = vmut.vms.load_vms("example_files/ICONDATA.VMS")
print(ICONDATA_vms.info)
ICONDATA_vms.image_save("ICONDATA_color.png")
ICONDATA_vms.image_save("ICONDATA_mono.png", mono=True)
print(ICONDATA_vms.generated_crc())

# VMI Read
VMI_read = vmut.vms.Vmi_file("example_files/THEME001.VMI")
print(VMI_read.info)
