from lxml import etree as ET
import re
from xml_helper import * 


#The pins that contain this name and you want to be at the top of the schematic
up_pin_names = ["VCC"]
#The pins that contain this name and you want to be at the down of the schematic
down_pin_names = ["GND"]

NO_DIRECTION = -1
DOWN_DIRECTION = 0
UP_DIRECTION = 1
LEFT_DIRECTION = 2
RIGHT_DIRECTION = 3

LIB_PART = 'LibPart'
DEFN = 'Defn'
NORMAL_VIEW = 'NormalView'


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

		result = "%-10s %-20s %-10s %-20s" % (self.pin, self.pin_name, self.bank, dir)
		return result

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


#FIXME: check file if not opened
# file: input source file that open
def xas_get_device_name(file):
	for line in file:
		if 'Device' in line and 'xc' in line:
			words = line.split(' ')
			for word in words:
				if 'xc' in word:
					return word.strip() # remove whitespace character from leading and trailing of word
	return ""

#FIXME: check file if not opened
# file: input source file that open
def xas_get_pin_objects(file):
	header_column = []
	all_pins = []
	for line in file:
		if '--' in line[0:2] or '     ' in line[0:5]: # comment or line with only spaces
			continue
		if 'Total Number of Pins' in line:
			total_number_pins = filter(None, line.split(' '))[-2]
			if xas_is_int(total_number_pins):
				total_number_pins = int(total_number_pins)
			else:
				print("Total Number of Pins is wrong", total_number_pins)
			continue
		if 'Pin' in line[0:3]: # header line
			header_column = xas_split_header(line)
			continue

		words = line.split(' ') # this line contains pin information
		words = list(filter(lambda item: item !="" and item != "\r\n", words)) # remove empty string and '\r\n'

		pin_name = ""
		pin = ""
		bank = ""
		for index,header in enumerate(header_column):
			if header == 'Pin Name':
				pin_name = words[index]
				if 'IO_' in pin_name:
					pin_name = xas_rename_io_pin(pin_name, words, header_column)
			elif header == 'Pin':
				pin = words[index]
			elif header == 'Bank':
				bank = words[index]
		all_pins.append(PinObject(pin,pin_name,bank))
	return all_pins, total_number_pins
		
def xas_split_header(line):
	words = line.split('  ')
	columns = []
	for word in words:
		if word != '': # check string is not empty
			columns.append(word.strip("\r\n ")) # remove any '\r' , '\n' , ' ' from leading and trailing of word
	return columns

# Rename 'IO' in pin_name with (I/O Type) pin.
# Remove '_T[0-9][UL], _AD[0-99][NP], _T[0-9], _N[0-99]' in pin_name
# e.g. IO_L1P_AD11P_87 -> HD_L1P_87
def xas_rename_io_pin(pin_name, words, headers):

	result = re.sub('_AD\d{1,2}[NP]|_N\d{1,2}', '', pin_name)
	if "IO_L" in result: # in case of 'IO_T' dont remove T[0-9][UL] or _T[0-9]
		result = re.sub('_T[0-9][UL]|_T[0-9]', '', result)

	for index,header in enumerate(headers):
		if header == "I/O Type":
			result = result.replace("IO", words[index])
			break

	return result

def xas_is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
