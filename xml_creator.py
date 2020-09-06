import math
from xml_helper import *
from pin_parser import *
import os
import sys


def create_output_file(device_name, all_banks):
	package = create_package(device_name)
	for bank in all_banks:
		package.append(bank.create_xml(device_name))

	f = open(OUTPUT_FILE,'wb')
	f.write(ET.tostring(package,pretty_print=True))
	f.close()

def print_pins(all_pins):
	for pin in all_pins:
		print(pin)

def print_banks(all_banks):
	for bank in all_banks:
		print(bank)

SOURCE_FILE = sys.argv[1] # input pin file sourced from xilinx
RESULT_FILE = sys.argv[2] # output xml filename
OUTPUT_FILE = 'temp.xml'
			
try:
	file = open(SOURCE_FILE, 'r')
	device_name = xas_get_device_name(file)
	file.seek(0) # go back to the start of the file.
	all_banks, total_pins = xas_get_bank_objects(file)
	# Check number of read pin with total pin number in source file
	if xas_get_total_pins(all_banks) != total_pins:
		msg = "Error: Number of pin object that read from " + SOURCE_FILE + " file is wrong\r\n"
		msg += "Total Pins: " + str(total_pins) + ", Total Read Pins: " + str(xas_get_total_pins(all_banks))
		print(msg)
		exit

	file.close()
except IOError:
	print("Could not open %s" % (SOURCE_FILE))
	exit

# Append bank number to pin name and unify the names all pin in bank
# and set direction to pins based on type bank
for bank in all_banks:
	bank.append_bank_number_to_pin_name()
	bank.rename_pin_name()
	bank.set_pins_direction()

# create_output_file(device_name,all_banks)
# os.system("./script.sh " + RESULT_FILE)