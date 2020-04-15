import math
from lxml import etree as ET
import lxml.builder as builder
import os
import sys

#vcc names that wants them to be in a specific bank(vcc_bank)
vcc_name = ["VCCINT","VCCBRAM","VCCAUX","VCCPAUX","VCCPINT","VCCPLL"]
vcc_bank = 0

#mgt names that wants them to be in a specific bank(mgt_bank)
mgt_name = ["MGTAVCC","MGTAVTT"]
mgt_bank = 112

#The pins that contain this name and you want to be at the top of the schematic
up_pin_names = ["VCC"]
#The pins that contain this name and you want to be at the down of the schematic
down_pin_names = ["GND"]

ps_mode = True
ps_banks = [500,501]


PACKAGE = 'Package'
LIB_PART = 'LibPart'
DEFN = 'Defn'
NORMAL_VIEW = 'NormalView'
PHYSICAL_PART = 'PhysicalPart'
SYMBOL_DISPLAY_PROP = 'SymbolDisplayProp'
SYMBOL_USER_PROP = 'SymbolUserProp'
SYMBOL_COLOR = 'SymbolColor'
SYMBOL_B_BOX = 'SymbolBBox'
IS_PIN_NUMBERS_VISIBLE = 'IsPinNumbersVisible'
IS_PIN_NAMES_ROTATED = 'IsPinNamesRotated'
IS_PIN_NAMES_VISIBLE = 'IsPinNamesVisible'
CONTENTS_LIB_NAME = 'ContentsLibName'
CONTENTS_VIEW_NAME = 'ContentsLibName'
CONTENTS_VIEW_TYPE = 'ContentsViewType'
PART_VALUE = 'PartValue'
REFERENCE = 'Reference'
RECT = 'Rect'
SYMBOL_PIN_SCALAR = 'SymbolPinScalar'
PIN_NUMBER = 'PinNumber'
PHYSICAL_PART = 'PhysicalPart'

NO_DIRECTION = -1
DOWN_DIRECTION = 0
UP_DIRECTION = 1
LEFT_DIRECTION = 2
RIGHT_DIRECTION = 3


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

    def get_id(self):
        return self.id

    def set_id(self,id):
        self.id = id

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
        for pin in self.pin_right:
            if(up_size<len(pin.get_pin_name())):
                up_size = len(pin.get_pin_name())
        
        down_size = 0
        for pin in self.pin_right:
            if(down_size<len(pin.get_pin_name())):
                down_size = len(pin.get_pin_name())

        # print(max(len(self.pin_down,self.pin_up))
        width = max(len(self.pin_down),len(self.pin_up)) + (right_size + left_size)/2
        height = max(len(self.pin_left),len(self.pin_right)) + (down_size + up_size)/2
        return max(width,height)

    def create_xml(self):

        rect_size = self.calculate_rect_size()*10

        lp = ET.Element(LIB_PART)
        lp.append(ET.Element(DEFN))

        pp = ET.Element(PHYSICAL_PART)
        pp.append(ET.Element(DEFN))

        nv = ET.Element(NORMAL_VIEW)
        defn = ET.Element(DEFN,suffix=".Normal")
        nv.append(defn)

        v_locx = rect_size/2 - (len(self.device_name)/2/2 - 1)*10
        v_locy = rect_size/2
        pcb_locx = v_locx
        pcb_locy = v_locy + 10
        r_locx = rect_size/2
        r_locy = v_locy - 10

        nv.append(XmlHelper.create_xml_symbol_diplay_prop(_locX=r_locx,_locY=r_locy,_name="Part Reference",_dispType=1))
        nv.append(XmlHelper.create_xml_symbol_diplay_prop(_locX=v_locx,_locY=v_locy,_name="Value",_dispType=1))
        nv.append(XmlHelper.create_xml_symbol_diplay_prop(_locX=pcb_locx,_locY=pcb_locy,_name="PCB Footprint",_dispType=0))
        nv.append(XmlHelper.create_xml_symbol_user_prop("PCB Footprint",self.device_name))
        nv.append(XmlHelper.create_xml_symbol_user_prop("Value",self.device_name))
        nv.append(XmlHelper.create_xml_symbol_user_prop("Description",self.device_name))
        nv.append(XmlHelper.create_xml_symbol_user_prop("Name",self.device_name))
        nv.append(XmlHelper.create_xml_symbol_user_prop("SPLIT_INST","TRUE"))
        nv.append(XmlHelper.create_xml_symbol_user_prop("SWAP_INFO","(S1+S2+S3+S4+S5+S6+S7)"))
        nv.append(XmlHelper.create_xml_symbol_color(48))
        nv.append(XmlHelper.create_xml_symbol_b_box(_x1=0,_x2=rect_size,_y1=0,_y2=rect_size))
        nv.append(XmlHelper.create_xml_is_pin_numbers_visible(1))
        nv.append(XmlHelper.create_xml_is_pin_names_rotated(1))
        nv.append(XmlHelper.create_xml_is_pin_names_visible(1))
        nv.append(XmlHelper.create_xml_contents_lib_name(""))
        nv.append(XmlHelper.create_xml_contents_view_name(""))
        nv.append(XmlHelper.create_xml_contents_view_type(0))
        nv.append(XmlHelper.create_xml_part_value(self.device_name))
        nv.append(XmlHelper.create_xml_reference("U"))
        nv.append(XmlHelper.create_xml_rect(_x1=0,_x2=rect_size,_y1=0,_y2=rect_size))

        for i,pin in enumerate(self.pin_up):
            pin_name = pin.get_pin_name()
            startX = (rect_size-len(self.pin_up)*10)/2 + 10*(i+1)
            startY = 0
            hotptX = startX
            hotptY = startY - 30
            type_pin = 7
            position = i
            nv.append(XmlHelper.create_xml_symbol_pin_scalar(   _hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
                                                                _startX=startX,_startY=startY,_type=type_pin))
            pp.append(XmlHelper.create_xml_pin_number(pin.get_pin(),position))
        
        cnt = len(self.pin_up)
        for i,pin in enumerate(self.pin_down):
            pin_name = pin.get_pin_name()
            startX = (rect_size-len(self.pin_down)*10)/2 + 10*(i+1)
            startY = rect_size
            hotptX = startX
            hotptY = startY + 30
            type_pin = 7
            position = i + cnt
            nv.append(XmlHelper.create_xml_symbol_pin_scalar(   _hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
                                                                _startX=startX,_startY=startY,_type=type_pin))
            pp.append(XmlHelper.create_xml_pin_number(pin.get_pin(),position))

        cnt = len(self.pin_up) + len(self.pin_down)
        for i,pin in enumerate(self.pin_right):
            pin_name = pin.get_pin_name()
            startX = rect_size
            startY = (rect_size-len(self.pin_right)*10)/2 + 10*(i+1)
            hotptX = startX + 30
            hotptY = startY
            type_pin = 1
            position = i + cnt
            nv.append(XmlHelper.create_xml_symbol_pin_scalar(   _hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
                                                                _startX=startX,_startY=startY,_type=type_pin))
            pp.append(XmlHelper.create_xml_pin_number(pin.get_pin(),position))

        cnt = len(self.pin_up) + len(self.pin_down) + len(self.pin_right)
        for i,pin in enumerate(self.pin_left):
            pin_name = pin.get_pin_name()
            startX = 0
            startY = (rect_size-len(self.pin_left)*10)/2 + 10*(i+1)
            hotptX = startX - 30
            hotptY = startY
            type_pin = 1
            position = i + cnt
            nv.append(XmlHelper.create_xml_symbol_pin_scalar(   _hotptX=hotptX,_hotptY=hotptY,_name=pin_name,_position=position,
                                                                _startX=startX,_startY=startY,_type=type_pin))
            pp.append(XmlHelper.create_xml_pin_number(pin.get_pin(),position))
        
        lp.append(nv)
        lp.append(pp)

        return lp

    def __str__(self):
        s = str(self.id) + "\n"
        for pin in self.pin_objects:
            s += pin.__str__()
            s += "\n"
        return s


class XmlHelper():

    @staticmethod
    def create_package(device_name):
        defn = ET.Element(DEFN,name=".OLB")
        package = ET.Element(PACKAGE)
        defn = ET.Element(DEFN,alphabeticNumbering="1", isHomogeneous="0", name=str(device_name), pcbFootprint="?", refdesPrefix="U")
        package.append(defn)
        return package

    @staticmethod
    def create_xml_symbol_diplay_prop(_locX,_locY,_name,_dispType):
        sdp = ET.Element(SYMBOL_DISPLAY_PROP)
        sdp.append(ET.Element(DEFN,locX=str(_locX),locY=str(_locY),name=str(_name),rotation=str(0)))

        pf = ET.Element("PropFont")
        pf.append(ET.Element(DEFN,escapement="0",height="7",italic="0",name="Arial",orientation="0",weight="400",width="4"))
        sdp.append(pf)

        pc = ET.Element("PropColor")
        pc.append(ET.Element(DEFN,val="48"))
        sdp.append(pc)

        pdt = ET.Element("PropDispType")
        pdt.append(ET.Element(DEFN,val=str(_dispType)))
        sdp.append(pdt)

        return sdp

    @staticmethod
    def create_xml_symbol_user_prop(_name,value):
        sup = ET.Element(SYMBOL_USER_PROP)
        sup.append(ET.Element(DEFN,name=str(_name),val=str(value)))
        return sup

    @staticmethod
    def create_xml_symbol_b_box(_x1,_x2,_y1,_y2):
        sbb = ET.Element(SYMBOL_B_BOX)
        sbb.append(ET.Element(DEFN,x1=str(_x1),x2=str(_x2),y1=str(_y1),y2=str(_y2)))
        return sbb

    @staticmethod
    def create_xml_symbol_color(color):
        sc = ET.Element(SYMBOL_COLOR)
        sc.append(ET.Element(DEFN,val=str(color)))
        return sc

    @staticmethod
    def create_xml_is_pin_numbers_visible(value):
        ipnv = ET.Element(IS_PIN_NUMBERS_VISIBLE)
        ipnv.append(ET.Element(DEFN,val=str(value)))
        return ipnv

    @staticmethod
    def create_xml_is_pin_names_rotated(value):
        ipnv = ET.Element(IS_PIN_NAMES_ROTATED)
        ipnv.append(ET.Element(DEFN,val=str(value)))
        return ipnv

    @staticmethod
    def create_xml_is_pin_names_visible(value):
        ipnv = ET.Element(IS_PIN_NAMES_VISIBLE)
        ipnv.append(ET.Element(DEFN,val=str(value)))
        return ipnv

    @staticmethod
    def create_xml_contents_lib_name(value):
        ipnv = ET.Element(CONTENTS_LIB_NAME)
        ipnv.append(ET.Element(DEFN,name=str(value)))
        return ipnv

    @staticmethod
    def create_xml_contents_view_name(value):
        ipnv = ET.Element(CONTENTS_VIEW_NAME)
        ipnv.append(ET.Element(DEFN,name=str(value)))
        return ipnv

    @staticmethod
    def create_xml_contents_view_type(value):
        ipnv = ET.Element(CONTENTS_VIEW_TYPE)
        ipnv.append(ET.Element(DEFN,type=str(value)))
        return ipnv

    @staticmethod
    def create_xml_part_value(value):
        ipnv = ET.Element(PART_VALUE)
        ipnv.append(ET.Element(DEFN,name=str(value)))
        return ipnv

    @staticmethod
    def create_xml_reference(value):
        ipnv = ET.Element(REFERENCE)
        ipnv.append(ET.Element(DEFN,name=str(value)))
        return ipnv

    @staticmethod
    def create_xml_rect(_x1,_x2,_y1,_y2):
        rect = ET.Element(RECT)
        rect.append(ET.Element(DEFN,fillStyle="1",hatchStyle="0",lineStyle="0",lineWidth="0",x1=str(_x1),x2=str(_x2),y1=str(_y1),y2=str(_y2)))
        return rect

    @staticmethod
    def create_xml_symbol_pin_scalar(_hotptX,_hotptY,_name,_position,_startX,_startY,_type):
        sps = ET.Element(SYMBOL_PIN_SCALAR)
        sps.append( ET.Element(DEFN,hotptX=str(_hotptX),hotptY=str(_hotptY),name=str(_name),
                    position=str(_position),startX=str(_startX),startY=str(_startY),type=str(_type),visible="1"))

        il = ET.Element("IsLong")
        il.append(ET.Element(DEFN,val="1"))
        sps.append(il)

        ic = ET.Element("IsClock")
        ic.append(ET.Element(DEFN,val="0"))
        sps.append(ic)

        id = ET.Element("IsDot")
        id.append(ET.Element(DEFN,val="0"))
        sps.append(id)

        ilp = ET.Element("IsLeftPointing")
        ilp.append(ET.Element(DEFN,val="0"))
        sps.append(ilp)

        irp = ET.Element("IsRightPointing")
        irp.append(ET.Element(DEFN,val="0"))
        sps.append(ilp)

        ins = ET.Element("IsNetStyle")
        ins.append(ET.Element(DEFN,val="0"))
        sps.append(ins)

        inc = ET.Element("IsNoConnect")
        inc.append(ET.Element(DEFN,val="0"))
        sps.append(inc)

        ig = ET.Element("IsGlobal")
        ig.append(ET.Element(DEFN,val="0"))
        sps.append(ig)

        inv = ET.Element("IsNumberVisible")
        inv.append(ET.Element(DEFN,val="1"))
        sps.append(inv)

        return sps

    @staticmethod
    def create_xml_pin_number(_number,_position):
        pn = ET.Element(PIN_NUMBER)
        pn.append(ET.Element(DEFN,number=str(_number),position=str(_position)))
        return pn


def get_device_name_and_pin_objects():
    f = open(SOURCE_FILE)
    line = f.next()
    device_name = line.split()[1]
    line = f.next() # '/n'
    line = f.next() # header
    all_pins = []
    for line in f:
        words = line.split()
        if(len(words)>7):
            pin = words[0]
            pin_name = words[1]
            bank = words[3]
            all_pins.append(PinObject(pin,pin_name,bank))
    f.close()
    return device_name,all_pins

# add index to pin_name if equals with another pin_name
def rename_all_pins(all_pins):
    cnt = 0
    for i,pin1 in enumerate(all_pins):
        for j,pin2 in enumerate(all_pins):
            if i!=j and pin1.get_pin_name()==pin2.get_pin_name():
                pin1.set_pin_name(pin1.get_pin_name() + "_" + str(cnt))
                cnt += 1

def get_banks(all_pins):
    banks = set()
    for pin in all_pins:
        if(pin.get_bank()!="NA"):
            banks.add(pin.get_bank())
    return list(banks)

def assign_bank_to_gnds(all_pins):
    banks = get_banks(all_pins)
    num_of_gnd = 0
    for pin in all_pins:
        if "GND" in pin.get_pin_name():
            num_of_gnd += 1

    gnd_in_bank = math.ceil(float(num_of_gnd)/len(banks))
    index = 0
    cnt = 0
    for pin in all_pins:
        if "GND" in pin.get_pin_name():
            pin.set_bank(banks[index])
            cnt += 1
            if(cnt == gnd_in_bank):
                cnt = 0
                index += 1

def assign_bank_to_vcc(all_pins):
    for pin in all_pins:
        pin_name = pin.get_pin_name()
        for vccn in vcc_name:
            if vccn in pin_name:
                pin.set_bank(vcc_bank)

def assign_bank_to_mgt(all_pins):
    mgt_bank = 0
    # get mgt bank
    for pin in all_pins:
        pin_name = pin.get_pin_name()
        if "MGT" in pin_name:
            if (pin.get_bank() != "NA" ):
                mgt_bank = pin.get_bank()
                break

    for pin in all_pins:
        pin_name = pin.get_pin_name()
        for mgtn in mgt_name:
            if mgtn in pin_name:
                pin.set_bank(mgt_bank)

def create_banks(all_pins,device_name):
    banks = get_banks(all_pins)
    all_banks = []
    for i,bankNumber in enumerate(banks):
        all_banks.append(Bank(bankNumber,device_name))

    for pin in all_pins:
        pin_bank = pin.get_bank()
        for bnk in all_banks:
            if( pin_bank==bnk.get_id() ):
                bnk.add_pin(pin)
                break
    for bank in all_banks:
        bank.set_up_down_left_right_pins()

    return all_banks

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
    package = XmlHelper.create_package(device_name)
    n_all_banks = []
    if ps_mode:
        n_all_banks = update_bank_for_ps_mode(all_banks)
    else:
        n_all_banks = all_banks
    for bank in n_all_banks:
        package.append(bank.create_xml())

    f = open(OUTPUT_FILE,'w')
    f.write(ET.tostring(package,pretty_print=True))
    f.close()

def print_pins(all_pins):
    for pin in all_pins:
        print(pin)
        # if(pin.get_bank()=="NA"):
        #     print(pin)

def print_banks(all_banks):
    for bank in all_banks:
        print(bank)

SOURCE_FILE = '/home/bijan/Projects/Builder/XC7Z030-SBG485/xc7z030sbg485pkg.txt'
OUTPUT_FILE = '/home/bijan/Projects/Builder/Pythons/result.xml'

SOURCE_FILE = sys.argv[1]
OUTPUT_FILE = '/home/bijan/Projects/Builder/Pythons/temp.xml'
RESULT_FILE = sys.argv[2]

device_name,all_pins = get_device_name_and_pin_objects()
rename_all_pins(all_pins)
assign_bank_to_gnds(all_pins)
assign_bank_to_vcc(all_pins)
assign_bank_to_mgt(all_pins)
all_banks = create_banks(all_pins,device_name)
create_output_file(device_name,all_banks)
os.system("./script.sh " + RESULT_FILE)