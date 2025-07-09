from qgis.core import QgsRasterLayer, QgsVectorLayer


def load_raster(path: str, layer_name: str):
    layer = QgsRasterLayer(path, layer_name)
    if not layer.isValid():
        raise Exception(f"Failed to load raster: {layer_name}")
    print(f"{layer_name} loaded.")
    return layer


def load_flood_points(path: str, layer_name: str):
    layer = QgsVectorLayer(path, layer_name, "ogr")
    if not layer.isValid():
        raise Exception(f"Failed to load vector: {layer_name}")
    print(f"{layer_name} loaded.")
    return layer
