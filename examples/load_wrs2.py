from star.sensors.landsat import Landsat

landsat = Landsat()

grid = landsat._load_wrs2_grid()

print(list(grid.columns))

print()

print(grid.crs)

print()

print(f"Number of tiles: {len(grid)}")
