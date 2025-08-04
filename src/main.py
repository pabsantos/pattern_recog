import os

from qgis.core import QgsApplication

from flood_classification import (
    check_resolution_and_crs,
    load_flood_points,
    load_raster,
    raster_to_dataframe,
    transform_to_raster,
    create_final_dataframe,
    calculate_distance_to_features,
    transform_vector_to_binary_raster
)

os.environ["QT_QPA_PLATFORM"] = "offscreen" 


def main():
    QgsApplication.setPrefixPath(
        "C:/OSGeo4W/bin", True
    )  # Change path based on qgis instalattion and system
    qgs = QgsApplication([], False)
    qgs.initQgis()

    dtm = None
    lulc = None
    flood_points = None
    flood_raster = None
    river_layer = None
    tributaries_layer = None
    basin_layer = None

    target_resolution = 50.0
    print(f"Processing data with a target resolution of {target_resolution}m.")

    try:
        path_dtm = "data/DigitalTerrainModel/DTM_TTI_buffer_1km_FILLED.tif"
        path_lulc = "data/LandUseLandCover/LULC_10m_TTI_clipped_1km.tif"
        path_floods = "data/SHP_floods_2019/Ocorrencias_Alag_2019.shp"
        path_river = "data/SHP_Tamanduatei/Rio_Tamanduatei.shp" 
        path_tributaries = "data/SHP_Tamanduatei/Afluentes_Tamanduatei.shp"
        path_basin = "data/SHP_Tamanduatei/Bacia_Tamanduatei.shp"

        dtm = load_raster(path_dtm, "dtm")
        lulc = load_raster(path_lulc, "lulc")
        flood_points = load_flood_points(path_floods, "flood_points")
        river_layer = load_flood_points(path_river, "river_layer")
        tributaries_layer = load_flood_points(path_tributaries, "tributaries_layer")
        basin_layer = load_flood_points(path_basin, "basin_layer")


        os.makedirs("temp", exist_ok=True)
        path_resampled_dtm = "temp/resampled_dtm.tif"
        path_resampled_lulc = "temp/resampled_lulc.tif"
        path_temp_flood = "temp/flood_raster.tif"
        path_temp_river_dist = "temp/river_dist.tif"
        path_temp_tributaries_dist = "temp/tributaries_dist.tif"
        path_temp_basin = "temp/basin_binary.tif"

        dtm, lulc = check_resolution_and_crs(
            dtm, lulc, path_dtm, path_lulc, path_resampled_dtm, path_resampled_lulc, target_resolution
        )
        flood_raster = transform_to_raster(flood_points, dtm, path_temp_flood, target_resolution)
        river_raster = calculate_distance_to_features(river_layer, dtm, path_temp_river_dist, target_resolution)
        tributaries_raster = calculate_distance_to_features(tributaries_layer, dtm, path_temp_tributaries_dist, target_resolution)
        basin_raster = transform_vector_to_binary_raster(basin_layer, dtm, path_temp_basin, target_resolution)

        dtm_df = raster_to_dataframe(dtm)
        lulc_df = raster_to_dataframe(lulc)
        flood_df = raster_to_dataframe(flood_raster)
        river_df = raster_to_dataframe(river_raster)
        tributaries_df = raster_to_dataframe(tributaries_raster)
        basin_df = raster_to_dataframe(basin_raster)

        final_df = create_final_dataframe(dtm_df, lulc_df, flood_df, river_df, tributaries_df, basin_df)

        final_df.to_parquet("temp/final_data.parquet")

        print("All files exported.")

    finally:
        del dtm, lulc, flood_points, flood_raster
        qgs.exitQgis()
        print("QGIS exited.")


if __name__ == "__main__":
    main()
