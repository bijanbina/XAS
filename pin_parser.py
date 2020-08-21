import math
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

#FIXME: check file if not opened
# file: input source file that open
def get_device_name(file):
	for line in file:
		if 'Device' in line and 'xc' in line:
			words = line.split(' ')
			for word in words:
				if 'xc' in word:
					return word.strip() # remove whitespace character from leading and trailing of word
	return ""

#FIXME: check file if not opened
# file: input source file that open
def get_pin_objects(file):
	header_column = []
	all_pins = []
	for line in file:
		#FIXME: check '\n' in empty line
		if '--' in line[0:2] or '     ' in line[0:5]: # comment or line with only spaces
			print(line)
			continue
		if 'Total Number of Pins' in line:
			total_number_pins = line.split(' ')[-1]
			continue
		if 'Pin' in line[0:3]: # header line
			header_column = xas_split_header(line)
			continue

		words = line.split(' ')
		pin_name = ""
		pin = ""
		bank = ""
		for index,header in enumerate(header_column):
			if header == 'Pin Name':
				pin_name = words[index]
			elif header == 'Pin':
				pin = words[index]
			elif header == 'Bank':
				bank = words[index]
		
		all_pins.append(PinObject(pin,pin_name,bank))
		
def xas_split_header(line):
	words = line.split('  ')
	columns = []
	for word in words:
		if word != '': # check string is not empty
			columns.append(word.strip("\r\n ")) # remove any '\r' , '\n' , ' ' from leading and trailing of word
	return columns
