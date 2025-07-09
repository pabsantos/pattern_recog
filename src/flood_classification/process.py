import numpy as np
import pandas as pd
from osgeo import gdal
from qgis.core import QgsCoordinateReferenceSystem

from flood_classification import load_raster


def check_resolution_and_crs(
    raster1, raster2, path_raster1, path_raster2, resampled_path
):
    crs1 = raster1.crs().authid()
    crs2 = raster2.crs().authid()

    if crs1 != crs2:
        raise ValueError(f"CRS mismatch: {crs1} vs {crs2}")

    res1_x = raster1.rasterUnitsPerPixelX()
    res1_y = raster1.rasterUnitsPerPixelY()
    res2_x = raster2.rasterUnitsPerPixelX()
    res2_y = raster2.rasterUnitsPerPixelY()

    res1 = res1_x * res1_y
    res2 = res2_x * res2_y

    if abs(res1 - res2) > 1e-6:
        if res1 < res2:
            print("Second raster has higher sample.")
            # raster2 has higher resolution, resample it
            source = path_raster2
            ref = raster1
        else:
            print("First raster has higher sample.")
            source = path_raster1
            ref = raster2

        gdal.Warp(
            resampled_path,
            source,
            xRes=ref.rasterUnitsPerPixelX(),
            yRes=ref.rasterUnitsPerPixelY(),
            targetAlignedPixels=True,
            dstSRS=ref.crs().authid(),
            outputBounds=(
                ref.extent().xMinimum(),
                ref.extent().yMinimum(),
                ref.extent().xMaximum(),
                ref.extent().yMaximum(),
            ),
            resampleAlg="near",
            format="GTiff",
        )

        if res1 < res2:
            raster2 = load_raster(resampled_path, "aligned_raster")
        else:
            raster1 = load_raster(resampled_path, "aligned_raster")
    print("Resample finished.")
    return raster1, raster2


def transform_to_raster(vector_layer, reference_raster, output_path):
    gdal.Rasterize(
        output_path,
        vector_layer.source(),
        options=gdal.RasterizeOptions(
            format="GTiff",
            outputType=gdal.GDT_Byte,
            burnValues=[1],
            noData=0,
            initValues=[0],
            xRes=reference_raster.rasterUnitsPerPixelX(),
            yRes=reference_raster.rasterUnitsPerPixelY(),
            outputBounds=(
                reference_raster.extent().xMinimum(),
                reference_raster.extent().yMinimum(),
                reference_raster.extent().xMaximum(),
                reference_raster.extent().yMaximum(),
            ),
            targetAlignedPixels=True,
            outputSRS=reference_raster.crs().authid(),
            creationOptions=["COMPRESS=LZW"],
        ),
    )
    print("Point transformed to raster.")
    return load_raster(output_path, "flood_raster")


def raster_to_dataframe(raster_layer):
    provider = raster_layer.dataProvider()
    nodata = provider.sourceNoDataValue(1)
    extent = raster_layer.extent()
    width = raster_layer.width()
    height = raster_layer.height()
    block = provider.block(1, extent, width, height)

    array_2d = np.array(
        [[block.value(x, y) for x in range(width)] for y in range(height)]
    )

    flat_array = array_2d.flatten()

    if nodata is not None:
        flat_array = np.where(flat_array == nodata, np.nan, flat_array)

    x_origin = extent.xMinimum()
    y_origin = extent.yMaximum()
    pixel_width = raster_layer.rasterUnitsPerPixelX()
    pixel_height = raster_layer.rasterUnitsPerPixelY()

    x_coords = np.array(
        [x_origin + (i % width) * pixel_width for i in range(width * height)]
    )

    y_coords = np.array(
        [y_origin - (i // width) * pixel_height for i in range(width * height)]
    )

    df = pd.DataFrame({"value": flat_array, "x": x_coords, "y": y_coords})

    return df
