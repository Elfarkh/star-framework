from pystac_client import Client

catalog = Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1"
)

search = catalog.search(
    collections=["landsat-c2-l2"],
    limit=1,
)

item = next(search.items())

print(item.id)

print()

print(item.properties.keys())
