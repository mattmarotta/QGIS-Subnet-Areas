# QGIS-Subnet-Areas

Input points and roads in the same co-ordinate system and get a resulting areas layer which represents closest areas to the points based on drive time (currently doesn't incorporate road speed).

Mainly relies on GRASS algorithm v.net.alloc which does a network allocation (allocates roads to closest points) essentially creating subnetworks. These subnetworks are then used to create areas, hence this model's name "Subnet Areas".

Some rough notes on the methodology: https://www.reddit.com/r/QGIS/comments/gimg5z/introducing_my_subnet_areas_model_my_first_model/

## Important notes on how to use

1. Always run these from the Processing Toolbox, not the model editor. In the Processing toolbox, click the gears icon and select "Add Model to Toolbox", or the python icon and select "Add Script to Toolbox". Then just load in the model3/python file.
2. When running the model from either the model file or python script, the "network_allocation" output must be saved to a file. Temporary Layer will cause the model execution to fail.
3. Output may load but look blank - you need to change the CRS of the layer in the later properties.

## Images

![QGIS Subnet Areas output](https://i.redd.it/hxx713akwzx41.png)


![QGIS Subnet Areas model](https://raw.githubusercontent.com/mattmarotta/QGIS-Subnet-Areas/master/Subnet%20Areas.png)

## Future Improvements

- Needs more testing; only tested with one dataset
- Potentially needs optimization - it runs quickly for a small city, but could take hours for state/province
- Incorporate road speed as optional for v.net.alloc
- Figure out how to incorporate road traffic (other tools out there can do this, such as Alteryx)
- Improve the documentation with screenshots, more detailed methodology
- Consider turning this into a plugin
- Fix projection issue - v.net.alloc output does not output the same as final areas

## References

https://gis.stackexchange.com/questions/209419/how-to-compute-areas-of-influence-in-qgis

I originally posted this question which led to this methodology.

https://gis.stackexchange.com/questions/297002/programmatically-changing-line-lengths-in-qgis

Helped with how to change line lengths.

https://gis.stackexchange.com/questions/307410/change-start-end-points-of-a-line-with-field-attributes#comment497542_307418

The final calculation in the link above did not work so I found this worked instead.

https://gis.stackexchange.com/questions/94493/unable-to-select-float-precision-when-adding-column

I could not for the life of me figure out why I couldn't change the precision in the field calculator. Turns out geopackages store precison as floating whereas it has to be explicitly defined for shapefiles I was used to working with.

https://gis.stackexchange.com/questions/310148/pyqgis-processing-memory-not-found

When I tried to run this model as a python script, it would just fail very early on using v.net.alloc. Confirms that grass in python cannot output to temporary layer. It also must be output to a permanent file when running the model file.

https://gis.stackexchange.com/questions/321297/qgis-crashes-when-running-script-from-processing-script-editor

This model may crash qgis and I couldn't figure out why. Running it from the processing toolbox solves this.
