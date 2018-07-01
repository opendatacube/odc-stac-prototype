#!/usr/bin/env python
# Created on: 30 June, 2018 by Dr. Arapauat V. Sivaprasad
# Last Modified on: 01 July, 2018 by Dr. Arapauat V. Sivaprasad
# Copyright (c) 2018, Geoscience Australia and Dr. Arapauat V. Sivaprasad
# Licence: GPL-3.0
# ------------------------------------------------------------------------------
'''
DESCRIPTION:
This program creates STAC catalog JSONs for the GeoTIFFs in the DEA Data Staging area.

This is a parallelised version of 'parse_direct.py' and gives ~20X speed improvement
over the serial program. However, this may not be suitable for the cron jobs if they
run on shared servers. You must start an interactive queue on Raijin (qsub -I) to run this.

Though it will auto detect the VDI and Raijin login nodes and exit,
there is no check for other hostnames. Therefore, running this on other hosts may
cause high load on the server and you may upset other users. So, be careful!

HOW:
    - Run as part of the cron job that creates and uploads GeoTIFFs from NetCDF.

PROGRAM FLOW:
1. Takes the base_url, input_dir, subset and output_dir specified in a YAML file or on commandline.

2. Takes the following files from input_dir/subset/item/:
    - bounds.geojson
    - ARD-METADATA.yaml

3. Parses the above files to create the 'output_dir/subset/item/STAC.json'
    
'''
# ------------------------------------------------------------------------------
import click
import os
import yaml
import json
import multiprocessing
import time
from multiprocessing import Pool
from subprocess import Popen, PIPE
import socket
import sys
hostname = socket.gethostname()
if (('vdi' in hostname) or ('raijin' in hostname)):
    print ("It is not safe to run the parallel program on a login node. Start a 'qsub -I' session. Exiting!")
    sys.exit()

# Globals
cores = 64 # Number of workers spawned for each iteration. A value of 64 is the optimum on one node. 
limit = 0
input_dir = ''
base_url = ''
output_dir = ''
subset = ''


# ------------------------------------------------------------------------------
# _default_config:
# Check that the config file exists. By default it is './stac.yaml'
# Example:
"""
base_url:       http://dea-public-data.s3-ap-southeast-2.amazonaws.com/S2_MSI_ARD
input_dir:      /g/data/dz56/datacube/002/S2_MSI_ARD/packaged
subset:         05S105E-10S110E
output_dir:     /tmp
"""
"""
- Only the 'output_dir' needs write permission. In production mode it will be the same as the 'input_dir'.
- The 'subset' is either the date as '2018-06-29', tile number as '05S105E-10S110E' or as the case may be.
- To generate a STAC.json for all subsets in a directory, use its value as 'A'. 
  It may be required in the case of tiles, as temporal data is spread across them.
    subset: A
- In the case of date as subset, give it as below. 
    subset: 2018-06-29
"""
# ------------------------------------------------------------------------------
# create_item_dict:
# Create a dictionary structure of the required values. This will be written out 
# as the 'output_dir/item.json'
# These output files are STAC compliant and must be viewable with any STAC browser.
# ------------------------------------------------------------------------------
def create_item_dict(item,ard,geodata,base_url,item_dict):
    item_dict['id'] = ard['id']
    item_dict['type'] = 'Feature'
    
    item_dict['bbox'] = [ ard['extent']['coord']['ll']['lon'], ard['extent']['coord']['ll']['lat'], 
    ard['extent']['coord']['ur']['lon'], ard['extent']['coord']['ur']['lat'] ]

    item_dict['geometry'] = geodata['features'][0]['geometry']

    item_dict['properties'] = {}
    item_dict['properties']['datetime'] = ard['extent']['center_dt']
    item_dict['properties']['provider'] = 'GA'
    item_dict['properties']['license'] = 'PDDL-1.0'

    item_dict['links'] = [0]
    item_json_url = base_url + item + "/" + item + ".json"
    item_dict['links'][0] = {'rel': 'self', 'href': item_json_url}

    item_json_map_url = base_url + item + '/map.html'

    item_dict['assets'] = {}
    item_dict['assets']['map'] = {'href': item_json_map_url, "required": 'true', "type": "html"}

    ard_metadata_url = base_url + item + "/ARD-METADATA.yaml"
    item_dict['assets']['metadata'] = {'href': ard_metadata_url, "required": 'true', "type": "yaml"}

    j = 0
    bands = ard['image']['bands']
    for key in bands:
        j += 1
        path = ard['image']['bands'][key]['path']
        item_dict['assets'][key] = {'href': path, "required": 'true', "type": "GeoTIFF", "eo:band":[j]}

# ------------------------------------------------------------------------------
# create_jsons:
# Iterate through all items and create a JSON file for each.
# Will skip an item if either the 'ARD-METADATA.yaml' or 'bounds.geojson' is missing or empty.
# ------------------------------------------------------------------------------
def create_jsons(item):
    global input_dir,base_url,output_dir,subset
    item_dict = {} # Blank out the array for each item. Not really necessary!
    item_dir = os.path.join(input_dir,item)
    ard_metadata_file = item_dir + '/ARD-METADATA.yaml'
    bounds_file = item_dir + '/bounds.geojson'

    if (os.path.exists(ard_metadata_file) and os.path.getsize(ard_metadata_file) > 0) and (os.path.exists(bounds_file) and os.path.getsize(bounds_file) > 0):
        try:
            ard_metadata = yaml.load(open(ard_metadata_file))
            with open(bounds_file) as f:
                geodata = json.load(f)
                create_item_dict(item,ard_metadata,geodata,base_url,item_dict)
        except:
            print("*** Unknown error in loading the data.", item)
            pass
    else:
        print("*** No valid ARD-METADATA.yaml and/or bounds.geojson: SKIPPING ***:", item)

    # Write out the JSON files.
    item_output_dir = output_dir + subset + item
    if not os.path.exists(item_output_dir):
        os.makedirs(item_output_dir)
    item_json_file = item_output_dir + "/" + "STAC.json"

    # Write out only if the file does not exist.
    if (os.path.exists(item_json_file) and os.path.getsize(item_json_file) > 0):
        print("*** File exits. Not overwriting:", item_json_file)
    else:
        with open(item_json_file, 'w') as file:
             file.write(json.dumps(item_dict,indent=1)) 
#             print("{}".format(item_json_file)) 
        time.sleep(1) # make this wait long enough to finish the processing

def parallel_process():
    global input_dir,base_url,output_dir,subset
    global limit,cores
    items_dirs = os.listdir(input_dir)
    pool = Pool(processes=cores)              # start $np worker processes. It is the optimum
    if not limit: limit = len(items_dirs)
    print("Cores: {}; Items to be processed: {}".format(cores,limit))
    pool.map(create_jsons, items_dirs[:limit]) # Send $cores files each time until the set limit         
    print("Finished !")    

    
# ------------------------------------------------------------------------------
# usage:
# Help info to run. Invoke it with --info=usage
# ------------------------------------------------------------------------------
def usage():
    this_program = os.path.basename(__file__)
    print("\n\
Usage:\n\
    {} config.yaml. Default is './stac.yaml'. \n\
\n\
    Or, commandline as:\n\
        {} --base_urlp=url --input_dirp=path --subsetp=str --output_dirp=path\n\
\n\
    Output files (output_dir/subset/item/STAC.json) will be created for each item.\n\
\n\
    Existing files will not be overwritten.\n\
\n\
".format(this_program,this_program))

# ------------------------------------------------------------------------------
# main:
# The main function.
# ***REMEMBER:*** COMMANDLINE OPTIONS MUST ALL BE IN LOWER CASE
# 
# ------------------------------------------------------------------------------
@click.command(name='parse_direct')
@click.argument('stac_config_file', type=str, default='stac.yaml', metavar='STAC_CONFIG_FILE')
@click.option('--info', type=str, help='Type --info=yes to get additional info.')
@click.option('--base_urlp', type=str, help='URL of the product. e.g. https://FQDN/S2_MSI_ARD',default='')
@click.option('--input_dirp', type=str, help='Full path of the directory where the subsets are. e.g. /g/data/dz56/datacube/002/S2_MSI_ARD/packaged',default='')
@click.option('--subsetp', type=str, help='Date, tile_no, etc. that lists the items. e.g. 2018-06-29, 05S105E-10S110E, etc. ',default='')
@click.option('--output_dirp', type=str, help='Relative or full path of the output directory where the STAC.json will be written under "subset/item/"',default='')
def main(stac_config_file,base_urlp,input_dirp,subsetp,output_dirp,info):
    global input_dir,base_url,output_dir,subset
    input_dir = input_dirp
    base_url = base_urlp
    output_dir = output_dirp
    subset = subsetp
    if (info): usage()
    else:
        if ((not base_url) or (not input_dir) or (not subset) or (not output_dir)):  # Specify all or none in commandline. If any is missing, it will use the config file.
            config = yaml.load(open(stac_config_file))
            base_url = config['base_url']
            base_url = os.path.join(base_url, '')
            
            input_dir = config['input_dir']
    
            # Subset is defined separately so that it can be a date or tile number
            subset = config['subset'] 
        
            output_dir = config['output_dir']
    
            output_dir = os.path.join(output_dir, '')
            input_dir = os.path.join(input_dir, '')
            # Specify a subset as 2018-06-30 for L2, or as 05S105E-10S110E for S2_MSI_ARD. 
            # Option 'A' is suitable for S2_MSI_ARD where multiple tiles are involved
            if(subset is not 'A'):
                subset = os.path.join(subset, '')
        
                base_url = base_url + subset
                input_dir = input_dir + subset
                
                # Iterate through all items abd create a JSON file for each.
                parallel_process()
            else:
                subsets = os.listdir(input_dir)
                for subset in subsets:
                    subset = os.path.join(subset, '')
            
                    base_url = base_url + subset
                    input_dir = input_dir + subset
                    
                    output_subset_dir = output_dir + subset
                    if not os.path.exists(output_subset_dir):
                        os.makedirs(output_subset_dir)
    
                    # Iterate through all items abd create a JSON file for each.
                    create_jsons(input_dir,base_url,output_dir,subset)
#                    break # Activate for limiting the iteration to just one subset. 

# ------------------------------------------------------------------------------
# Standard boilerplate to call the main() function.
if __name__ == '__main__':
  main()

