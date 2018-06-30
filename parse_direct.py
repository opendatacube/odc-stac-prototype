#!/usr/bin/env python
# Created on 30 June, 2018, by copyright owner
# Last Modified on: 30 June, 2018, by copyright owner
# Copyright (c) 2018 Dr. Arapauat V. Sivaprasad
# Licence: GPL-3.0
# ------------------------------------------------------------------------------
'''
DESCRIPTION:
This program creates STAC catalog Jsons for the GeoTIFFs in the DEA Staging area.

HOW:

1. Run as part of the cron job that creates and uploads GeoTIFFs from NetCDF.

2. Takes the following dirname(s) from the 'base_dir' speciied in a YAML file
    e.g. from: /g/data/dz56/datacube/002/S2_MSI_ARD/packaged/10S150E-15S155E
    dirs: S2B_OPER_MSI_ARD_TL_SGS__20171202T014216_A003860_T56LMP_N02.06

3. Takes from the above the following files
    - bounds.geojson
    - ARD-METADATA.yaml

4. Parse the above two files to create the 'item.json' which contains all assets.

5. Save the file as 'STAC.json' in S2B_OPER_MSI_ARD_TL_SGS__20171202T014216_A003860_T56LMP_N02
    Note: In the dev version the files will be written to './Json'. But in production version it
    must write directly to S3 or any dir that gets uploaded.

CONFIG FILE: parse_direct.yaml

base_dir:
    /g/data/dz56/datacube/002/S2_MSI_ARD/packaged/10S150E-15S155E
output_dir:
    ./Json
'''
# ------------------------------------------------------------------------------
import click
import os
from os import path
import yaml
import json

# Globals
item_dict = {} # This is what gets written out as item_json

def _default_config(ctx, param, value):
    if path.exists(value):
        return value

    ctx.fail('STAC_CONFIG_FILE not provided.')

def get_bounds_geojson(item_json):
    with open(saved_bounds_geojson) as f:
        geodata = json.load(f)
        print(type(geodata))
        print (geodata['features'][0]['geometry'])
        geometry = geodata['features'][0]['geometry']
        item_dict['geometry'] = geometry

def create_item_dict(item,ard,geodata,base_url):
    item_dict['id'] = ard['id']
    item_dict['type'] = 'Feature'
    
    bbox = [ ard['extent']['coord']['ll']['lon'], ard['extent']['coord']['ll']['lat'], ard['extent']['coord']['ur']['lon'], ard['extent']['coord']['ur']['lat'] ]
    item_dict['bbox'] = bbox

    geometry = geodata['features'][0]['geometry']
    item_dict['geometry'] = geometry

    datetime = ard['extent']['center_dt']
    item_dict['properties'] = {}
    item_dict['properties']['datetime'] = datetime
    item_dict['properties']['provider'] = 'GA'
    item_dict['properties']['license'] = 'PDDL-1.0'

    item_dict['links'] = [0,0]
    item_json_file = 'Json/' + item + ".json"
    item_json_url = base_url + "/" + item + ".json"
    item_dict['links'][0] = {'rel': 'self', 'href': item_json_url}

    item_json_map_url = base_url + item + '/map.html'
    item_dict['links'][1] = {'rel': 'alternate', 'href': item_json_map_url, 'type':'html'}

    item_dict['assets'] = {}
    item_dict['assets']['map'] = {'href': item_json_map_url, "required": 'true', "type": "html"}

    ard_metadata_url = base_url + "/" + item + "/ARD-METADATA.yaml"
    item_dict['assets']['metadata'] = {'href': ard_metadata_url, "required": 'true', "type": "yaml"}

    j =0
    bands = ard['image']['bands']
    for key in bands:
        j += 1
        path = ard['image']['bands'][key]['path']
        item_dict['assets'][key] = {'href': path, "required": 'true', "type": "GeoTIFF", "eo:band":j}

def create_jsons(input_dir,base_url,output_dir):
    items_dirs = os.listdir(input_dir)
    for item in items_dirs:
        item_dir = os.path.join(input_dir,item)
        ard_metadata_file = item_dir + '/ARD-METADATA.yaml'
        bounds_file = item_dir + '/bounds.geojson'

        if (path.exists(ard_metadata_file) and path.getsize(ard_metadata_file) > 0) and (path.exists(bounds_file) and path.getsize(bounds_file) > 0):
            try:
                ard_metadata = yaml.load(open(ard_metadata_file))
                with open(bounds_file) as f:
                    geodata = json.load(f)
                    create_item_dict(item,ard_metadata,geodata,base_url)
            except:
                print("*** Unknown error in loading the metadata and/or bounds.")
                pass
        else:
            print("*** No file(s). SKIPPING ***:", item)

        item_json_file = output_dir + "/" + item + ".json"
        with open(item_json_file, 'w') as file:
             file.write(json.dumps(item_dict)) 
        print("Wrote: ", item_json_file)         

def usage():
    print("Usage: ./parse_direct.py config.yaml, where the input/output dirs and date/tile are given. Default=stac.yaml. \
Output files (*.json) will be created for each item in the input dir.")

@click.command(name='parse_direct')
@click.argument('stac_config_file', type=str, callback=_default_config, default='stac.yaml',
                metavar='STAC_CONFIG_FILE')
@click.option('--info', type=str, help='Usage: ./parse_direct.py config.yaml, where the input/output dirs and date/tile are given. Default=stac.yaml. \
Output files (*.json) will be created for each item in the input dir.')
def main(stac_config_file,info):
    if (info): usage()
    else:
        config = yaml.load(open(stac_config_file))
        base_url = config['base_url']
    
        input_dir = config['input_dir']
        subset = config['subset'] # Subset is defined separately so that it can be a date or tile number
    
        base_url = base_url + "/" + subset
        input_dir = input_dir + "/" + subset
        
        output_dir = config['output_dir']
        create_jsons(input_dir,base_url,output_dir)

# Standard boilerplate to call the main() function.
if __name__ == '__main__':
  main()

