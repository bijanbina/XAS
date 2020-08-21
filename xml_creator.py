import math
from xml_helper import *
from pin_parser import *
import os
import sys


#vcc names that wants them to be in a specific bank(vcc_bank)
vcc_name = ["VCCINT","VCCBRAM","VCCAUX","VCCPAUX","VCCPINT","VCCPLL", "VCCADC"]
vcc_bank = 0

#The pins that contain this name and you want to be at the top of the schematic
up_pin_names = ["VCC"]
#The pins that contain this name and you want to be at the down of the schematic
down_pin_names = ["GND"]

ps_mode = False
ps_banks = [500,501]

NO_DIRECTION = -1
DOWN_DIRECTION = 0
UP_DIRECTION = 1
LEFT_DIRECTION = 2
RIGHT_DIRECTION = 3

BANK_MGT_TYPE = "MGT"
BANK_PS_TYPE = "PS"
BANK_NR_TYPE = "NR" #Normal bank

def get_device_name_and_pin_objects():
	try:
		file = open(SOURCE_FILE, 'r')
		line = file.readline()
		if '--' in line: #New format file
			line = file.readline()
			while '--' in line:
				line = file.readline()
			device_name = SOURCE_FILE[:-7]
		else: #Old format file
			device_name = line.split()[1]
			line = file.readline() # '/n'
		line = file.readline() # header
		all_pins = []
		for line in file:
			words = line.split()
			if(len(words)>5):
				pin = words[0]
				pin_name = words[1]
				bank = words[3]
				all_pins.append(PinObject(pin,pin_name,bank))
		file.close()
		return device_name,all_pins
	except IOError:
		print("Could not open file")

def update_bank_for_mgt(all_pins, all_banks):
	n_all_banks = []
	merged_banks = []
	is_merged = False

	for bank1 in all_banks:
		is_merged = False
		if bank1.get_type() == "MGT":
			if bank1.get_id() in merged_banks:
				continue
			if bank1.get_number_of_rx() <= 8:
				for bank2 in all_banks:
					if bank2.get_id() != bank1.get_id() and bank2.get_type() == "MGT" and bank2.get_id() not in merged_banks:
						merged_banks.append(bank1.get_id())
						merged_banks.append(bank2.get_id())
						bank = merge_banks(bank1, bank2)
						bank.set_type("MGT")
						n_all_banks.append(bank)
						is_merged = True
						break
				if is_merged == False:
					n_all_banks.append(bank1)
			else:
				n_all_banks.append(bank1)
		else:
			n_all_banks.append(bank1)

	return n_all_banks

def set_direction_pins_in_banks(all_banks):
	for bank in all_banks:
		bank.set_up_down_left_right_pins()

def merge_banks(bank1,bank2):
	bank = Bank(bank1.get_id(),bank1.get_device_name())
	bank.add_pin_from_bank(bank1)
	bank.add_pin_from_bank(bank2)
	return bank

def update_bank_for_ps_mode(all_banks):
	n_all_banks = []
	bank1 = 0
	bank2 = 0
	for bank in all_banks:
		if bank.get_id() in ps_banks:
			if bank1 == 0:
				bank1 = bank
			elif bank2 ==0:
				bank2 = bank
		else:
			n_all_banks.append(bank)
	bank_ps = merge_banks(bank1,bank2)
	n_all_banks.append(bank_ps)
	return n_all_banks

def create_output_file(device_name,all_banks):
	package = create_package(device_name)
	n_all_banks = []
	if ps_mode:
		n_all_banks = update_bank_for_ps_mode(all_banks)
	else:
		n_all_banks = all_banks
	for bank in n_all_banks:
		package.append(bank.create_xml())

	f = open(OUTPUT_FILE,'wb')
	f.write(ET.tostring(package,pretty_print=True))
	f.close()

def print_pins(all_pins):
	for pin in all_pins:
		if pin.get_bank() == "NA":
			print(pin)
		# if(pin.get_bank()=="NA"):
		#     print(pin)

def print_banks(all_banks):
	for bank in all_banks:
		print(bank)

SOURCE_FILE = sys.argv[1] # input pin file sourced from xilinx
RESULT_FILE = sys.argv[2] # output xml filename
OUTPUT_FILE = 'temp.xml'
			
# device_name,all_pins = get_device_name_and_pin_objects()

try:
	file = open(SOURCE_FILE, 'r')
	device_name = xas_get_device_name(file)
	file.seek(0) # go back to the start of the file.
	all_pins, total_pins = xas_get_pin_objects(file)
	# Check number of read pin with total pin number in source file
	if len(all_pins) != total_pins:
		print("number of pin object that read from source file is wrong")
		exit

	file.close()
except IOError:
	print("Could not open %s" % (SOURCE_FILE))


nr_banks = set() #Normal banks
mgt_banks = set() #MGT banks
ps_banks = set() #PS banks
cnt_mgtv_pin = 0
cnt_mgtv_ps_pin = 0
cnt_gnd = 0
for pin in all_pins:

	pin_name = pin.get_pin_name()

	# set vcc_bank to vcc_pins
	for vccn in vcc_name:
		if vccn in pin_name and BANK_MGT_TYPE not in pin_name:
			pin.set_bank(vcc_bank)

	#Count number of ground pins
	if "GND" in pin_name:
		cnt_gnd += 1

	pin_bank = pin.get_bank()
	
	#Count MGT,PS banks and total banks
	if pin_bank != "NA":
		if BANK_MGT_TYPE in pin_name and BANK_PS_TYPE not in pin_name:
			mgt_banks.add(pin_bank)
		elif BANK_PS_TYPE in pin_name:
			ps_banks.add(pin_bank)
		else:
			nr_banks.add(pin_bank)

	#Count MGT,PS pins
	if pin_bank == "NA":
		if BANK_MGT_TYPE in pin_name and BANK_PS_TYPE not in pin_name:
			cnt_mgtv_pin += 1
		elif BANK_PS_TYPE in pin_name:
			cnt_mgtv_ps_pin += 1

mgt_banks = list(mgt_banks)
ps_banks = list(ps_banks)
nr_banks = list(nr_banks)
total_banks = len(mgt_banks) + len(ps_banks) + len(nr_banks)

#Create all banks based on types
all_banks = []
for id_bank in mgt_banks:
	bnk = Bank(id_bank, device_name)
	bnk.set_type(BANK_MGT_TYPE)
	all_banks.append(bnk)

for id_bank in ps_banks:
	bnk = Bank(id_bank, device_name)
	bnk.set_type(BANK_PS_TYPE)
	all_banks.append(bnk)

for id_bank in nr_banks:
	bnk = Bank(id_bank, device_name)
	bnk.set_type(BANK_NR_TYPE)
	all_banks.append(bnk)

gnd_in_bank = math.ceil(float(cnt_gnd)/total_banks)
mgtv_in_bank = math.ceil(float(cnt_mgtv_pin)/len(mgt_banks))
mgtv_ps_in_bank = math.ceil(float(cnt_mgtv_ps_pin)/len(ps_banks))

index_gnd = 0
cnt_gnd = 0
index_mgtv = 0
cnt_mgtv = 0
index_mgtv_ps = 0
cnt_mgtv_ps = 0
for pin in all_pins:

	pin_bank = pin.get_bank()

	if pin_bank == "NA":
		pin_name = pin.get_pin_name()

		#Assign gnd pins to banks
		if "GND" in pin_name:
			pin.set_bank(all_banks[index_gnd].get_id())
			cnt_gnd += 1
			if cnt_gnd == gnd_in_bank:
				cnt_gnd = 0
				index_gnd += 1
		#Assign mgtv pins to mgt banks
		elif BANK_MGT_TYPE in pin_name and BANK_PS_TYPE not in pin_name:
			pin.set_bank(mgt_banks[index_mgtv])
			cnt_mgtv += 1
			if cnt_mgtv == mgtv_in_bank:
				cnt_mgtv = 0
				index_mgtv += 1
		#Assign ps_mgtv pins to ps banks
		elif BANK_PS_TYPE in pin_name: 
			pin.set_bank(ps_banks[index_mgtv_ps])
			cnt_mgtv_ps += 1
			if cnt_mgtv_ps == mgtv_ps_in_bank:
				cnt_mgtv_ps = 0
				index_mgtv_ps += 1
		#Assign remining pins to vcc_bank
		else:
			pin.set_bank(vcc_bank)

	for bank in all_banks:
		if pin.get_bank() == bank.get_id():
			bank.add_pin(pin)

for bank in all_banks:
	bank.append_bank_number_to_pin_name()
	bank.rename_pin_name()
	bank.set_up_down_left_right_pins()

create_output_file(device_name,all_banks)
os.system("./script.sh " + RESULT_FILE)