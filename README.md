# QGIS-Subnet-Areas

Input points and roads in the same co-ordinate system and get a resulting areas layer which represents closest areas to the points based on drive time (currently doesn't incorporate road speed).

The .model3 file is confirmed to be working. The output may load but look blank - you need to change the CRS of the layer in the later properties.

The python script does not seem to work due to temporary layers - needs more investigation.

![Image description](https://i.redd.it/hxx713akwzx41.png)


![Image description](https://raw.githubusercontent.com/mattmarotta/QGIS-Subnet-Areas/master/Subnet%20Areas.png)

Credits/References
https://gis.stackexchange.com/questions/209419/how-to-compute-areas-of-influence-in-qgis
https://gis.stackexchange.com/questions/297002/programmatically-changing-line-lengths-in-qgis
https://gis.stackexchange.com/questions/307410/change-start-end-points-of-a-line-with-field-attributes#comment497542_307418
