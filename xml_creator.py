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


class PinObject():

	def __init__(self, pin, pin_name, bank):
		self.pin = pin
		self.pin_name = pin_name
		self.bank = bank
		if( bank!="NA" ):
			self.bank = int(bank)
		self.direction = NO_DIRECTION

	def get_pin(self):
		return self.pin

	def set_pin(self,pin):
		self.pin = pin

	def get_pin_name(self):
		return self.pin_name

	def set_pin_name(self,name):
		self.pin_name = name

	def get_bank(self):
		return self.bank

	def set_bank(self,bank):
		self.bank = int(bank)

	def get_direction(self):
		return self.direction

	def set_direction(self,direction):
		self.direction = direction

	def __str__(self):
		dir = ""
		if(self.direction==UP_DIRECTION):
			dir = "UP"
		elif (self.direction==DOWN_DIRECTION):
			dir = "DOWN"
		elif (self.direction==RIGHT_DIRECTION):
			dir = "RIGHT"
		elif (self.direction==LEFT_DIRECTION):
			dir = "LEFT"
		else:
			dir = "NO_DIRECTION"

		return self.pin + "\t" + self.pin_name + "\t" + str(self.bank) + "\t" + dir


class Bank():
	def __init__(self, id, device_name):
		self.id = id
		self.device_name = device_name
		self.pin_objects = []
		self.pin_down = []
		self.pin_up = []
		self.pin_left = []
		self.pin_right = []
		self.type = ""

	def get_id(self):
		return self.id

	def set_id(self,id):
		self.id = id

	def get_type(self):
		return self.type

	def set_type(self, type):
		self.type = type

	def get_number_of_rx(self):
		cnt=0
		for pin in self.pin_objects:
			if "RX" in pin.get_pin_name():
				cnt += 1
		return cnt

	def get_device_name(self):
		return self.device_name

	def add_pin(self,pin):
		self.pin_objects.append(pin)

	def get_pin_objects(self):
		return self.pin_objects

	def add_pin_from_bank(self,bank):
		self.pin_objects.extend(bank.get_pin_objects())
		self.set_up_down_left_right_pins()

	def set_pin_direction(self):
		cnt = 0
		for pin in self.pin_objects:
			pin_name = pin.get_pin_name()
			for upn in up_pin_names:
				if upn in pin_name:
					pin.set_direction(UP_DIRECTION)
					cnt += 1
			for dpn in down_pin_names:
				if dpn in pin_name:
					pin.set_direction(DOWN_DIRECTION)
					cnt += 1
		cnt1 = (len(self.pin_objects) - cnt)/2
		for pin in self.pin_objects:
			if(pin.get_direction()==NO_DIRECTION):
				if(cnt1>0):
					pin.set_direction(LEFT_DIRECTION)
					cnt1 -= 1
				else:
					pin.set_direction(RIGHT_DIRECTION)

	def set_up_down_left_right_pins(self):
		self.set_pin_direction()
		for pin in self.pin_objects:
			if(pin.get_direction()==UP_DIRECTION):
				self.pin_up.append(pin)
			elif(pin.get_direction()==DOWN_DIRECTION):
				self.pin_down.append(pin)
			elif(pin.get_direction()==LEFT_DIRECTION):
				self.pin_left.append(pin)
			elif(pin.get_direction()==RIGHT_DIRECTION):
				self.pin_right.append(pin)

	def append_bank_number_to_pin_name(self):
		for pin in self.pin_objects:
			pin_name = pin.get_pin_name()
			bn = pin_name.split('_')[-1]
			if bn.isdigit() != True or int(bn) != self.id:
				pin.set_pin_name(pin_name + "_" + str(self.id))

	# add index to pin_name if equals with another pin_name
	def rename_pin_name(self):
		cnt = 1
		for i,pin1 in enumerate(self.pin_objects):
			for j,pin2 in enumerate(self.pin_objects):
				if i!=j and pin1.get_pin_name()==pin2.get_pin_name():
					pin1.set_pin_name(pin1.get_pin_name() + "_" + str(cnt))
					cnt += 1

	def calculate_rect_size(self):
		left_size = 0
		for pin in self.pin_left:
			if(left_size<len(pin.get_pin_name())):
				left_size = len(pin.get_pin_name())

		right_size = 0
		for pin in self.pin_right:
			if(right_size<len(pin.get_pin_name())):
				right_size = len(pin.get_pin_name())

		up_size = 0
		for pin in self.pin_up:
			if(up_size<len(pin.get_pin_name())):
				up_size = len(pin.get_pin_name())
		
		down_size = 0
		for pin in self.pin_down:
			if(down_size<len(pin.get_pin_name())):
				down_size = len(pin.get_pin_name())

		# print(max(len(self.pin_down,self.pin_up))
		width = max(len(self.pin_down),len(self.pin_up)) + (right_size + left_size)/2
		height = max(len(self.pin_left),len(self.pin_right)) + (down_size + up_size)/2
		return max(width,height)

	def create_xml(self):

		rect_size = int(self.calculate_rect_size()*10)

		lp = ET.Element(LIB_PART)
		lp.append(ET.Element(DEFN))

		pp = ET.Element('PhysicalPart')
		pp.append(ET.Element(DEFN))

		nv = ET.Element(NORMAL_VIEW)
		defn = ET.Element(DEFN,suffix=".Normal")
		nv.append(defn)

		v_locx = int(rect_size/2 - (len(self.device_name)/2/2 - 1)*10)
		v_locy = int(rect_size/2)
		pcb_locx = v_locx
		pcb_locy = v_locy + 10
		r_locx = int(rect_size/2)
		r_locy = v_locy - 10

		nv.append(create_xml_symbol_diplay_prop(_locX=r_locx,_locY=r_locy,_name="Part Reference",_dispType=1))
		nv.append(create_xml_symbol_diplay_prop(_locX=v_locx,_locY=v_locy,_name="Value",_dispType=1))
		nv.append(create_xml_symbol_diplay_prop(_locX=pcb_locx,_locY=pcb_locy,_name="PCB Footprint",_dispType=0))
		nv.append(create_xml_symbol_user_prop("PCB Footprint",self.device_name))
		nv.append(create_xml_symbol_user_prop("Value",self.device_name))
		nv.append(create_xml_symbol_user_prop("Description",self.device_name))
		nv.append(create_xml_symbol_user_prop("Name",self.device_name))
		nv.append(create_xml_symbol_user_prop("SPLIT_INST","TRUE"))
		nv.append(create_xml_symbol_user_prop("SWAP_INFO","(S1+S2+S3+S4+S5+S6+S7)"))
		nv.append(create_xml_symbol_color(48))
		nv.append(create_xml_symbol_b_box(_x1=0,_x2=rect_size,_y1=0,_y2=rect_size))
		nv.append(create_xml_is_pin_numbers_visible(1))
		nv.append(create_xml_is_pin_names_rotated(1))
		nv.append(create_xml_is_pin_names_visible(1))
		nv.append(create_xml_contents_lib_name(""))
		nv.append(create_xml_contents_view_name(""))
		nv.append(create_xml_contents_view_type(0))
		nv.append(create_xml_part_value(self.device_name))
		nv.append(create_xml_reference("U"))
		nv.append(create_xml_rect(_x1=0,_x2=rect_size,_y1=0,_y2=rect_size))

		for i,pin in enumerate(self.pin_up):
			pin_name = pin.get_pin_name()
			startX = int((rect_size-len(self.pin_up)*10)/2 + 10*(i+1))
			startY = 0
			hotptX = startX
			hotptY = startY - 30
			type_pin = 7
			position = i
			nv.append(create_xml_symbol_pin_scalar(   _hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
																_startX=startX,_startY=startY,_type=type_pin))
			pp.append(create_xml_pin_number(pin.get_pin(),position))
		
		cnt = len(self.pin_up)
		for i,pin in enumerate(self.pin_down):
			pin_name = pin.get_pin_name()
			startX = int((rect_size-len(self.pin_down)*10)/2 + 10*(i+1))
			startY = rect_size
			hotptX = startX
			hotptY = startY + 30
			type_pin = 7
			position = i + cnt
			nv.append(create_xml_symbol_pin_scalar(   _hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
																_startX=startX,_startY=startY,_type=type_pin))
			pp.append(create_xml_pin_number(pin.get_pin(),position))

		cnt = len(self.pin_up) + len(self.pin_down)
		for i,pin in enumerate(self.pin_right):
			pin_name = pin.get_pin_name()
			startX = rect_size
			startY = int((rect_size-len(self.pin_right)*10)/2 + 10*(i+1))
			hotptX = startX + 30
			hotptY = startY
			type_pin = 1
			position = i + cnt
			nv.append(create_xml_symbol_pin_scalar(   _hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
																_startX=startX,_startY=startY,_type=type_pin))
			pp.append(create_xml_pin_number(pin.get_pin(),position))

		cnt = len(self.pin_up) + len(self.pin_down) + len(self.pin_right)
		for i,pin in enumerate(self.pin_left):
			pin_name = pin.get_pin_name()
			startX = 0
			startY = int((rect_size-len(self.pin_left)*10)/2 + 10*(i+1))
			hotptX = startX - 30
			hotptY = startY
			type_pin = 1
			position = i + cnt
			nv.append(create_xml_symbol_pin_scalar(   _hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
																_startX=startX,_startY=startY,_type=type_pin))
			pp.append(create_xml_pin_number(pin.get_pin(),position))
		
		lp.append(nv)
		lp.append(pp)

		return lp

	def __str__(self):
		s = str(self.id) + "\n"
		for pin in self.pin_objects:
			s += pin.__str__()
			s += "\n"
		return s

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
			
device_name,all_pins = get_device_name_and_pin_objects()

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

try:
	file = open(SOURCE_FILE, 'r')
	print(get_device_name(file))
except IOError:
	print("Could not open file")


# create_output_file(device_name,all_banks)
# os.system("./script.sh " + RESULT_FILE)