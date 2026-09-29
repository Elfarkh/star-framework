import numpy as np

from ...core.raster import Raster
from ...core.qa_mask import QAMask
from ..landsat_scene import LandsatScene

from .metadata import (
    REFLECTANCE_SCALE,
    REFLECTANCE_OFFSET,
    TEMPERATURE_SCALE,
    TEMPERATURE_OFFSET,
)

class LandsatProcessing:
    """
    Landsat processing operations.
    """

    def _reflectance(
            self,
            scene: LandsatScene,
            band: str,
        ) -> Raster:
            """
            Read a surface reflectance band.
            """
    
            raster = self.read(scene, band)
    
            reflectance = (
                raster.data.astype("float32")
                * REFLECTANCE_SCALE
                + REFLECTANCE_OFFSET
            )
    
            reflectance[reflectance <= 0] = np.nan
    
            return Raster(
                data=reflectance,
                profile=raster.profile,
            )
        
    def usgs_lst(
        self,
        scene: LandsatScene,
    ) -> Raster:
        """
        Read the Landsat surface temperature band.
        """

        raster = self.read(scene, "lwir11")

        temperature = (
            raster.data.astype("float32")
            * TEMPERATURE_SCALE
            + TEMPERATURE_OFFSET
        )

        temperature[temperature <= 149.0] = np.nan

        return Raster(
            data=temperature,
            profile=raster.profile,
        )
    
    def ndvi(self, scene: LandsatScene) -> Raster:
        """
        Compute NDVI from a Landsat scene.
        """

        red = self._reflectance(scene, "red")

        nir = self._reflectance(scene, "nir08")

        return (nir - red) / (nir + red)

    def qa_mask(self, scene: LandsatScene) -> Raster:
        """
        Read the Landsat QA_PIXEL band.
        """

        qa = self.read(scene, "qa_pixel")

        bits = qa.data.astype("uint16")

        cloud = (bits & (1 << 3)) != 0
        shadow = (bits & (1 << 4)) != 0
        snow = (bits & (1 << 5)) != 0
        water = (bits & (1 << 7)) != 0

        return QAMask(
            cloud=Raster(
                data=cloud,
                profile=qa.profile,
            ),
            shadow=Raster(
                data=shadow,
                profile=qa.profile,
            ),
            snow=Raster(
                data=snow,
                profile=qa.profile,
            ),
            water=Raster(
                data=water,
                profile=qa.profile,
            ),
        )