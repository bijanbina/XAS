# Xilinx Allegro Symbol Generator
Converts xilinx package pin out file to orcad library symbols.

You can download package file [here](https://www.xilinx.com/support/package-pinout-files.html)

## How To Use
1. First run below command for installation lxml package

```
pip install lxml
```

    
2. Run code with source_file[.xml] and output_file[.txt]

```
python xml_creator.py [source_file] [output_file]
```
    
Example: `xml_creator.py xc7z030sbg485pkg.txt result.xml`

## Parameters
The code offer following options:

### vcc_name
Name of pins that should be place in the vcc_bank.

### vcc_bank
The bank id that `vcc_name` should be placed in.

### mgt_name
Name of pins that should be place in the mgt_bank.

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
