import xarray as xr
import json
import numpy as np

# ============================================================
# CONFIGURACIÓN
# ============================================================

ruta_nc = "data/WRFDETAR_01H_20251126_18_010.nc"  # Cambiar ruta
variable = "PP"  # Precipitación
output = "precipitacion.geojson"

# ============================================================
# ABRIR ARCHIVO NetCDF
# ============================================================

ds = xr.open_dataset(ruta_nc)

if variable not in ds.variables:
    raise ValueError(f"⚠ La variable '{variable}' no existe en el archivo.")

lat = ds["lat"].values
lon = ds["lon"].values
pp = ds[variable]

# WRF tiene lat/lon en 2D
ny, nx = lat.shape

# Tiempo de validez
if "time" in ds:
    tiempo = ds["time"].values
    valid_time = np.datetime_as_string(tiempo[0], unit='s')
else:
    valid_time = None

# ============================================================
# GENERAR FEATURES SOLO PARA PRECIPITACIÓN > 0
# ============================================================

features = []

# PP puede ser 2D (solo 1 tiempo) o 3D (time, y, x)
if pp.ndim == 3:
    campo = pp.values[0, :, :]
else:
    campo = pp.values

for i in range(ny):
    for j in range(nx):

        valor = float(campo[i, j])

        if np.isnan(valor) or valor <= 0:
            continue

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(lon[i, j]), float(lat[i, j])]
            },
            "properties": {
                "PP_mm": valor,
                "valid_time": valid_time
            }
        })

# ============================================================
# EXPORTAR GEOJSON
# ============================================================

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open(output, "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False)

print(f"✔ GeoJSON generado → {output}")
print(f"✔ Puntos con precipitación: {len(features)}")
