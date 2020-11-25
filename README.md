# Xilinx Allegro Symbol Generator
Converts xilinx package pinout file to Orcad library xml files.

You can download package file from [here](https://www.xilinx.com/support/package-pinout-files.html)

## How To Use
1. Install lxml package

```
pip install lxml
```

    
2. Execute following command to generate xml symbol

```
python xml_creator.py [input.txt] [output.xml]
```
    
Example: `xml_creator.py xc7z030sbg485pkg.txt result.xml`

## Parameters

### vcc_name
Name of pins that should be placed in the vcc_bank.

### vcc_bank
The bank id that `vcc_name` should be placed in.

### mgt_name
Name of pins that should be placed in the mgt_bank.

### mgt_bank
The bank id that `mgt_name` should be placed in.

### up_pin_names
Pin that contains this string would be placed on top edge of symbol.

### down_pin_names
Pin that contains this string would be placed on down edge of symbol.
		
### ps_mode
If sets to true merge `ps_banks`.

### ps_banks
Id of banks that should be merge in case of ps_mode is true.
