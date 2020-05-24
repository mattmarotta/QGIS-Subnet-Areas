"""
Subnet Areas
v0.2
By Matt Marotta
2020-05-24
With QGIS : 31202

This script takes a road and point layer and creates areas that are closest to the points.

Requirements:
1. Always run these from the Processing Toolbox, not the model editor. In the Processing toolbox,
click the gears icon and select "Add Model to Toolbox", or the python icon and select "Add Script
to Toolbox". Then just load in the model3/python file.

2. When running the model from either the model file or python script, the "network_allocation"
output must be saved to a file. Temporary Layer will cause the model execution to fail.

3. Output may load but look blank - you need to change the CRS of the layer in the later properties.

"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterVectorDestination
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class SubnetAreas(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('points', 'Points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('roads', 'Roads', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorDestination('Network_allocation', 'network_allocation', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Subnet_areas', 'subnet_areas', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(16, model_feedback)
        results = {}
        outputs = {}

        # v.net.alloc
        alg_params = {
            '-g': False,
            'GRASS_MIN_AREA_PARAMETER': 0.0001,
            'GRASS_OUTPUT_TYPE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
            'GRASS_VECTOR_DSCO': '',
            'GRASS_VECTOR_EXPORT_NOCAT': False,
            'GRASS_VECTOR_LCO': '',
            'arc_backward_column': '',
            'arc_column': '',
            'arc_type': [0,1],
            'center_cats': '1-100000',
            'input': parameters['roads'],
            'node_column': '',
            'points': parameters['points'],
            'threshold': 500,
            'output': parameters['Network_allocation']
        }
        outputs['Vnetalloc'] = processing.run('grass7:v.net.alloc', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Network_allocation'] = outputs['Vnetalloc']['output']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Explode lines
        alg_params = {
            'INPUT': outputs['Vnetalloc']['output'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExplodeLines'] = processing.run('native:explodelines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract vertices
        alg_params = {
            'INPUT': outputs['ExplodeLines']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractVertices'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary)
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['ExplodeLines']['OUTPUT'],
            'JOIN': outputs['ExtractVertices']['OUTPUT'],
            'JOIN_FIELDS': ['cat'],
            'PREDICATE': [0],
            'SUMMARIES': [1],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationSummary'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # outlen
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'outlen',
            'FIELD_PRECISION': 8,
            'FIELD_TYPE': 0,
            'FORMULA': 'if(\"cat_unique\" > 1, length($geometry) - (length($geometry) * 0.005), length($geometry))',
            'INPUT': outputs['JoinAttributesByLocationSummary']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Outlen'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # x0
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'x0',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'x(centroid($geometry)) - \n    (outlen/2) * sin(radians(angle_at_vertex($geometry, 0)))',
            'INPUT': outputs['Outlen']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['X0'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # y0
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'y0',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'y(centroid($geometry)) - \n    (outlen/2) * cos(radians(angle_at_vertex($geometry, 0)))\n',
            'INPUT': outputs['X0']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Y0'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # x1
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'x1',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'x(centroid($geometry)) + \n    (outlen/2) * sin(radians(angle_at_vertex($geometry, 0)))\n',
            'INPUT': outputs['Y0']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['X1'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # y1
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'y1',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'y(centroid($geometry)) + \n    (outlen/2) * cos(radians(angle_at_vertex($geometry, 0)))',
            'INPUT': outputs['X1']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Y1'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Geometry by expression
        alg_params = {
            'EXPRESSION': 'geom_from_wkt(\'Linestring(\'||\"x1\"||\' \'||\"y1\"||\',\'||\"x0\"||\' \'||\"y0\"||\')\')',
            'INPUT': outputs['Y1']['OUTPUT'],
            'OUTPUT_GEOMETRY': 1,
            'WITH_M': False,
            'WITH_Z': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['GeometryByExpression'] = processing.run('native:geometrybyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract vertices 2
        alg_params = {
            'INPUT': outputs['GeometryByExpression']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractVertices2'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # x
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'x',
            'FIELD_PRECISION': 1,
            'FIELD_TYPE': 0,
            'FORMULA': 'round(x($geometry),1)',
            'INPUT': outputs['ExtractVertices2']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['X'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # y
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'y',
            'FIELD_PRECISION': 1,
            'FIELD_TYPE': 0,
            'FORMULA': 'round(y($geometry),1)',
            'INPUT': outputs['X']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Y'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Delete duplicates by attribute
        alg_params = {
            'FIELDS': ['cat_unique','x','y'],
            'INPUT': outputs['Y']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteDuplicatesByAttribute'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Voronoi polygons
        alg_params = {
            'BUFFER': 0,
            'INPUT': outputs['DeleteDuplicatesByAttribute']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VoronoiPolygons'] = processing.run('qgis:voronoipolygons', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Dissolve
        alg_params = {
            'FIELD': ['cat'],
            'INPUT': outputs['VoronoiPolygons']['OUTPUT'],
            'OUTPUT': parameters['Subnet_areas']
        }
        outputs['Dissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Subnet_areas'] = outputs['Dissolve']['OUTPUT']
        return results

    def name(self):
        return 'Subnet Areas'

    def displayName(self):
        return 'Subnet Areas'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return SubnetAreas()
