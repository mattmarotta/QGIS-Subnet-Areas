### v.net.alloc
- Straightforward, separates the roads into segments based on closest drive time to points. Currently my model does not incorporate road speed but could easily be done. I'm not sure if it could incorporate road direction (ex. one way streets). Also would be cool to explore traffic data, although it probably wouldn't have a major impact on areas.

### Explode Lines
- To separate multipart features and make sure the roads separate at the "border" of where the closest point changes.

### Extract Vertices

### Join attributes by location
- This checks to see if the roads touch two points with different categories from v.net.alloc. Since the above steps create overlapping points at a border, checking this is key for the next steps.

### Field calculator: outlen
- This calculates the length of the line minus 0.5%. This field will be used to shorten a line if it touches two overlapping points with different categories from v.net.alloc.

### Field calculator: x0,y0,x1,y1
- If the line segment touches two overlapping points with different category values, it gets shortened. This is crucial because the voronoi polygons later on will get messed up if there are two points in the same spot with different categories. This step calculates the start and end points of a line; if they dont touch two points with different categories, they dont change. If they do, they are shortened.

### Geometry by expression
- This does the actual change of line length

### Extract vertices 2
- Now take all of the vertices, the only overlapping points should be ones with the same category.

### Calculate x and y
- There is no tool in qgis that lets you remove duplicate points with a threshold. It only works for polygons. So, I've rounded x an y to the nearest tenth - kind of a manual threshold.

### Remove duplicates
- Removes duplicate points where x, y, and category are the same (overlapping points, or very close to overlapping, where they are closest to the main points, therefore no need for two)

### Voronoi

### Dissolve
