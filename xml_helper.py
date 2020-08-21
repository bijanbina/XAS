from lxml import etree as ET
import lxml.builder as builder


PACKAGE = 'Package'
LIB_PART = 'LibPart'
DEFN = 'Defn'
NORMAL_VIEW = 'NormalView'
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

def create_package(device_name):
    defn = ET.Element(DEFN,name=".OLB")
    package = ET.Element(PACKAGE)
    defn = ET.Element(DEFN,alphabeticNumbering="1", isHomogeneous="0", name=str(device_name), pcbFootprint="?", refdesPrefix="U")
    package.append(defn)
    return package

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

def create_xml_symbol_user_prop(_name,value):
    sup = ET.Element(SYMBOL_USER_PROP)
    sup.append(ET.Element(DEFN,name=str(_name),val=str(value)))
    return sup

def create_xml_symbol_b_box(_x1,_x2,_y1,_y2):
    sbb = ET.Element(SYMBOL_B_BOX)
    sbb.append(ET.Element(DEFN,x1=str(_x1),x2=str(_x2),y1=str(_y1),y2=str(_y2)))
    return sbb

def create_xml_symbol_color(color):
    sc = ET.Element(SYMBOL_COLOR)
    sc.append(ET.Element(DEFN,val=str(color)))
    return sc

def create_xml_is_pin_numbers_visible(value):
    ipnv = ET.Element(IS_PIN_NUMBERS_VISIBLE)
    ipnv.append(ET.Element(DEFN,val=str(value)))
    return ipnv

def create_xml_is_pin_names_rotated(value):
    ipnv = ET.Element(IS_PIN_NAMES_ROTATED)
    ipnv.append(ET.Element(DEFN,val=str(value)))
    return ipnv

def create_xml_is_pin_names_visible(value):
    ipnv = ET.Element(IS_PIN_NAMES_VISIBLE)
    ipnv.append(ET.Element(DEFN,val=str(value)))
    return ipnv

def create_xml_contents_lib_name(value):
    ipnv = ET.Element(CONTENTS_LIB_NAME)
    ipnv.append(ET.Element(DEFN,name=str(value)))
    return ipnv

def create_xml_contents_view_name(value):
    ipnv = ET.Element(CONTENTS_VIEW_NAME)
    ipnv.append(ET.Element(DEFN,name=str(value)))
    return ipnv

def create_xml_contents_view_type(value):
    ipnv = ET.Element(CONTENTS_VIEW_TYPE)
    ipnv.append(ET.Element(DEFN,type=str(value)))
    return ipnv

def create_xml_part_value(value):
    ipnv = ET.Element(PART_VALUE)
    ipnv.append(ET.Element(DEFN,name=str(value)))
    return ipnv

def create_xml_reference(value):
    ipnv = ET.Element(REFERENCE)
    ipnv.append(ET.Element(DEFN,name=str(value)))
    return ipnv

def create_xml_rect(_x1,_x2,_y1,_y2):
    rect = ET.Element(RECT)
    rect.append(ET.Element(DEFN,fillStyle="1",hatchStyle="0",lineStyle="0",lineWidth="0",x1=str(_x1),x2=str(_x2),y1=str(_y1),y2=str(_y2)))
    return rect

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

def create_xml_pin_number(_number,_position):
    pn = ET.Element(PIN_NUMBER)
    pn.append(ET.Element(DEFN,number=str(_number),position=str(_position)))
    return pn