import unittest

from ddd.model.performance import Performance
from ddd.utils import get_project_root

PROJECT_ROOT = get_project_root()

# TODO: move to better location
FLAT_RINGERS_TEST_DATA = {
    "performances": {
        "@xmlns": "http://bb.ringingworld.co.uk/NS/performances#",
        "performance": [
            {
                "@xmlns": "http://bb.ringingworld.co.uk/NS/performances#",
                "@id": "P1620738",
                "association": "Lancashire Association",
                "place": {
                    "@towerbase-id": "3861",
                    "@dove-tower-id": "16797",
                    "place-name": [
                        {
                            "@type": "place",
                            "#text": "Pendleton"
                        },
                        {
                            "@type": "dedication",
                            "#text": "St Thomas"
                        },
                        {
                            "@type": "county",
                            "#text": "Greater Manchester"
                        }
                    ],
                    "ring": {
                        "@type": "tower",
                        "@dove-ring-id": "6798",
                        "@tenor": "18-0-10 in E"
                    }
                },
                "date": "2023-05-06",
                "title": {
                    "method": "Rounds and Called Changes"
                },
                "ringers": {
                    "ringer": [
                        "Eleanor Wood",
                        "Malcom Murphy",
                        "Beth Ingham",
                        "Ian Jorysz",
                        "Freja Steinke"
                    ]
                },
                "footnote": "Rung for the coronation of King Charles III.",
                "timestamp": "2023-05-07T15:24:53",
                "rwref": "5846a.487"
            }
        ]
    }
}

class TestPerformance(unittest.TestCase):
    def test_parse_flat_ringers(self) -> None:
        """TODO: test docstring"""
        raw_perf = FLAT_RINGERS_TEST_DATA["performances"]["performance"][0]
        modelled = Performance.model_validate(raw_perf)
        expected_ringers = [
            "Eleanor Wood",
            "Malcom Murphy",
            "Beth Ingham",
            "Ian Jorysz",
            "Freja Steinke"
        ]
        self.assertEqual(modelled.get_ringers(), expected_ringers)