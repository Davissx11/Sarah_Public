import unittest

from dash.open_meteo import open_meteo_fetch_forecast, zip_to_coords


class OpenMeteoTest(unittest.TestCase):

    def test_zip_to_coords(self) -> None:
        lat, lng = zip_to_coords("94025")
        self.assertEqual(37.45, lat)
        self.assertEqual(-122.17, lng)

        self.assertEqual(
            (37.65, -122.42),
            zip_to_coords("94080"),
        )

    def test_logan(self) -> None:
        """Verify that leading zero works fine, for BOS airport."""
        self.assertEqual(
            (42.36, -71.01),
            zip_to_coords("02128"),
        )

    def test_fetch(self) -> None:
        d = open_meteo_fetch_forecast("94080")
        self.assertEqual(168, len(d))
