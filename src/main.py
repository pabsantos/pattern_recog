from qgis.core import QgsApplication

from flood_classification import (
    check_resolution_and_crs,
    load_flood_points,
    load_raster,
    transform_to_raster,
)


def main():
    QgsApplication.setPrefixPath(
        "/Applications/QGIS-LTR.app/Contents/MacOS", True
    )  # Change path based on qgis instalattion and system
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        path_dtm = "data/dtm/DTM_TTI_buffer_1km_FILLED.tif"
        path_lulc = "data/lulc/lulc_utm.tif"
        path_floods = "data/floods/Ocorrencias_Alag_2019.shp"

        dtm = load_raster(path_dtm, "dtm")
        lulc = load_raster(path_lulc, "lulc")
        flood_points = load_flood_points(path_floods, "flood_points")

        path_temp_res = "temp/resample.tif"
        path_temp_flood = "temp/flood_raster.tif"

        dtm, lulc = check_resolution_and_crs(
            dtm, lulc, path_dtm, path_lulc, path_temp_res
        )
        flood_raster = transform_to_raster(flood_points, dtm, path_temp_flood)
    finally:
        del dtm, lulc, flood_points, flood_raster
        qgs.exitQgis()
        print("QGIS exited.")


if __name__ == "__main__":
    main()
