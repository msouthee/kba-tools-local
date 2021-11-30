# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      SpeciesSelectionTool.py
#
# Script Created:   2021-10-27
# Last Updated:     2021-11-30
# Script Author:    Meg Southee
#
# Purpose:          Create definition queries and group the output datasets (with valid data) under a species heading
#                   in the TOC in the active map.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries
import arcpy


class Tool:
    """Select all points, lines and polygons for a specific species."""
    def __init__(self):
        pass

    def run_tool(self, parameters, messages):

        # Make variables from parameters
        param_table = parameters[0].valueAsText
        param_sql = parameters[1].valueAsText
        param_infraspecies = parameters[2].valueAsText

        arcpy.AddMessage("Parameters: {0}, {1}, {2}".format(param_table, param_sql, param_infraspecies))

        # # species level list based on the Canadian national name level [ca_nname_level] field
        # sp_level_list = ["species",
        #                  "subspecies",
        #                  "population",
        #                  "variety"]

        # List of biotics fields that you want to use in the search cursor
        biotics_fields = ["national_scientific_name",
                          "speciesid",
                          "ca_nname_level"]

        try:
            # Current ArcPro Project
            aprx = arcpy.mp.ArcGISProject("CURRENT")

            # Current Active Map in ArcPro Project
            m = aprx.activeMap

            # clear all selections in the map
            m.clearSelection()

            # Select the record in BIOTICS table based on the user-specified sql expression
            biotics_record = arcpy.management.SelectLayerByAttribute(param_table,
                                                                     "NEW_SELECTION",
                                                                     param_sql)

            # Get record-level information about the selected record using a search cursor
            with arcpy.da.SearchCursor(param_table, biotics_fields, param_sql) as cursor:
                for row in cursor:

                    arcpy.AddMessage("Scientific Name: {}".format(row[0]))
                    arcpy.AddMessage("Species ID: {}".format(row[1]))
                    arcpy.AddMessage("Species Level: {}".format(row[2]))

                    # # Check to see if the selected record is a full species or a subspecies
                    # if row[2].lower() == "species":
                    #     arcpy.AddMessage("Species selected")
                    #     pass
                    #
                    # # this could also just be an else: statement if all 3 categories are being handled the same way
                    # elif row[2].lower() in ("subspecies", "population", "variety"):
                    #     arcpy.AddMessage("{} selected".format(row[2]))
                    #     pass

                    # Logic if user wants to select the full species & infraspecies [based on param_infraspecies]
                    if param_infraspecies == "Yes":

                        # Logic to select additional records in the biotics table

                        # Get the full species name
                        split = row[0].split(" ")
                        s = " "
                        species = s.join(split[:2])

                        # SQL statement to add full species and all infraspecies/subspecies/populations/varieties
                        sql = "national_scientific_name LIKE '{}%'".format(species)

                        # Add the full species and infraspecies to the selected record in biotics table
                        biotics_record = arcpy.management.SelectLayerByAttribute(param_table,
                                                                                 "ADD_TO_SELECTION",
                                                                                 sql)

                    # Logic if users only wants to select the single species
                    else:
                        pass

                """ This is where you end up if directly if param_infraspecies == "Yes", but you get here either way.
                    Use the speciesid value to iterate through the datasets and create output layers in the TOC."""

                # Get the count from the Result object based on the selected records in BIOTICS table
                count = int(arcpy.GetCount_management(biotics_record).getOutput(0))

                # Check to see how many records are selected in biotics
                if count == 1:  # Process single species
                    arcpy.AddMessage("{} record selected from Biotics table.".format(count))

                    # Variable to hold the species id
                    speciesid = row[1]

                    # Variable to hold the speciesid sql statement
                    speciesid_sql = "speciesid = {}".format(speciesid)
                    # arcpy.AddMessage(speciesid_sql)

                    # This logic doesn't actually help the workflow, it just checks that the logic is working properly
                    # Select single record in the species table
                    species_record = arcpy.management.SelectLayerByAttribute("Species",
                                                                             "NEW_SELECTION",
                                                                             speciesid_sql)

                    # Check that one record is selected
                    species_count = int(arcpy.GetCount_management(species_record).getOutput(0))
                    arcpy.AddMessage("{} record selected from Species table.".format(species_count))

                    # # Iterate through the other 4 feature classes and start making data layers
                    # points = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputPoint",
                    #                                                  "NEW_SELECTION",
                    #                                                  speciesid_sql)
                    #
                    # lines = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputLine",
                    #                                                 "NEW_SELECTION",
                    #                                                 speciesid_sql)
                    #
                    # polygons = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputPolygon",
                    #                                                    "NEW_SELECTION",
                    #                                                    speciesid_sql)
                    #
                    eo_polygons = arcpy.management.SelectLayerByAttribute(r"SpeciesData\EO_Polygon",
                                                                          "NEW_SELECTION",
                                                                          speciesid_sql)

                    eo_count = int(arcpy.GetCount_management(eo_polygons).getOutput(0))
                    arcpy.AddMessage("{} record selected from EO_Polygon table.".format(eo_count))

                    # lyr_name = "EO Polygon - SpeciesID {}".format(speciesid)
                    # arcpy.AddMessage(lyr_name)

                    # This stuff isn't working, but it also isn't throwing errors
                    # arcpy.management.MakeFeatureLayer(eo_polygons, lyr_name, speciesid_sql, None)

                    eo_polygons_lyr = arcpy.management.MakeFeatureLayer(r"SpeciesData\EO_Polygon",
                                                                        "layer 1")

                    # # Test 1 - this is what you see from the geoprocessing history
                    # eo_polygons_lyr = arcpy.management.MakeFeatureLayer(r"SpeciesData\EO_Polygon",
                    #                                                     "layer 1", speciesid_sql, None,
                    #                                                     "objectid objectid VISIBLE NONE;"
                    #                                                     "inputpolygonid inputpolygonid VISIBLE NONE;"
                    #                                                     "inputdatasetid inputdatasetid VISIBLE NONE;"
                    #                                                     "speciesid speciesid VISIBLE NONE;"
                    #                                                     "mindate mindate VISIBLE NONE;"
                    #                                                     "maxdate maxdate VISIBLE NONE;"
                    #                                                     "datasetsourceuniqueid datasetsourceuniqueid VISIBLE NONE;"
                    #                                                     "uri uri VISIBLE NONE;license license VISIBLE NONE;"
                    #                                                     "coordinatesobscured coordinatesobscured VISIBLE NONE;"
                    #                                                     "accuracy accuracy VISIBLE NONE;"
                    #                                                     "eorank eorank VISIBLE NONE;"
                    #                                                     "individualcount individualcount VISIBLE NONE;"
                    #                                                     "representationaccuracy representationaccuracy VISIBLE NONE;"
                    #                                                     "synonymid synonymid VISIBLE NONE;"
                    #                                                     "globalid globalid VISIBLE NONE;"
                    #                                                     "created_user created_user VISIBLE NONE;"
                    #                                                     "created_date created_date VISIBLE NONE;"
                    #                                                     "last_edited_user last_edited_user VISIBLE NONE;"
                    #                                                     "last_edited_date last_edited_date VISIBLE NONE;"
                    #                                                     "globalid_1 globalid_1 VISIBLE NONE;"
                    #                                                     "origin origin VISIBLE NONE;"
                    #                                                     "seasonality seasonality VISIBLE NONE;"
                    #                                                     "subnation subnation VISIBLE NONE;"
                    #                                                     "eodata eodata VISIBLE NONE;"
                    #                                                     "gendesc gendesc VISIBLE NONE;"
                    #                                                     "eorankdesc eorankdesc VISIBLE NONE;"
                    #                                                     "repaccuracycomment repaccuracycomment VISIBLE NONE;"
                    #                                                     "confidenceextent confidenceextent VISIBLE NONE;"
                    #                                                     "confidenceextentdesc confidenceextentdesc VISIBLE NONE;"
                    #                                                     "surveydate surveydate VISIBLE NONE;"
                    #                                                     "datasensitivity datasensitivity VISIBLE NONE;"
                    #                                                     "datasensitivitycat datasensitivitycat VISIBLE NONE;"
                    #                                                     "idconfirmed idconfirmed VISIBLE NONE;"
                    #                                                     "eorankdate eorankdate VISIBLE NONE;"
                    #                                                     "eorankcomments eorankcomments VISIBLE NONE;"
                    #                                                     "additionalinvneeded additionalinvneeded VISIBLE NONE;"
                    #                                                     "ownership ownership VISIBLE NONE;"
                    #                                                     "ownercomments ownercomments VISIBLE NONE;"
                    #                                                     "dataqcstatus dataqcstatus VISIBLE NONE;"
                    #                                                     "mapqcstatus mapqcstatus VISIBLE NONE;"
                    #                                                     "qccomments qccomments VISIBLE NONE;"
                    #                                                     "eoid eoid VISIBLE NONE;"
                    #                                                     "sfid sfid VISIBLE NONE;"
                    #                                                     "descriptor descriptor VISIBLE NONE;"
                    #                                                     "locator locator VISIBLE NONE;"
                    #                                                     "mappingcomments mappingcomments VISIBLE NONE;"
                    #                                                     "digitizingcomments digitizingcomments VISIBLE NONE;"
                    #                                                     "locuncertaintytype locuncertaintytype VISIBLE NONE;"
                    #                                                     "locuncertaintydistcls locuncertaintydistcls VISIBLE NONE;"
                    #                                                     "locuncertaintydistunit locuncertaintydistunit VISIBLE NONE;"
                    #                                                     "locuseclass locuseclass VISIBLE NONE;"
                    #                                                     "independentsf independentsf VISIBLE NONE;"
                    #                                                     "unsuitablehabexcluded unsuitablehabexcluded VISIBLE NONE;"
                    #                                                     "Shape__Area Shape__Area VISIBLE NONE;"
                    #                                                     "Shape__Length Shape__Length VISIBLE NONE;"
                    #                                                     "shape shape VISIBLE NONE"
                    #                                                     )

                    # # Test 2 - doesn't work
                    # eo_polygons_lyr = arcpy.management.MakeFeatureLayer(eo_polygons,
                    #                                                     "layer 2", speciesid_sql, None,
                    #                                                     "objectid objectid VISIBLE NONE;"
                    #                                                     "inputpolygonid inputpolygonid VISIBLE NONE;"
                    #                                                     "inputdatasetid inputdatasetid VISIBLE NONE;"
                    #                                                     "speciesid speciesid VISIBLE NONE;"
                    #                                                     "mindate mindate VISIBLE NONE;"
                    #                                                     "maxdate maxdate VISIBLE NONE;"
                    #                                                     "datasetsourceuniqueid datasetsourceuniqueid VISIBLE NONE;"
                    #                                                     "uri uri VISIBLE NONE;license license VISIBLE NONE;"
                    #                                                     "coordinatesobscured coordinatesobscured VISIBLE NONE;"
                    #                                                     "accuracy accuracy VISIBLE NONE;"
                    #                                                     "eorank eorank VISIBLE NONE;"
                    #                                                     "individualcount individualcount VISIBLE NONE;"
                    #                                                     "representationaccuracy representationaccuracy VISIBLE NONE;"
                    #                                                     "synonymid synonymid VISIBLE NONE;"
                    #                                                     "globalid globalid VISIBLE NONE;"
                    #                                                     "created_user created_user VISIBLE NONE;"
                    #                                                     "created_date created_date VISIBLE NONE;"
                    #                                                     "last_edited_user last_edited_user VISIBLE NONE;"
                    #                                                     "last_edited_date last_edited_date VISIBLE NONE;"
                    #                                                     "globalid_1 globalid_1 VISIBLE NONE;"
                    #                                                     "origin origin VISIBLE NONE;"
                    #                                                     "seasonality seasonality VISIBLE NONE;"
                    #                                                     "subnation subnation VISIBLE NONE;"
                    #                                                     "eodata eodata VISIBLE NONE;"
                    #                                                     "gendesc gendesc VISIBLE NONE;"
                    #                                                     "eorankdesc eorankdesc VISIBLE NONE;"
                    #                                                     "repaccuracycomment repaccuracycomment VISIBLE NONE;"
                    #                                                     "confidenceextent confidenceextent VISIBLE NONE;"
                    #                                                     "confidenceextentdesc confidenceextentdesc VISIBLE NONE;"
                    #                                                     "surveydate surveydate VISIBLE NONE;"
                    #                                                     "datasensitivity datasensitivity VISIBLE NONE;"
                    #                                                     "datasensitivitycat datasensitivitycat VISIBLE NONE;"
                    #                                                     "idconfirmed idconfirmed VISIBLE NONE;"
                    #                                                     "eorankdate eorankdate VISIBLE NONE;"
                    #                                                     "eorankcomments eorankcomments VISIBLE NONE;"
                    #                                                     "additionalinvneeded additionalinvneeded VISIBLE NONE;"
                    #                                                     "ownership ownership VISIBLE NONE;"
                    #                                                     "ownercomments ownercomments VISIBLE NONE;"
                    #                                                     "dataqcstatus dataqcstatus VISIBLE NONE;"
                    #                                                     "mapqcstatus mapqcstatus VISIBLE NONE;"
                    #                                                     "qccomments qccomments VISIBLE NONE;"
                    #                                                     "eoid eoid VISIBLE NONE;"
                    #                                                     "sfid sfid VISIBLE NONE;"
                    #                                                     "descriptor descriptor VISIBLE NONE;"
                    #                                                     "locator locator VISIBLE NONE;"
                    #                                                     "mappingcomments mappingcomments VISIBLE NONE;"
                    #                                                     "digitizingcomments digitizingcomments VISIBLE NONE;"
                    #                                                     "locuncertaintytype locuncertaintytype VISIBLE NONE;"
                    #                                                     "locuncertaintydistcls locuncertaintydistcls VISIBLE NONE;"
                    #                                                     "locuncertaintydistunit locuncertaintydistunit VISIBLE NONE;"
                    #                                                     "locuseclass locuseclass VISIBLE NONE;"
                    #                                                     "independentsf independentsf VISIBLE NONE;"
                    #                                                     "unsuitablehabexcluded unsuitablehabexcluded VISIBLE NONE;"
                    #                                                     "Shape__Area Shape__Area VISIBLE NONE;"
                    #                                                     "Shape__Length Shape__Length VISIBLE NONE;"
                    #                                                     "shape shape VISIBLE NONE"
                    #                                                     )

                    # # Test 3 - didn't work either
                    # eo_polygons_lyr = arcpy.management.MakeFeatureLayer("https://gis.natureserve.ca/arcgis/rest/services/EO_Polygons/FeatureServer/0",
                    #                                                     "layer 3", speciesid_sql, None,
                    #                                                     "objectid objectid VISIBLE NONE;"
                    #                                                     "inputpolygonid inputpolygonid VISIBLE NONE;"
                    #                                                     "inputdatasetid inputdatasetid VISIBLE NONE;"
                    #                                                     "speciesid speciesid VISIBLE NONE;"
                    #                                                     "mindate mindate VISIBLE NONE;"
                    #                                                     "maxdate maxdate VISIBLE NONE;"
                    #                                                     "datasetsourceuniqueid datasetsourceuniqueid VISIBLE NONE;"
                    #                                                     "uri uri VISIBLE NONE;license license VISIBLE NONE;"
                    #                                                     "coordinatesobscured coordinatesobscured VISIBLE NONE;"
                    #                                                     "accuracy accuracy VISIBLE NONE;"
                    #                                                     "eorank eorank VISIBLE NONE;"
                    #                                                     "individualcount individualcount VISIBLE NONE;"
                    #                                                     "representationaccuracy representationaccuracy VISIBLE NONE;"
                    #                                                     "synonymid synonymid VISIBLE NONE;"
                    #                                                     "globalid globalid VISIBLE NONE;"
                    #                                                     "created_user created_user VISIBLE NONE;"
                    #                                                     "created_date created_date VISIBLE NONE;"
                    #                                                     "last_edited_user last_edited_user VISIBLE NONE;"
                    #                                                     "last_edited_date last_edited_date VISIBLE NONE;"
                    #                                                     "globalid_1 globalid_1 VISIBLE NONE;"
                    #                                                     "origin origin VISIBLE NONE;"
                    #                                                     "seasonality seasonality VISIBLE NONE;"
                    #                                                     "subnation subnation VISIBLE NONE;"
                    #                                                     "eodata eodata VISIBLE NONE;"
                    #                                                     "gendesc gendesc VISIBLE NONE;"
                    #                                                     "eorankdesc eorankdesc VISIBLE NONE;"
                    #                                                     "repaccuracycomment repaccuracycomment VISIBLE NONE;"
                    #                                                     "confidenceextent confidenceextent VISIBLE NONE;"
                    #                                                     "confidenceextentdesc confidenceextentdesc VISIBLE NONE;"
                    #                                                     "surveydate surveydate VISIBLE NONE;"
                    #                                                     "datasensitivity datasensitivity VISIBLE NONE;"
                    #                                                     "datasensitivitycat datasensitivitycat VISIBLE NONE;"
                    #                                                     "idconfirmed idconfirmed VISIBLE NONE;"
                    #                                                     "eorankdate eorankdate VISIBLE NONE;"
                    #                                                     "eorankcomments eorankcomments VISIBLE NONE;"
                    #                                                     "additionalinvneeded additionalinvneeded VISIBLE NONE;"
                    #                                                     "ownership ownership VISIBLE NONE;"
                    #                                                     "ownercomments ownercomments VISIBLE NONE;"
                    #                                                     "dataqcstatus dataqcstatus VISIBLE NONE;"
                    #                                                     "mapqcstatus mapqcstatus VISIBLE NONE;"
                    #                                                     "qccomments qccomments VISIBLE NONE;"
                    #                                                     "eoid eoid VISIBLE NONE;"
                    #                                                     "sfid sfid VISIBLE NONE;"
                    #                                                     "descriptor descriptor VISIBLE NONE;"
                    #                                                     "locator locator VISIBLE NONE;"
                    #                                                     "mappingcomments mappingcomments VISIBLE NONE;"
                    #                                                     "digitizingcomments digitizingcomments VISIBLE NONE;"
                    #                                                     "locuncertaintytype locuncertaintytype VISIBLE NONE;"
                    #                                                     "locuncertaintydistcls locuncertaintydistcls VISIBLE NONE;"
                    #                                                     "locuncertaintydistunit locuncertaintydistunit VISIBLE NONE;"
                    #                                                     "locuseclass locuseclass VISIBLE NONE;"
                    #                                                     "independentsf independentsf VISIBLE NONE;"
                    #                                                     "unsuitablehabexcluded unsuitablehabexcluded VISIBLE NONE;"
                    #                                                     "Shape__Area Shape__Area VISIBLE NONE;"
                    #                                                     "Shape__Length Shape__Length VISIBLE NONE;"
                    #                                                     "shape shape VISIBLE NONE"
                    #                                                     )

                    # Save the project
                    aprx.save()

                    # Reference the layers from the map
                    lyr = m.listLayers("layer 1")[0]
                    group_lyr = m.listLayers("SpeciesData")[0]

                    aprx.save()

                    # Add the layer to an existing group
                    m.addLayerToGroup(group_lyr, lyr, "TOP")

                    # Move layer in the TOC?

                    # Save the project
                    aprx.save()

                    arcpy.AddMessage("End of script.")

                elif count > 1:  # Process species & infraspecies
                    arcpy.AddMessage("{} records selected.".format(count))

                    # process all of the species in the list

                    # create a new search cursor & start calling your function to do stuff


                else:
                    # Throw an error that there are no species selected
                    arcpy.AddError("{} records selected. Please select a species using the SQL statement"
                                   .format(count))




        except:
            print("Error!")


# Controlling process
if __name__ == '__main__':
    sst = Tool()

    # Hard-coded parameters for debugging
    param_table = arcpy.Parameter()
    param_sql = arcpy.Parameter()
    param_infraspecies = arcpy.Parameter()

    param_table.value = "BIOTICS_ELEMENT_NATIONAL"
    param_sql.value = "national_scientific_name = 'Abronia umbellata'"
    param_infraspecies = "Yes"

    parameters = [param_table, param_sql, param_infraspecies]

    # Run the tool using the parameters
    sst.run_tool(parameters, None)
