"""
STAC catalog interface.
"""

from pystac_client import Client
from datetime import datetime


class STAC:
    """
    Interface to a STAC catalog.
    """

    CATALOG_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

    def __init__(self):
        """Initialize the STAC catalog."""

        self._catalog = self._connect()

    def _connect(self):
        """
        Connect to the STAC catalog.
        """

        return Client.open(self.CATALOG_URL)

    def search(
            self,
            collection: str,
            geometry: list[float],
            start_date: datetime,
            end_date: datetime,
    ):
        """
        Search a STAC collection.
        """

        search = self._catalog.search(
            collections=[collection],
            intersects=geometry.__geo_interface__,
            datetime=f"{start_date.isoformat()}/{end_date.isoformat()}",
        )

        return list(search.items())
