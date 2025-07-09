from qgis.core import QgsRasterLayer, QgsVectorLayer


def load_raster(path: str, layer_name: str):
    """
    Loads a raster file as a QgsRasterLayer.

    Args:
        path (str): The file path to the raster file.
        layer_name (str): The name to assign to the loaded raster layer.

    Returns:
        QgsRasterLayer: The loaded raster layer object.

    Raises:
        Exception: If the raster layer fails to load.

    Prints:
        Confirmation message indicating successful loading of the raster layer.
    """
    layer = QgsRasterLayer(path, layer_name)
    if not layer.isValid():
        raise Exception(f"Failed to load raster: {layer_name}")
    print(f"{layer_name} loaded.")
    return layer


def load_flood_points(path: str, layer_name: str):
    """
    Loads a vector layer of flood points using the specified file path and layer name.

    Args:
        path (str): The file path to the vector data source.
        layer_name (str): The name to assign to the loaded layer.

    Returns:
        QgsVectorLayer: The loaded vector layer object.

    Raises:
        Exception: If the vector layer fails to load.

    Prints:
        Confirmation message indicating successful loading of the layer.
    """
    layer = QgsVectorLayer(path, layer_name, "ogr")
    if not layer.isValid():
        raise Exception(f"Failed to load vector: {layer_name}")
    print(f"{layer_name} loaded.")
    return layer
