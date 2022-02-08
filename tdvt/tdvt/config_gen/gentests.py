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
import logging
from typing import Dict

debug = False

def get_logical_config_templates(ds_registry):
    all_templates = template_attributes.copy()

    for ds in ds_registry.dsnames:
        info = ds_registry.get_datasource_info(ds)
        if not info:
            continue
        all_templates.update(info.logical_config)

    return all_templates

def get_logical_config_template(ds_registry, config_name):
    return get_logical_config_templates(ds_registry)[config_name]

def check_logical_config_boolean_attr_value(attrs: Dict, key: str) -> bool:
    if key not in attrs:
        return False
    if attrs[key] is False or attrs[key] == 'False':
        return False
    if attrs[key] is True or attrs[key] == 'True':
        return True

    # For backwards compatibility
    logging.warning("Only True or False are valid for attribute " + key)
    return True

def get_customized_table_name(attributes, base_table):
    table_prefix = ""
    if 'tablePrefix' in attributes:
        table_prefix = attributes['tablePrefix']

    table_name = attributes['tablename']

    t = Template(table_name)
    #These substitution holders are in templates.py.
    if check_logical_config_boolean_attr_value(attributes, 'tablenameUpper'):
        table_name = t.substitute(dsName=base_table.upper())
    else:
        table_name = t.substitute(dsName=base_table)

    if check_logical_config_boolean_attr_value(attributes, 'tablenameLower'):
        table_name = table_name.lower()
    elif 'calcsnameLower' in attributes and 'calcs' in table_name.lower():
        table_name = table_name.lower()
    elif 'staplesnameLower' in attributes and 'staples' in table_name.lower():
        table_name= table_name.lower()

    if 'tablenamePrefix' in attributes:
        table_name = attributes['tablenamePrefix'] + table_name
    if 'tablenamePostfix' in attributes:
        table_name += attributes['tablenamePostfix']

    return table_prefix + '[' + table_name + ']'

def get_new_field_name(field, attrs):
    new_field = field
    if check_logical_config_boolean_attr_value(attrs, 'bool_underscore'):
        m = re.search('\[(bool[0-9])\]', new_field, flags=re.IGNORECASE)
        if m:
            new_field = '[' + m.group(1) + '_]'

    if check_logical_config_boolean_attr_value(attrs, 'fieldnameDate_underscore'):
        m = re.search('\[(.*? date)\]', new_field, flags=re.IGNORECASE)
        if m:
            new_field = '[' + m.group(1) + '_]'

    if check_logical_config_boolean_attr_value(attrs, 'fieldnameLower'):
        new_field = new_field.lower()
    if check_logical_config_boolean_attr_value(attrs, 'fieldnameUpper'):
        new_field = new_field.upper()
    if check_logical_config_boolean_attr_value(attrs, 'fieldnameNoSpace'):
        new_field = new_field.replace(' ', '')
    if check_logical_config_boolean_attr_value(attrs, 'fieldnameLower_underscore'):
        new_field = new_field.lower().replace(' ', '_')
    if check_logical_config_boolean_attr_value(attrs, 'fieldnameUnderscoreNotSpace'):
        new_field = new_field.replace(' ', '_')
    if 'fieldnamePostfix' in attrs:
        m = re.search('\[(.*)\]', new_field, flags=re.IGNORECASE)
        if m:
            new_field = '[' + m.group(1) + attrs['fieldnamePostfix'] + ']'

    return new_field

def get_field_name_map(fields, attrs):
    m = {}
    for f in fields:
        m[f] = get_new_field_name(f, attrs)
    return m

def get_modified_line(line, attrs, fields, field_name_map):
    new_line = line
    if 'test name' in line:
         return new_line
    if 'query-function' in line:
        return new_line
    if 'runquery-column' in line:
        return new_line

    for field in fields:
        new_line = new_line.replace(field, field_name_map[field])

    calcs_table_name = get_customized_table_name(attrs, 'Calcs')
    staples_table_name = get_customized_table_name(attrs, 'Staples')
    new_line = new_line.replace('$Calcs$', calcs_table_name)
    new_line = new_line.replace('$Staples$', staples_table_name)
    return new_line

def process_test_file( filename, output_dir, staples_fields, calcs_fields, ds_registry ):
    if debug: print ("Processing " + filename )

    input_file = open(filename, 'r', encoding='utf-8')
    base_name = os.path.basename(filename)
    if debug: print("base_name " + base_name)
    match = re.search('setup\.(.*)\.xml', base_name)
    if match:
        test_name = match.group(1)
    else:
        test_name = os.path.splitext(base_name)[0]

    if debug: print ("Test " + test_name)


    fields = staples_fields + calcs_fields

    ds_file_map = {}
    for ds in get_logical_config_templates(ds_registry):
        setup_file = open( os.path.join( output_dir, 'setup.' + test_name + '.' + ds + '.xml'), 'w', encoding='utf-8' )
        field_name_map = get_field_name_map(fields,  get_logical_config_template(ds_registry, ds))
        ds_file_map[ds] = (setup_file, field_name_map)

    #Go through all the configurations in templates.py and generate logical configs for them.
    for line in input_file:
        for ds in ds_file_map:
            new_line = get_modified_line(line, get_logical_config_template(ds_registry, ds), fields, ds_file_map[ds][1])
            ds_file_map[ds][0].write( new_line )

    for ds in ds_file_map:
        ds_file_map[ds][0].close()

    input_file.close()

    #Go through all the ini files and see if any of them define a logical config. Generate test files for those.


def process_text(ds, text, attributes, fields, field_map):
    new_text = ''
    for line in text:
        new_line = get_modified_line(line, attributes, fields, field_map)
        new_line = new_line.replace('$Name$', ds)
        new_text += new_line + '\n'
    return new_text

def get_config_text(config_name, config_attributes, fields, config_field_map):
    configs = []
    sample_text = [ 'Name = $Name$', 'Calcs = $Calcs$', 'Staples = $Staples$', 'Camel Case = ' + fields[0], 'bool0 = ' + fields[1], 'Date = ' + fields[2] ]

    cfg = process_text(config_name, sample_text, config_attributes, fields, config_field_map)
    configs.append(cfg)
    return configs

def list_config(ds_registry, config_name):
    return list_configs(ds_registry, config_name)

def list_configs(ds_registry, target_config_name=None):
    configs = []

    fields = ['[Camel Case]', '[bool0]', '[Date]']
    cfgs = get_logical_config_templates(ds_registry)
    for config_name in sorted(cfgs.keys(), key=str.lower):
        if target_config_name and config_name != target_config_name:
            continue
        cfg_template = get_logical_config_template(ds_registry, config_name)
        field_name_map = get_field_name_map(fields,  cfg_template)
        configs += get_config_text(config_name, cfg_template, fields, field_name_map)
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

def generate_logical_files(input_dir, output_dir, ds_registry, force=False):
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
                print ("Generating test files from: " + str(input_dir))
                print ("Writing test files to: " + str(output_dir))
                clean_create_dir(output_dir)
                for input_root, input_dirs, input_files in os.walk(input_dir):
                    for input_filename in input_files:
                        process_test_file( os.path.join(input_root, input_filename), output_dir, staples_fields, calcs_fields, ds_registry )

