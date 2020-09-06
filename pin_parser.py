from lxml import etree as ET
import re
from xml_helper import * 
import math


#The pins that contain this name and you want to be at the top of the schematic
up_pin_names = ["VCC", "VTT"]
#The pins that contain this name and you want to be at the down of the schematic
down_pin_names = ["GND"]

special_pin_names = ["VREF"]

NO_DIRECTION = -1
DOWN_DIRECTION = 0
UP_DIRECTION = 1
LEFT_DIRECTION = 2
RIGHT_DIRECTION = 3

LIB_PART = 'LibPart'
DEFN = 'Defn'
NORMAL_VIEW = 'NormalView'

# Bank Types
XAS_HP_BANK  = "HP"
XAS_HR_BANK  = "HR"
XAS_MGT_BANK = "MGT"
XAS_PSMGT_BANK  = "PSMGT"
XAS_DDR_BANK  = "DDR"
XAS_PS_BANK  = "PS"
XAS_PSCONFIG_BANK  = "PSCONFIG"
XAS_PLCONFIG_BANK  = "PLCONFIG"
XAS_DATA_BANK = "DATA"


class PinObject():

	def __init__(self, pin, pin_name, io_type, bank):
		self.pin = pin
		self.pin_name = pin_name
		self.io_type = io_type
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

	def get_io_type(self):
		return self.io_type

	def get_bank_number(self):
		return self.bank

	def get_direction(self):
		return self.direction

	def set_direction(self,direction):
		self.direction = direction

	def get_string_direction(self):
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
		return dir

	def __str__(self):
		result = "Pin:%-10s Pin name:%-20s Direction:%-20s" % (self.pin, self.pin_name, self.get_string_direction())
		return result

class Bank():

	# @type: XAS_BANK_TYPES(XAS_HP_BANK, XAS_HR_BANK, XAS_MGT_BANK, XAS_PSMGT_BANK,...)
	# @cap:  capacity bank for bank numbers(for example bank number 503,502 -> cnt=2)
	def __init__(self, type, cap):
		self.type = type
		self.capacity = cap
		self.numbers = [] # bank numbers that max size = capacity
		self.pin_objects = []
		self.pin_down = []
		self.pin_up = []
		self.pin_left = []
		self.pin_right = []

	def get_bank_numbers(self):
		return self.numbers

	def add_bank_number(self, id):
		self.numbers.append(id)

	def get_type(self):
		return self.type

	def set_type(self, type):
		self.type = type

	def is_full(self):
		return self.capacity == len(self.numbers)

	def add_pin(self,pin):
		self.pin_objects.append(pin)

	def get_pin_objects(self):
		return self.pin_objects

	def set_pins_direction(self):
		self.set_up_down_left_right_pins()

	def set_up_down_left_right_pins(self):

		num_pin_assigned_direction = 0 # the number of pins that assigned them direction

		if self.type == XAS_DATA_BANK:# Direction for DATA bank is set when read from file
			num_pin_assigned_direction = len(self.pin_objects) # all pins set directions
		else:
			for pin in self.pin_objects:
				pin_name = pin.get_pin_name()

				#if pin name contain any word in 'up_pin_names'
				if any(upn in pin_name for upn in up_pin_names):
					pin.set_direction(UP_DIRECTION)
					self.pin_up.append(pin)
					num_pin_assigned_direction += 1
					continue

				#if pin name contain any word in 'down_pin_names'
				if any(dpn in pin_name for dpn in down_pin_names):
					pin.set_direction(DOWN_DIRECTION)
					self.pin_down.append(pin)
					num_pin_assigned_direction += 1
					continue

		#FIXME: for based on bank numbers
		#right and left pins for HP and HR banks
		if self.type == XAS_HR_BANK or self.type == XAS_HP_BANK:
			num_diff_pin = self.get_num_pin_io(is_diff=True)/2 # /2 for N,P
			for i in range(0,num_diff_pin/2):# /2 for left,right

				# add differential pins to left
				d_pin_name = "L" + str(i+1) + "P" # desired pin name
				p_pin = self.get_pin_io(d_pin_name)#FIXME: change get_pin_io with get_desired_pin
				p_pin.set_direction(LEFT_DIRECTION)
				self.pin_left.append(p_pin)

				d_pin_name = "L" + str(i+1) + "N" # desired pin name
				n_pin = self.get_pin_io(d_pin_name)
				n_pin.set_direction(LEFT_DIRECTION)
				self.pin_left.append(n_pin)

				# add differential pins to right
				d_pin_name = "L" + str(num_diff_pin - i) + "P" # desired pin name
				p_pin = self.get_pin_io(d_pin_name)
				p_pin.set_direction(RIGHT_DIRECTION)
				self.pin_right.insert(0, p_pin)

				d_pin_name = "L" + str(num_diff_pin - i ) + "N" # desired pin name
				n_pin = self.get_pin_io(d_pin_name)
				n_pin.set_direction(RIGHT_DIRECTION)
				self.pin_right.insert(0, n_pin)

				num_pin_assigned_direction += 4

			num_single_ended_pin = self.get_num_pin_io(False)
			for i in range(0, num_single_ended_pin/2):
				# add single ended pins to left
				d_pin_name = "T" + str(i) + "U" # desired pin name
				pin_l = self.get_pin_io(d_pin_name)#FIXME: change get_pin_io with get_desired_pin
				pin_l.set_direction(LEFT_DIRECTION)
				self.pin_left.append(pin_l)

				# add single ended pins to right
				d_pin_name = "T" + str(num_single_ended_pin - i - 1) + "U" # desired pin name
				pin_r = self.get_pin_io(d_pin_name)
				pin_r.set_direction(RIGHT_DIRECTION)
				self.pin_right.insert(0, pin_r)

				num_pin_assigned_direction += 2

		#right and left pins for MGT and PS_MGT banks that must be differential
		if self.type == XAS_MGT_BANK or self.type == XAS_PSMGT_BANK:
			for index,num_bank in enumerate(self.numbers):
				num_clk_pin = self.get_num_desired_pins(["CLK"], num_bank)/2 # /2 for N,P
				
				# First bank number, pins insert the beginning pin_left, pin_right
				if index == 0:
					for i in range(0, num_clk_pin/2): # /2 for left,right
						# add differential clock pins to left
						d_pin_name = "CLK" + str(i) + "P"
						p_clk = self.get_desired_pin([d_pin_name], num_bank)
						p_clk.set_direction(LEFT_DIRECTION)
						self.pin_left.append(p_clk)

						d_pin_name = "CLK" + str(i) + "N"
						n_clk = self.get_desired_pin([d_pin_name], num_bank)
						n_clk.set_direction(LEFT_DIRECTION)
						self.pin_left.append(n_clk)

						# add differential clock pins to right
						d_pin_name = "CLK" + str(num_clk_pin-i-1) + "P"
						p_clk = self.get_desired_pin([d_pin_name], num_bank)
						p_clk.set_direction(RIGHT_DIRECTION)
						self.pin_right.insert(0, p_clk)

						d_pin_name = "CLK" + str(num_clk_pin-i-1) + "N"
						n_clk = self.get_desired_pin([d_pin_name], num_bank)
						n_clk.set_direction(RIGHT_DIRECTION)
						self.pin_right.insert(0 ,n_clk)

						num_pin_assigned_direction += 4

				num_diff_pin = self.get_num_desired_pins(["RX", "TX"],num_bank)/2 # /2 for N,P
				for i in range(0, num_diff_pin/2): # /2 for RX,TX
					# add differential pins to left
					d_pin_name = "RX" + "P" + str(i) # desired pin name
					p_pin = self.get_desired_pin([d_pin_name], num_bank)
					p_pin.set_direction(LEFT_DIRECTION)
					self.pin_left.append(p_pin)

					d_pin_name = "RX" + "N" + str(i) # desired pin name
					n_pin = self.get_desired_pin([d_pin_name], num_bank)
					n_pin.set_direction(LEFT_DIRECTION)
					self.pin_left.append(n_pin)

					# add differential pins to right
					d_pin_name = "TX" + "P" + str(i) # desired pin name
					p_pin = self.get_desired_pin([d_pin_name], num_bank)
					p_pin.set_direction(RIGHT_DIRECTION)
					self.pin_right.insert(0, p_pin)

					d_pin_name = "TX" + "N" + str(i) # desired pin name
					n_pin = self.get_desired_pin([d_pin_name], num_bank)
					n_pin.set_direction(RIGHT_DIRECTION)
					self.pin_right.insert(0, n_pin)
					
					num_pin_assigned_direction += 4
				
				# Second bank number, pins append to end pin_left, pin_right				
				if index == 1:
					for i in range(0, num_clk_pin/2): # /2 for left,right 
						# add differential clock pins to left
						d_pin_name = "CLK" + str(i) + "P"
						p_clk = self.get_desired_pin([d_pin_name], num_bank)
						p_clk.set_direction(LEFT_DIRECTION)
						self.pin_left.append(p_clk)

						d_pin_name = "CLK" + str(i) + "N"
						n_clk = self.get_desired_pin([d_pin_name], num_bank)
						n_clk.set_direction(LEFT_DIRECTION)
						self.pin_left.append(n_clk)

						# add differential clock pins to right
						d_pin_name = "CLK" + str(num_clk_pin-i-1) + "P"
						p_clk = self.get_desired_pin([d_pin_name], num_bank)
						p_clk.set_direction(RIGHT_DIRECTION)
						self.pin_right.insert(0, p_clk)

						d_pin_name = "CLK" + str(num_clk_pin-i-1) + "N"
						n_clk = self.get_desired_pin([d_pin_name], num_bank)
						n_clk.set_direction(RIGHT_DIRECTION)
						self.pin_right.insert(0, n_clk)

						num_pin_assigned_direction += 4

		#right and left pins for PS banks
		if self.type == XAS_PS_BANK:
			for num_bank in self.numbers:
				num_mio_pins = self.get_num_desired_pins(["PS_MIO"], num_bank)
				start_number = self.get_min_number_mio_pins(num_bank)
				end_number = start_number + num_mio_pins
				for i in range(0, num_mio_pins/2): # /2 for left,right
					# add differential pins to left
					d_pin_name = "MIO" + str(start_number + i) # desired pin name
					l_pin = self.get_desired_pin([d_pin_name], num_bank)
					l_pin.set_direction(LEFT_DIRECTION)
					self.pin_left.append(l_pin)

					# add differential pins to right
					d_pin_name = "MIO" + str(end_number-i-1) # desired pin name
					r_pin = self.get_desired_pin([d_pin_name], num_bank)
					r_pin.set_direction(RIGHT_DIRECTION)
					self.pin_right.insert(0, r_pin)

					num_pin_assigned_direction += 2

		#right and left pins for DDR banks
		if self.type == XAS_DDR_BANK:
			num_ddr_add = self.get_num_ddr_address_pins() # number of ddr address pins
			for i in range(0, num_ddr_add):
				d_pin_name = "PS_DDR_A" + str(i) + "_" 
				add_pin = self.get_desired_pin([d_pin_name], self.numbers[0])#FIXME: bank number
				add_pin.set_direction(LEFT_DIRECTION)
				self.pin_left.append(add_pin)


		# set direction for remind pins
		cnt1 = (len(self.pin_objects) - num_pin_assigned_direction)/2
		for pin in self.pin_objects:
			if(pin.get_direction()==NO_DIRECTION):
				if(cnt1>0):
					pin.set_direction(RIGHT_DIRECTION)
					self.pin_right.insert(0, pin)
					cnt1 -= 1
				else:
					pin.set_direction(LEFT_DIRECTION)
					self.pin_left.append(pin)
					

	def add_pin_to_left(self, pins):
		for pin in pins:
			pin.set_direction(LEFT_DIRECTION)
			self.pin_objects.append(pin)
			self.pin_left.append(pin)

	def add_pin_to_right(self, pins):
		for pin in pins:
			pin.set_direction(RIGHT_DIRECTION)
			self.pin_objects.append(pin)
			self.pin_right.append(pin)

	def add_pin_to_up(self, pins):
		for pin in pins:
			pin.set_direction(UP_DIRECTION)
			self.pin_objects.append(pin)
			self.pin_up.append(pin)

	def add_pin_to_down(self, pins):
		for pin in pins:
			pin.set_direction(DOWN_DIRECTION)
			self.pin_objects.append(pin)
			self.pin_down.append(pin)

	# @num: byte lane number(0,1,2,...)
	# @change_diff_order_pin: change order P-N in return byte lane. (True,False)
	# @return: list of pins inside a byte lane
	#		   and pop from pin_objects
	def get_byte_lane(self, num, change_diff_order_pin):
		pins = []
		# DQ pins
		for i in range(0,8):
			d_pin_name = "DQ" + str(i+num*8)
			pin = self.get_desired_pin_with_pop([d_pin_name], self.numbers[0]) #FIXME: bank number
			pins.append(pin)
		
		# DQS{num}{P-N} pins
		d_pin_name = "DQS_" + "P" + str(num)
		p_pin = self.get_desired_pin_with_pop([d_pin_name], self.numbers[0])#FIXME: bank number
		d_pin_name = "DQS_" + "N" + str(num)
		n_pin = self.get_desired_pin_with_pop([d_pin_name], self.numbers[0])#FIXME: bank number

		if change_diff_order_pin:
			pins.append(n_pin)
			pins.append(p_pin)
		else:
			pins.append(p_pin)
			pins.append(n_pin)

		# DM{num} pin
		d_pin_name = "DM" + str(num)
		pin = self.get_desired_pin_with_pop([d_pin_name], self.numbers[0])#FIXME: bank number
		pins.append(pin)

		return pins
			
	# @num_bank: pin in desired bank number
	# @return: minimum number in mio pins
	def get_min_number_mio_pins(self, num_bank):
		min_number = 4000 # init with big number
		for pin in self.pin_objects:
			if pin.get_bank_number() == num_bank:
				pin_name = pin.get_pin_name()
				split_pin_name = pin_name.split("_")
				for s_pin_name in split_pin_name:
					if "MIO" in s_pin_name:
						number = int(s_pin_name[3:len(s_pin_name)]) # MIO{0-90-9...}
						if number < min_number:
							min_number = number
							break
		return min_number

	# @return: number of ddr address pins
	def get_num_ddr_address_pins(self):
		cnt = 0
		for pin in self.pin_objects:
			pin_name = pin.get_pin_name()
			if "PS_DDR_A" in pin_name:
				split_pin_name = pin_name.split("_")
				add_name = split_pin_name[2] #FIXME: Assume the struct of the pin name for address as "PS_DDR_A{0-9}"
				add_num = add_name[1:len(add_name)]
				if add_num.isdigit():
					cnt += 1
		return cnt

	# @d_pin_name: list of desired pin names
	# @num_bank: pin in desired bank number
	# @return: number of desired pin with d_pin_name in pin_name 
	# 		   and num_bank
	def get_num_desired_pins(self, d_pin_names, num_bank):
		cnt = 0
		for pin in self.pin_objects:
			if any(name in pin.get_pin_name() for name in d_pin_names) and num_bank == pin.get_bank_number():
				cnt += 1
		return cnt

	# @d_pin_name: list of desired pin names
	# @num_bank: pin in desired bank number
	# @return: if find desired pin with d_pin_name and num_bank
	#		   otherwise return None
	def get_desired_pin(self, d_pin_names, num_bank):
		for pin in self.pin_objects:
			if any(name in pin.get_pin_name() for name in d_pin_names) and num_bank == pin.get_bank_number():
				return pin

	# @d_pin_name: list of desired pin names
	# @num_bank: pin in desired bank number
	# @return: if find desired pin with d_pin_name and num_bank
	#		   and pop from pin_objects
	#		   otherwise return None
	def get_desired_pin_with_pop(self, d_pin_names, num_bank):
		cnt = 0
		for index,pin in enumerate(self.pin_objects):
			if any(name in pin.get_pin_name() for name in d_pin_names) and num_bank == pin.get_bank_number():
				return self.pin_objects.pop(index)

	# Note: Call this function if type bank is (HP or HR)
	# @d_pin_name: desired pin name
	# @return: if find desired pin with d_pin_name
	#		   otherwise return None
	def get_pin_io(self, d_pin_name):
		part2_pin_name = d_pin_name

		for pin in self.pin_objects:
			pin_name = pin.get_pin_name()
			split_pin_name = pin_name.split("_")
			io_type = split_pin_name[0]
			# Check type pin is I/O
			if io_type == pin.get_io_type(): # in HR and HP banks, the beginning of their pin names equal with I/O Type
				part2 = split_pin_name[1]
				if part2 == part2_pin_name:
					return pin
	
	# @is_diff: pin is differential or single ended
	# @return: number of io pins in io banks
	def get_num_pin_io(self, is_diff):
		num = 0
		for pin in self.pin_objects:
			pin_name = pin.get_pin_name()
			split_pin_name = pin_name.split("_")
			io_type = split_pin_name[0]
			# Check type pin is I/O
			if io_type == pin.get_io_type(): # in HR and HP banks, the beginning of their pin names equal with I/O Type
				part2_pin_name = split_pin_name[1]
				if is_diff:
					if part2_pin_name[0] == "L":
						num += 1
				else:
					if part2_pin_name[0] == "T":
						num += 1
		return num

	def append_bank_number_to_pin_name(self):
		if self.numbers[0] != "NA":
			for pin in self.pin_objects:
				pin_name = pin.get_pin_name()
				bn = pin_name.split('_')[-1] # get last word from pin_name
				if bn.isdigit() == False or int(bn) not in self.numbers :
					#FIXME: which bank number append to pin name if we have two bank(capacity = 2)
					pin.set_pin_name(pin_name + "_" + str(self.numbers[0])) # assign first bank number to pins

	# add index to pin_name if equals with another pin_name
	def rename_pin_name(self):
		cnt = 1
		for i,pin1 in enumerate(self.pin_objects):
			for j,pin2 in enumerate(self.pin_objects):
				if i!=j and pin1.get_pin_name()==pin2.get_pin_name():
					pin1.set_pin_name(pin1.get_pin_name() + "_" + str(cnt))
					cnt += 1

	def calculate_rect_size(self):
		offset_left = 0
		left_size = 0
		for pin in self.pin_left:
			if(left_size<len(pin.get_pin_name())):
				left_size = len(pin.get_pin_name())
			if any(spn in pin.get_pin_name() for spn in special_pin_names):
				offset_left += 1
			if (pin.get_io_type() + "_T") in pin.get_pin_name():
				offset_left += 1

		offset_right = 0
		right_size = 0
		for pin in self.pin_right:
			if(right_size<len(pin.get_pin_name())):
				right_size = len(pin.get_pin_name())
			if any(spn in pin.get_pin_name() for spn in special_pin_names):
				offset_right += 1
			if (pin.get_io_type() + "_T") in pin.get_pin_name():
				offset_right += 1

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
		height = max(len(self.pin_left),len(self.pin_right)) + (down_size + up_size)/2 + offset_right + offset_left
		return max(width,height)

	def create_xml(self, device_name):

		rect_size = int(self.calculate_rect_size()*10)

		lp = ET.Element(LIB_PART)
		lp.append(ET.Element(DEFN))

		pp = ET.Element('PhysicalPart')
		pp.append(ET.Element(DEFN))

		nv = ET.Element(NORMAL_VIEW)
		defn = ET.Element(DEFN,suffix=".Normal")
		nv.append(defn)

		v_locx = int(rect_size/2 - (len(device_name)/2/2 - 1)*10)
		v_locy = int(rect_size/2)
		pcb_locx = v_locx
		pcb_locy = v_locy + 10
		r_locx = int(rect_size/2)
		r_locy = v_locy - 10

		nv.append(create_xml_symbol_diplay_prop(_locX=r_locx,_locY=r_locy,_name="Part Reference",_dispType=1))
		nv.append(create_xml_symbol_diplay_prop(_locX=v_locx,_locY=v_locy,_name="Value",_dispType=1))
		nv.append(create_xml_symbol_diplay_prop(_locX=pcb_locx,_locY=pcb_locy,_name="PCB Footprint",_dispType=0))
		nv.append(create_xml_symbol_user_prop("PCB Footprint", device_name))
		nv.append(create_xml_symbol_user_prop("Value", device_name))
		nv.append(create_xml_symbol_user_prop("Description", device_name))
		nv.append(create_xml_symbol_user_prop("Name", device_name))
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
		nv.append(create_xml_part_value(device_name))
		nv.append(create_xml_reference("U"))
		nv.append(create_xml_rect(_x1=0,_x2=rect_size,_y1=0,_y2=rect_size))

		for i,pin in enumerate(self.pin_up):
			pin_name = pin.get_pin_name()
			startX = int(rect_size - (rect_size-len(self.pin_up)*10)/2 - 10*(i+1))
			startY = 0
			hotptX = startX
			hotptY = startY - 30
			type_pin = 7
			position = i
			nv.append(create_xml_symbol_pin_scalar(_hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
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
			nv.append(create_xml_symbol_pin_scalar(_hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
												   _startX=startX,_startY=startY,_type=type_pin))
			pp.append(create_xml_pin_number(pin.get_pin(),position))

		offset_right = 0
		for pin in self.pin_right:
			if any(spn in pin.get_pin_name() for spn in special_pin_names):
				offset_right += 1
			if (pin.get_io_type() + "_T") in pin.get_pin_name():
				offset_right += 1

		offset_left = 0
		for pin in self.pin_left:
			if any(spn in pin.get_pin_name() for spn in special_pin_names):
				offset_left += 1
			if (pin.get_io_type() + "_T") in pin.get_pin_name():
				offset_left += 1
		
		offset = min(offset_left, offset_right)

		cnt = len(self.pin_up) + len(self.pin_down)
		for i,pin in enumerate(self.pin_right):
			pin_name = pin.get_pin_name()
			startX = rect_size

			startY = int(rect_size - (rect_size-len(self.pin_right)*10)/2 - 10*(i+1 + offset))
			if any(spn in pin_name for spn in special_pin_names):
				startY += 10
			if (pin.get_io_type() + "_T") in pin_name:
				startY += 10

			hotptX = startX + 30
			hotptY = startY
			type_pin = 1
			position = i + cnt
			nv.append(create_xml_symbol_pin_scalar(_hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
												   _startX=startX,_startY=startY,_type=type_pin))
			pp.append(create_xml_pin_number(pin.get_pin(),position))

		cnt = len(self.pin_up) + len(self.pin_down) + len(self.pin_right)
		for i,pin in enumerate(self.pin_left):
			pin_name = pin.get_pin_name()
			startX = 0

			startY = int((rect_size-len(self.pin_left)*10)/2 + 10*(i - offset))
			if any(spn in pin_name for spn in special_pin_names):
				startY += 10
			if (pin.get_io_type() + "_T") in pin_name:
				startY += 10

			hotptX = startX - 30
			hotptY = startY
			type_pin = 1
			position = i + cnt
			nv.append(create_xml_symbol_pin_scalar(_hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
												   _startX=startX,_startY=startY,_type=type_pin))
			pp.append(create_xml_pin_number(pin.get_pin(),position))
		
		lp.append(nv)
		lp.append(pp)

		return lp

	def __str__(self):
		s = str(self.numbers) + "\n"
		for pin in self.pin_objects:
			s += pin.__str__()
			s += "\n"
		return s


#FIXME: check file if not opened
# file: input source file that opened
def xas_get_device_name(file):
	for line in file:
		if 'Device' in line and 'xc' in line:
			words = line.split(' ')
			for word in words:
				if 'xc' in word:
					return word.strip() # remove whitespace character from leading and trailing of word
	return ""

#FIXME: check file if not opened
# file: input source file that opened		
def xas_get_bank_objects(file):
	header_column = []

	gnd_pins = [] # ground pins
	bankless_mgt_pins = [] # mgt vcc pins
	bankless_ps_mgt_pins = [] # ps mgt vcc pins
	bankless_ddr_pins = [] # DDR vcc pins
	bankless_ps_pins = [] # PS vcc pins

	# 0 Bank number
	pl_config_bank = Bank(XAS_PLCONFIG_BANK, 1) 
	pl_config_bank.add_bank_number(0)
	all_banks = [pl_config_bank]

	for line in file:
		line = line.rstrip()
		# comment or line with only spaces or package name for zynq7000 files
		if '--' in line[0:2] or "Device/Package" in line or line == "":
			continue
		if 'Total Number of Pins' in line:
			total_number_pins = line.split()[-1] # split with space and get last word
			if total_number_pins.isdigit():
				total_number_pins = int(total_number_pins)
			else:
				print("Total Number of Pins is wrong", total_number_pins)
			continue
		if 'Pin' in line[0:3]: # header line
			header_column = xas_split_header(line)
			continue

		words = line.rstrip().split(' ') # this line contains pin information
		words = filter(None, line.split(' ')) # remove empty string

		pin = ""
		pin_name = ""
		bank_number = "NA"
		io_type = ""
		for index,header in enumerate(header_column):
			if header == 'Pin Name':
				pin_name = words[index]
				if 'IO_' in pin_name:
					pin_name = xas_rename_io_pin(pin_name, words, header_column)
			elif header == 'Pin':
				pin = words[index]
			elif header == 'Bank':
				if words[index].isdigit():
					bank_number = int(words[index])
				else:
					bank_number = pin_name.split('_')[-1] # get last word in pin_name
					if bank_number.isdigit():
						bank_number = int(bank_number)
					else:
						bank_number = "NA"
			elif header == "I/O Type":
				io_type = words[index]

		pin_object = PinObject(pin, pin_name, io_type, bank_number)

		pin_is_assigned = False
		for bank in all_banks:
			if any([bank_number in bank.get_bank_numbers()]):
				bank.add_pin(pin_object)
				pin_is_assigned = True
				break

		if pin_is_assigned:
			continue
		else:
			if io_type == "HP" :
				new_bank = Bank(XAS_HP_BANK, 1)
				new_bank.add_bank_number(bank_number)
				new_bank.add_pin(pin_object)
				all_banks.append(new_bank)
			elif io_type == "HR" or io_type == "HD" :
				new_bank = Bank(XAS_HR_BANK, 1)
				new_bank.add_bank_number(bank_number)
				new_bank.add_pin(pin_object)
				all_banks.append(new_bank)
			elif io_type == "PSDDR" : #or "DDR" in pin_name
				new_bank = Bank(XAS_DDR_BANK, 1)
				new_bank.add_bank_number(bank_number)
				new_bank.add_pin(pin_object)
				all_banks.append(new_bank)
			elif io_type == "PSCONFIG":
				new_bank = Bank(XAS_PSCONFIG_BANK, 1)
				new_bank.add_bank_number(bank_number)
				new_bank.add_pin(pin_object)
				all_banks.append(new_bank)
			elif "PSGT" in io_type : #or "PS_MGT" in pin_name
				is_assign_pin = False

				for bank in all_banks:
					if bank.get_type() == XAS_PSMGT_BANK and bank.is_full() == False:
						is_assign_pin = True
						bank.add_bank_number(bank_number)
						bank.add_pin(pin_object)
						break
				
				if is_assign_pin == False:
					new_bank = Bank(XAS_PSMGT_BANK, 2)
					new_bank.add_bank_number(bank_number)
					new_bank.add_pin(pin_object)
					all_banks.append(new_bank)
			elif "GT" in io_type  : #or "MGT" in pin_name
				is_assign_pin = False

				for bank in all_banks:
					if bank.get_type() == XAS_MGT_BANK and bank.is_full() == False:
						is_assign_pin = True
						bank.add_bank_number(bank_number)
						bank.add_pin(pin_object)
						break
				
				if is_assign_pin == False:
					new_bank = Bank(XAS_MGT_BANK, 2)
					new_bank.add_bank_number(bank_number)
					new_bank.add_pin(pin_object)
					all_banks.append(new_bank)
			elif io_type == "PSMIO":# or "PS" in pin_name
				new_bank = Bank(XAS_PS_BANK, 1)
				new_bank.add_bank_number(bank_number)
				new_bank.add_pin(pin_object)
				all_banks.append(new_bank)
			elif io_type == "CONFIG":
				print("PLCONFIG",pin, pin_name, bank_number)
				new_bank = Bank(XAS_PLCONFIG_BANK, 1)
				new_bank.add_bank_number(bank_number)
				new_bank.add_pin(pin_object)
				all_banks.append(new_bank)
			else:
				if "GND" in pin_name:
					gnd_pins.append(pin_object)
				elif "DDR" in pin_name:
					bankless_ddr_pins.append(pin_object)	
				elif "PS_MGT" in pin_name:
					bankless_ps_mgt_pins.append(pin_object)	
				elif "MGT" in pin_name:
					bankless_mgt_pins.append(pin_object)
				elif "PS" in pin_name:
					bankless_ps_pins.append(pin_object)
				else:
					pl_config_bank.add_pin(pin_object)

	# Assign gnd pins to banks
	gnd_in_bank = int(math.ceil(float(len(gnd_pins))/len(all_banks))) # number of gnd pins assigned to specific bank
	for i in range(0, len(gnd_pins)):
		all_banks[i/gnd_in_bank].add_pin(gnd_pins[i])

	mgt_banks = []
	ps_mgt_banks = []
	ddr_banks = []
	ps_banks = []
	for bank in all_banks:
		if bank.get_type() == XAS_MGT_BANK:
			mgt_banks.append(bank)
		elif bank.get_type() == XAS_PSMGT_BANK:
			ps_mgt_banks.append(bank)
		elif bank.get_type() == XAS_DDR_BANK:
			ddr_banks.append(bank)
		elif bank.get_type() == XAS_PS_BANK:
			ps_banks.append(bank)

	# Assign MGTV pins to MGT banks
	if len(mgt_banks) != 0: # Check have MGT banks or not
		mgtv_in_bank = int(math.ceil(float(len(bankless_mgt_pins))/len(mgt_banks))) # number of MGTV pins assigned to MGT bank
		for i in range(0, len(bankless_mgt_pins)):
			mgt_banks[i/mgtv_in_bank].add_pin(bankless_mgt_pins[i])

	# Assign PS_MGTV pins to PS_MGT banks
	if len(ps_mgt_banks) != 0: # Check have PS_MGT banks or not
		ps_mgtv_in_bank = int(math.ceil(float(len(bankless_ps_mgt_pins))/len(ps_mgt_banks))) # number of PS_MGTV pins assigned to MGT bank
		for i in range(0, len(bankless_ps_mgt_pins)):
			ps_mgt_banks[i/ps_mgtv_in_bank].add_pin(bankless_ps_mgt_pins[i])

	# Assign DDRV pins to DDR banks
	if len(ddr_banks) != 0: # Check have DDR banks or not
		ddrv_in_bank = int(math.ceil(float(len(bankless_ddr_pins))/len(ddr_banks))) # number of DDRV pins assigned to DDR bank
		for i in range(0, len(bankless_ddr_pins)):
			ddr_banks[i/ddrv_in_bank].add_pin(bankless_ddr_pins[i])
		
		# Create new DDR bank based on byte lane if number of pins more than 70 
		for bank in ddr_banks:
			if len(bank.get_pin_objects()) > 70:
				pins = []
				data_bank = Bank(XAS_DATA_BANK, 0)
				data_bank.add_bank_number("NA")
				num_byte_lane = bank.get_num_desired_pins(["DQS"], bank.numbers[0])/2 #FIXME: bank number
																					  #/2 for P,N
				byte_lane_in_each_direction = int(num_byte_lane/4)
				for i in range(0,num_byte_lane):
					if i < byte_lane_in_each_direction:
						pins = bank.get_byte_lane(i, change_diff_order_pin = False)
						data_bank.add_pin_to_left(pins)
					elif i< 2*byte_lane_in_each_direction:
						pins = bank.get_byte_lane(i, change_diff_order_pin = False)
						data_bank.add_pin_to_down(pins)
					elif i< 3*byte_lane_in_each_direction:
						pins = bank.get_byte_lane(i, change_diff_order_pin = True)
						data_bank.add_pin_to_right(pins)
					else:
						pins = bank.get_byte_lane(i, change_diff_order_pin = True)
						data_bank.add_pin_to_up(pins)
					
				all_banks.append(data_bank)

	# Assign PSV pins to PS banks
	if len(ps_banks) != 0: # Check have PS banks or not
		psv_in_bank = int(math.ceil(float(len(bankless_ps_pins))/len(ps_banks))) # number of PSV pins assigned to PS bank
		for i in range(0, len(bankless_ps_pins)):
			ps_banks[i/psv_in_bank].add_pin(bankless_ps_pins[i])

	return all_banks, total_number_pins

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

# @all_banks: list of bank
# @return: total number of pins in all_banks
def xas_get_total_pins(all_banks):
	cnt = 0
	for bank in all_banks:
		cnt += len(bank.get_pin_objects())
	return cnt

