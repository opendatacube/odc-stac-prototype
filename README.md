
# STAC Catalog Json Generation


## What is STAC?
The [SpatioTemporal Asset Catalog specification](https://github.com/radiantearth/stac-spec/) is a simple specification being
designed to make open geospatial assets searchable and crawlable. It aims to realise the dream of enabling users to search for imagery and other assets across multiple providers.[[Ref-1](https://gist.github.com/omad/da6f740be0ead467c77c80d66701450f#file-spatio-temporal-access-catalogues-org)]

"Spatio-Temporal" means "belonging to both space and time". The data uploaded in the [DEA Data Staging Area](http://dea-public-data.s3-website-ap-southeast-2.amazonaws.com/) on a daily basis is spatio-temporal. It contains all the GeoTIFF files and their associated metadata collected over certain time intervals. Some are updated on a daily basis, whereas some others are at random.

The data is publicly available for downloading and analysing offsite. However, in order to read and display them, it may require third party programs such as QGIS or custom programs.

To make them STAC-compliant, so that it will have a universally accepted format, it is required to create a JSON file for each item. The specifications for it are still evolving, but the latest can be found at the links given below.

## STAC json spec

The core of a Spatio-Temporal Asset Catalog (STAC) is set of JSON fields defined by the [STAC json spec](https://github.com/radiantearth/stac-spec/blob/master/json-spec/json-spec.md). These define an `Item` of a catalog, which can be served up in static or dynamic catalogs.[[Ref-2](https://github.com/radiantearth/stac-spec/tree/master/json-spec)] 


### This program is designed to create the STAC-compliant JSON file for the items.

It is expected to be part of the cron jobs that daily update the DEA Data Staging area. The structure of the DEA Data Staging Area is given below. 

```
DEA Data Staging Area
This is a staging space to provide data to Digital Earth Australia's partner organisations.

If you'd prefer to access these files with s3fs the name of the AWS bucket is dea-public-data

Path:
http://dea-public-data.s3-ap-southeast-2.amazonaws.com /
Contents:
Last Modified                   Size           Key 
---------------------------------------------------------------------------------------------
                                0              ARD-Sample-Products/
                                0              ITEM_Intervals/
                                0              ITEM_V2/
                                0              L2/
                                0              LHTC_Tides/
                                0              S2-Sample-Products/
                                0              S2_MSI_ARD/
                                0              bench-data/
                                0              ewater/
                                0              geomedian-australia/
                                0              projects/
                                0              wofs-test/
2017-12-13T03:40:52.000Z        273.6 MB       canberra-S2AB-20m.tif

http://dea-public-data.s3-ap-southeast-2.amazonaws.com / L2 /
---------------------------------------------------------------------------------------------
                                               ../
                                0              sentinel-2-nrt/

http://dea-public-data.s3-ap-southeast-2.amazonaws.com / L2 / sentinel-2-nrt /
---------------------------------------------------------------------------------------------
                                               ../
                                0              S2MSIARD/

http://dea-public-data.s3-ap-southeast-2.amazonaws.com / L2 / sentinel-2-nrt / S2MSIARD /
---------------------------------------------------------------------------------------------
                                               ../
                                0              2018-05-28/
                                0              2018-05-29/
                                
http://dea-public-data.s3-ap-southeast-2.amazonaws.com / L2 / sentinel-2-nrt / S2MSIARD / 2018-05-28 /
---------------------------------------------------------------------------------------------
                                               ../
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56HPK_N02.06/
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56JPL_N02.06/
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56JPM_N02.06/
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56JPN_N02.06/
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56JQS_N02.06/

http://dea-public-data.s3-ap-southeast-2.amazonaws.com / L2 / sentinel-2-nrt / S2MSIARD / 2018-05-28 / S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56HPK_N02.06 /
---------------------------------------------------------------------------------------------
                                               ../
                                0              LAMBERTIAN/
                                0              NBAR/
                                0              NBART/
                                0              QA/
                                0              SUPPLEMENTARY/
2018-05-29T15:37:47.000Z        5.2 kB         map.html
2018-05-29T15:37:47.000Z        0.7 kB         bounds.geojson
2018-05-29T15:37:47.000Z        4.0 kB         README.md
2018-05-29T15:37:47.000Z        5.1 kB         CHECKSUM.sha1
2018-05-29T15:37:47.000Z        23.4 kB        ARD-METADATA.yaml

```
##### We need a STAC-compliant Json file, STAC.json, in the last directory above.

This STAC.json can, presumably, be read by a third party STAC browser similar to [this](http://iserv-stac.netlify.com/item/2014/01/02/IPR201401020901061496N02371W) or [this](https://s3-us-west-2.amazonaws.com/ai-gravitylab-stacbrowser/stacb.html) without a need to write separate code to interpret the data.

## Program Overview
The program, 'parse_direct.py', is a python program that can be executed as commandline, within a bash script or within crontab. The code is self-contained and requires only the standard Python modules. Parameters to the program can be given in a configuration file in YAML format or as commandline params.

The program will read two files listed above, bounds.geojson and ARD-METADATA.yaml, to create the Json file and save the latter as 'stac.json' in the above item directory.

Since each day's or tile's items can run into thousands, it may take several minutes to hours to complete. Be patient! A parallelised program
is planned to speed up the process.

## Program Details

#### DESCRIPTION:
This program creates STAC catalog Jsons for the GeoTIFFs in the DEA Staging area.

#### HOW TO USE:
Run as part of the cron job that creates and uploads GeoTIFFs from NetCDF.

#### PROGRAM FLOW:
1. Takes the base_url, input_dir, subset and output_dir specified in a YAML file or on commandline.

2. Takes the following files from input_dir/subset/item/:
    - bounds.geojson
    - ARD-METADATA.yaml

3. Parses the above files to create the 'stac.json'.
    - output_dir/subset/item/stac.json
    

## How to execute

1. Create a config file, e.g. stac.yaml or any other name, with the following content. 

```
base_url:       http://dea-public-data.s3-ap-southeast-2.amazonaws.com/S2_MSI_ARD
input_dir:      /g/data/dz56/datacube/002/S2_MSI_ARD/packaged
subset:         05S105E-10S110E
output_dir:     /tmp

```
NOTES:
```    
    - Only the 'output_dir' needs write permission. In production mode it will be the same as the 'input_dir'.
    - The 'subset' is either the date as '2018-06-29', tile number as '05S105E-10S110E' or as the case may be.
    - To generate a stac.json for all subsets in a directory, use its value as 'A'. It may be required in the case of tiles, as temporal data is spread across them.
        subset: A
    - In the case of date as subset, give it as below. 
        subset: 2018-06-29
    
```
2. Run the program from the commandline as below.

> parse_direct.py stac.yaml

or, without creating the stac.yaml:

> parse_direct.py --base_url=url --input_dir=path --subset=str --output_dir=path


## How to setup as a cron job

It depends on how the current setup is with regard to updating the staging area. The easiest way will be to add a line to execute the program from within the program that creates and uploads all other files to the staging area. 

More details shall be added here after the updating process is clearly understood.

_____________________________________________________________________________________________________________
```
TITLE: STAC Catalog Json Generation
DATE: <2018-07-01 Sun>
AUTHOR: Dr. Arapaut V. Sivaprasad
EMAIL: Sivaprasad.Arapaut@ga.gov.au, avs@webgenie.com
LANGUAGE: en
URL: https://github.com/opendatacube/odc-stac-prototype
```