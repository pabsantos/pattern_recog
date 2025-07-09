from qgis.core import QgsApplication

from flood_classification import load_flood_points, load_raster


def main():
    QgsApplication.setPrefixPath(
        "/Applications/QGIS-LTR.app/Contents/MacOS", True
    )  # Change path based on qgis instalattion and system
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        path_dtm = "data/dtm/DTM_TTI_buffer_1km_FILLED.tif"
        path_lulc = "data/lulc/LULC_10m_TTI_clipped_1km.tif"
        path_floods = "data/floods/Ocorrencias_Alag_2019.shp"

        dtm = load_raster(path_dtm, "dtm")
        lulc = load_raster(path_lulc, "lulc")
        flood_points = load_flood_points(path_floods, "flood_points")

    finally:
        del dtm, lulc, flood_points
        qgs.exitQgis()
        print("QGIS exited.")


if __name__ == "__main__":
    main()
