# STAC Catalog Json Generation


## What is STAC?
The [SpatioTemporal Asset Catalog specification](https://github.com/radiantearth/stac-spec/) is a simple specification being
designed to make open geospatial assets searchable and crawlable. It aims to realise the dream of enabling users to search for imagery and other assets across multiple providers.[[Ref](https://gist.github.com/omad/da6f740be0ead467c77c80d66701450f#file-spatio-temporal-access-catalogues-org)]

The word, "Spatio-Temporal", means "belonging to both space and time". The data uploaded in the [DEA Data Staging Area](http://dea-public-data.s3-website-ap-southeast-2.amazonaws.com/) on a daily basis is Spatio-temporal. It contains all the GeoTIFF files and their associated metadata collected over certain time intervals. Some are updated on a daily basis, whereas some are at random.

The data is publicly available for downloading and analysing offsite. 

However, in order to make them STAC-compliant, it is required to create a JSON file for each item. The specifications for it are still evolving.

## STAC json spec

The core of a Spatio-Temporal Asset Catalog (STAC) is set of JSON fields defined by the [STAC json spec](https://github.com/radiantearth/stac-spec/blob/master/json-spec/json-spec.md). These define an `Item` of a catalog, which can be served up in static or dynamic catalogs.[[Ref](https://github.com/radiantearth/stac-spec/tree/master/json-spec)] 


### This program is designed to create the STAC-compliant JSON file for the items.

It is expected to be part of the cron jobs that daily update the DEA Data Staging area. 

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
```
Navigating through the links will show the details as given below.

```
Path:
http://dea-public-data.s3-ap-southeast-2.amazonaws.com / L2 /
Contents:
Last Modified                   Size           Key 
---------------------------------------------------------------------------------------------
                                               ../
                                0              sentinel-2-nrt/

http://dea-public-data.s3-ap-southeast-2.amazonaws.com / L2 / sentinel-2-nrt /
Last Modified                   Size           Key 
---------------------------------------------------------------------------------------------
                                               ../
                                0              S2MSIARD/

http://dea-public-data.s3-ap-southeast-2.amazonaws.com / L2 / sentinel-2-nrt / S2MSIARD /
Last Modified                   Size           Key 
---------------------------------------------------------------------------------------------
                                               ../
                                0              2018-05-28/
                                0              2018-05-29/
                                
http://dea-public-data.s3-ap-southeast-2.amazonaws.com / L2 / sentinel-2-nrt / S2MSIARD / 2018-05-28 /
Contents:
Last Modified                   Size           Key 
---------------------------------------------------------------------------------------------
                                               ../
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56HPK_N02.06/
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56JPL_N02.06/
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56JPM_N02.06/
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56JPN_N02.06/
                                0              S2B_OPER_MSI_ARD_TL_EPAE_20180529T010118_A006405_T56JQS_N02.06/
```
