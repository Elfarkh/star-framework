"""
Landsat sensor module.

This module provides the Landsat class used throughout the
STAR Framework.
"""


class Landsat:
    """
    Interface to the Landsat archive.

    This class will be responsible for:

    - searching Landsat scenes,
    - downloading Landsat products,
    - reading Landsat metadata.

    The implementation will be added progressively.
    """

    def __repr__(self):
        return "Landsat()"
