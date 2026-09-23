import unittest
from wetu_studio.product_studio import ProductStudio

class ProductStudioTests(unittest.TestCase):
    def test_all_studios_are_available(self):
        ids = {x["studio_id"] for x in ProductStudio().templates()}
        self.assertEqual(ids, {"advertising", "film", "series"})

    def test_plan_contains_required_stages(self):
        plan = ProductStudio().plan("series", "Test", "Episode")
        self.assertIn("continuity", plan["ready_for"])
        self.assertIn("postproduction", plan["ready_for"])
