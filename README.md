# STAC catalog generation


## What is STAC?
The [SpatioTemporal Asset Catalog specification](https://github.com/radiantearth/stac-spec/) is a simple specification being
designed to make open geospatial assets searchable and crawlable. It aims to realise the dream of enabling users to search for imagery and other assets across multiple providers.[[Ref](https://gist.github.com/omad/da6f740be0ead467c77c80d66701450f#file-spatio-temporal-access-catalogues-org)]

The word, "Spatio-Temporal", means "belonging to both space and time". The data uploaded in the [DEA Data Staging Area](http://dea-public-data.s3-website-ap-southeast-2.amazonaws.com/) on a daily basis is Spatio-temporal. It contains all the GeoTIFF files and their associated metadata collected over certain time intervals. Some are updated on a daily basis, whereas some are at random.

The data is publicly available for downloading and analysing offsite. 

However, in order to make them STAC-compliant, it is required to create a JSON file for each item.

## STAC json spec

The core of a Spatio-Temporal Asset Catalog (STAC) is set of JSON fields defined by the [STAC json spec](https://github.com/radiantearth/stac-spec/blob/master/json-spec/json-spec.md). These define an `Item` of a catalog, which can be served up in static or dynamic catalogs.[[Ref](https://github.com/radiantearth/stac-spec/tree/master/json-spec)] 


### This program is designed to create the STAC-compliant JSON file for the items that are daily updated.

