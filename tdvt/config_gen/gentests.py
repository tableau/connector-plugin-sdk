"""
    Generate datasource specific logical query files based on a set of genericized input files.
"""

import sys
import os
import shutil
import argparse
from .templates import *
from string import Template
import re
import glob
from ..resources import *

debug = False

def get_customized_table_name(attributes, base_table):
    table_prefix = ""
    if 'tablePrefix' in attributes:
        table_prefix = attributes['tablePrefix']

    table_name = attributes['tablename']

    t = Template('[' + table_name + ']')
    #These substitution holders are in templates.py.
    if 'tablenameUpper' in attributes:
        table_name = t.substitute(dsName=base_table.upper())
    else:
        table_name = t.substitute(dsName=base_table)

    if 'tablenameLower' in attributes:
        table_name = table_name.lower()

    
    return table_prefix + table_name

def get_new_field_name(field, attrs):
    new_field = field
    if 'bool_underscore' in attrs:
        m = re.search('\[(bool[0-9])\]', new_field)
        if m:
            new_field = '[' + m.group(1) + '_]'
    if 'fieldnameLower' in attrs:
        new_field = new_field.lower()        
    if 'fieldnameNoSpace' in attrs:
        new_field = new_field.replace(' ', '')
    if 'fieldnameLower_underscore' in attrs:
        new_field = new_field.lower().replace(' ', '_')
    if 'fieldnameDate_underscore' in attrs:
            if 'date]' in new_field:
                new_field = new_field.replace('date]', 'date_]')
            elif 'Date]' in new_field:
                new_field = new_field.replace('Date]', 'Date_]')

    return new_field

def get_modified_line(line, attrs, fields):
    new_line = line
    if 'test name' in line:
         return new_line
    if 'query-function' in line:
        return new_line
    if 'runquery-column' in line:
        return new_line

    for field in fields:
        new_field = get_new_field_name(field, attrs)
        new_line = new_line.replace(field, new_field)

    calcs_table_name = get_customized_table_name(attrs, 'Calcs')
    staples_table_name = get_customized_table_name(attrs, 'Staples')
    new_line = new_line.replace('$Calcs$', calcs_table_name)
    new_line = new_line.replace('$Staples$', staples_table_name)
    return new_line

def process_test_file( filename, output_dir, staples_fields, calcs_fields ):
    if debug: print ("Processing " + filename )
    for ds in attributes:
        input_file = open(filename, 'r', encoding='utf-8')
        base_name = os.path.basename(filename)
        if debug: print("base_name " + base_name)
        match = re.search('setup\.(.*)\.xml', base_name)
        if match:
            test_name = match.group(1)
        else:
            test_name = os.path.splitext(base_name)[0]

        if debug: print ("Test " + test_name)

        setup_file = open( os.path.join( output_dir, 'setup.' + test_name + '.' + ds + '.xml'), 'w', encoding='utf-8' )

        fields = staples_fields + calcs_fields
        for line in input_file:
            new_line = get_modified_line(line, attributes[ds], fields)
            setup_file.write( new_line )

        setup_file.close()
        input_file.close()

def process_text(ds, text, attributes, fields):
    new_text = ''
    for line in text:
        new_line = get_modified_line(line, attributes, fields)
        new_line = new_line.replace('$Name$', ds)
        new_text += new_line + '\n'
    return new_text

def list_configs():
    configs = []
    fields = ['[Camel Case]', '[bool0]', '[Date]']
    sample_text = [ 'Name = $Name$', 'Calcs = $Calcs$', 'Staples = $Staples$', 'Camel Case = ' + fields[0], 'bool0 = ' + fields[1], 'Date = ' + fields[2] ]

    for ds in sorted(attributes.keys(), key=str.lower):
        cfg = process_text(ds, sample_text, attributes[ds], fields)
        configs.append(cfg)
    return configs

def clean_create_dir(new_dir):
    try:
        shutil.rmtree(new_dir, True)
        create_dir(new_dir)
    except OSError:
        return

def create_dir(new_dir):
    #Make the output dir if needed, otherwise continue on our way since its there.
    try:
        os.makedirs(new_dir)
    except OSError:
        return

def generate_logical_files(input_dir, output_dir, force=False):
    base_output_dir = output_dir
    create_dir(base_output_dir)

    calcs_fields = []
    calcs_fields.append('[key]'         )
    calcs_fields.append('[num0]'        )
    calcs_fields.append('[num1]'        )
    calcs_fields.append('[num2]'        )
    calcs_fields.append('[num3]'        )
    calcs_fields.append('[num4]'        )
    calcs_fields.append('[str0]'        )
    calcs_fields.append('[str1]'        )
    calcs_fields.append('[str2]'        )
    calcs_fields.append('[str3]'        )
    calcs_fields.append('[int0]'        )
    calcs_fields.append('[int1]'        )
    calcs_fields.append('[int2]'        )
    calcs_fields.append('[int3]'        )
    calcs_fields.append('[bool0]'       )
    calcs_fields.append('[bool1]'       )
    calcs_fields.append('[bool2]'       )
    calcs_fields.append('[bool3]'       )
    calcs_fields.append('[bool0_]'      )
    calcs_fields.append('[bool1_]'      )
    calcs_fields.append('[bool2_]'      )
    calcs_fields.append('[bool3_]'      )
    calcs_fields.append('[date0]'       )
    calcs_fields.append('[date1]'       )
    calcs_fields.append('[date2]'       )
    calcs_fields.append('[date3]'       )
    calcs_fields.append('[time0]'       )
    calcs_fields.append('[time1]'       )
    calcs_fields.append('[datetime0]'   )
    calcs_fields.append('[datetime1]'   )
    calcs_fields.append('[zzz]'         )

    staples_fields = []
    staples_fields.append('[Item Count]'               )
    staples_fields.append('[Ship Priority]'            )
    staples_fields.append('[Order Priority]'           )
    staples_fields.append('[Order Status]'             )
    staples_fields.append('[Order Quantity]'           )
    staples_fields.append('[Sales Total]'              )
    staples_fields.append('[Discount]'                 )
    staples_fields.append('[Tax Rate]'                 )
    staples_fields.append('[Ship Mode]'                )
    staples_fields.append('[Fill Time]'                )
    staples_fields.append('[Gross Profit]'             )
    staples_fields.append('[Price]'                    )
    staples_fields.append('[Ship Handle Cost]'         )
    staples_fields.append('[Employee Name]'            )
    staples_fields.append('[Employee Dept]'            )
    staples_fields.append('[Manager Name]'             )
    staples_fields.append('[Employee Yrs Exp]'         )
    staples_fields.append('[Employee Salary]'          )
    staples_fields.append('[Customer Name]'            )
    staples_fields.append('[Customer State]'           )
    staples_fields.append('[Call Center Region]'       )
    staples_fields.append('[Customer Balance]'         )
    staples_fields.append('[Customer Segment]'         )
    staples_fields.append('[Prod Type1]'               )
    staples_fields.append('[Prod Type2]'               )
    staples_fields.append('[Prod Type3]'               )
    staples_fields.append('[Prod Type4]'               )
    staples_fields.append('[Product Name]'             )
    staples_fields.append('[Product Container]'        )
    staples_fields.append('[Ship Promo]'               )
    staples_fields.append('[Supplier Name]'            )
    staples_fields.append('[Supplier Balance]'         )
    staples_fields.append('[Supplier Region]'          )
    staples_fields.append('[Supplier State]'           )
    staples_fields.append('[Order ID]'                 )
    staples_fields.append('[Order Year]'               )
    staples_fields.append('[Order Month]'              )
    staples_fields.append('[Order Day]'                )
    staples_fields.append('[Order Date]'               )
    staples_fields.append('[Order Quarter]'            )
    staples_fields.append('[Product Base Margin]'      )
    staples_fields.append('[Product ID]'               )
    staples_fields.append('[Receive Time]'             )
    staples_fields.append('[Received Date]'            )
    staples_fields.append('[Ship Date]'                )
    staples_fields.append('[Ship Charge]'              )
    staples_fields.append('[Total Cycle Time]'         )
    staples_fields.append('[Product In Stock]'         )
    staples_fields.append('[PID]'                      )
    staples_fields.append('[Market Segment]'           )

    #Go through input and top level subdirs. Create those in the output and then process the files.
    for root, dirs, files in os.walk(input_dir):
        for name in dirs:
            input_dir = os.path.join(root, name)
            output_dir = os.path.join(base_output_dir, name)
            any_test_files = glob.glob(os.path.join(output_dir, 'setup*xml'))
            if not any_test_files or force:
                print (input_dir)
                print (output_dir)
                clean_create_dir(output_dir)
                for input_root, input_dirs, input_files in os.walk(input_dir):
                    for input_filename in input_files:
                        process_test_file( os.path.join(input_root, input_filename), output_dir, staples_fields, calcs_fields )

