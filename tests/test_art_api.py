import unittest
from unittest.mock import patch

from h3_cloud_mcp import art_api

TASK = "2a25da1d-39ad-495c-8dac-bae8e8f6b1a1"


class ArtApiTests(unittest.TestCase):
    def setUp(self):
        art_api._submitted = 0

    def test_quote_and_input_bounds(self):
        self.assertEqual(art_api.quote()["worst_observed_cny"], 0.2)
        self.assertEqual(art_api.quote(5, "768p竖")["worst_observed_cny"], 0.25)
        for args in ((0, "480p横"), (16, "480p横"), (5, "1080p横")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                art_api.quote(*args)

    def test_paid_generation_requires_opt_in_and_limits_repeat(self):
        with patch.dict("os.environ", {"AUTODL_ART_TOKEN": "test-token"}, clear=True):
            with patch.object(art_api, "_api") as api, self.assertRaises(RuntimeError):
                art_api.generate("a scene")
            api.assert_not_called()
        env = {"AUTODL_ART_TOKEN": "test-token", "H3_ART_ENABLE_PAID": "1"}
        with patch.dict("os.environ", env, clear=True), patch.object(art_api, "_api", return_value={"task_id": TASK, "status": "QUEUED"}) as api:
            result = art_api.generate("a scene")
            self.assertEqual(result["task_id"], TASK)
            self.assertEqual(api.call_count, 1)
            with self.assertRaises(RuntimeError):
                art_api.generate("another scene")
            self.assertEqual(api.call_count, 1)

    def test_guard_uses_peak_price_and_no_post_retry(self):
        env = {"AUTODL_ART_TOKEN": "test-token", "H3_ART_ENABLE_PAID": "1"}
        with patch.dict("os.environ", env, clear=True), patch.object(art_api, "_api") as api:
            with self.assertRaises(ValueError):
                art_api.generate("scene", duration=7)
            api.assert_not_called()
            api.side_effect = TimeoutError("unknown outcome")
            with self.assertRaises(TimeoutError):
                art_api.generate("scene")
            with self.assertRaises(RuntimeError):
                art_api.generate("scene")
            self.assertEqual(api.call_count, 1)

    def test_status_and_download_never_echo_signed_url(self):
        data = {"status": "SUCCESS", "results": [{"type": "video", "url": "https://cdn.example/video.mp4?secret=signed"}]}
        with patch.object(art_api, "_api", return_value=data):
            self.assertEqual(art_api.status(TASK)["video_count"], 1)
            self.assertNotIn("signed", str(art_api.status(TASK)))
        with self.assertRaises(ValueError):
            art_api.status("../../other")
        with self.assertRaises(ValueError):
            art_api._public_https("http://127.0.0.1/video.mp4")
        art_api._public_https("https://cg-comfyui-prod.tos-cn-beijing.volces.com/video.mp4")


if __name__ == "__main__":
    unittest.main()
