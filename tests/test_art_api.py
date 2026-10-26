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

    def test_all_reviewed_workflows_are_listed_and_quoteable(self):
        workflows = art_api.list_workflows()
        self.assertEqual(len(workflows), 18)
        self.assertEqual(len({item["workflow_id"] for item in workflows}), 18)
        for item in workflows:
            with self.subTest(workflow=item["workflow_id"]):
                quote = art_api.quote_workflow(item["workflow_id"], 1)
                self.assertGreater(quote["estimated_cny"], 0)
                self.assertIn(quote["resolution"], item["resolutions"])
        self.assertEqual(art_api.quote_workflow("minimax_h3_b99_001", 5)["worst_observed_cny"], 0.30)
        self.assertEqual(art_api.quote_workflow("minimax_h3_z0901", 5, "768p横")["provider_resolution"],
                         "768p横(1344*768)")
        self.assertEqual(art_api.quote_workflow("minimax_h3_803", 5, "768p横")["provider_resolution"],
                         "768p横(1376*768)")

    def test_all_workflow_payloads_can_be_built_without_a_network_call(self):
        workflows = art_api.list_workflows()
        env = {"AUTODL_ART_TOKEN": "test-token", "H3_ART_ENABLE_PAID": "1",
               "H3_ART_MAX_ESTIMATED_CNY": "50", "H3_ART_MAX_TASKS_PER_SESSION": "18"}
        with patch.dict("os.environ", env, clear=True), patch.object(
                art_api, "_api", return_value={"task_id": TASK, "status": "QUEUED"}) as api:
            for item in workflows:
                with self.subTest(workflow=item["workflow_id"]):
                    images = ["https://images.example/a.png"] * item["images"]["min"]
                    audios = ["https://audio.example/a.mp3"] * item["audios"]["min"]
                    kwargs = {"images": images, "audios": audios}
                    if item["first_last"]:
                        kwargs.update(first_frame="https://images.example/first.png",
                                      last_frame="https://images.example/last.png")
                    result = art_api.generate_workflow(item["workflow_id"], "scene" if
                                                       item["workflow_id"] != "minimax_h3_image_audio_to_video" else "",
                                                       duration=1, **kwargs)
                    self.assertEqual(result["workflow_id"], item["workflow_id"])
                    self.assertEqual(api.call_args.args[1],
                                     f"/api/v1/comfyui/comfyui_workflow/{item['workflow_id']}")
            self.assertEqual(api.call_count, 18)

    def test_first_last_payload_and_shared_paid_limit(self):
        env = {"AUTODL_ART_TOKEN": "test-token", "H3_ART_ENABLE_PAID": "1",
               "H3_ART_MAX_ESTIMATED_CNY": "0.50"}
        with patch.dict("os.environ", env, clear=True), patch.object(
                art_api, "_api", return_value={"task_id": TASK, "status": "QUEUED"}) as api:
            result = art_api.generate_workflow(
                "minimax_h3_lightx2v", "glass whale", duration=5, resolution="480p横",
                first_frame="https://images.example/first.png",
                last_frame="https://images.example/last.webp")
            self.assertEqual(result["workflow_id"], "minimax_h3_lightx2v")
            args, kwargs = api.call_args
            self.assertEqual(args[:2], ("POST", "/api/v1/comfyui/comfyui_workflow/minimax_h3_lightx2v"))
            self.assertEqual(kwargs["body"], {
                "prompt": "glass whale", "duration": 5, "resolution": "480p横",
                "first_frame": "https://images.example/first.png",
                "last_frame": "https://images.example/last.webp"})
            with self.assertRaises(RuntimeError):
                art_api.generate("second task")
            self.assertEqual(api.call_count, 1)

    def test_reference_and_lipsync_payloads_use_their_own_schemas(self):
        env = {"AUTODL_ART_TOKEN": "test-token", "H3_ART_ENABLE_PAID": "1",
               "H3_ART_MAX_ESTIMATED_CNY": "1", "H3_ART_MAX_TASKS_PER_SESSION": "2"}
        with patch.dict("os.environ", env, clear=True), patch.object(
                art_api, "_api", return_value={"task_id": TASK, "status": "QUEUED"}) as api:
            art_api.generate_workflow("minimax_h3_803", "scene", 5, "1088p横",
                                      images=["https://images.example/a.jpg"],
                                      audios=["https://audio.example/a.mp3"], mode="高质模式")
            body = api.call_args.kwargs["body"]
            self.assertEqual(body["resolution"], "1088p横(1920*1088)")
            self.assertEqual(body["ref_image_0"], "https://images.example/a.jpg")
            self.assertEqual(body["ref_audio_0"], "https://audio.example/a.mp3")
            self.assertEqual(body["mode"], "高质模式")
            art_api.generate_workflow("minimax_h3_image_audio_to_video", duration=5,
                                      images=["https://images.example/a.jpg"],
                                      audios=["https://audio.example/a.mp3"])
            body = api.call_args.kwargs["body"]
            self.assertEqual(body["audio_duration"], 5)
            self.assertNotIn("duration", body)
            self.assertNotIn("prompt", body)

    def test_invalid_workflow_media_and_budget_never_submit(self):
        env = {"AUTODL_ART_TOKEN": "test-token", "H3_ART_ENABLE_PAID": "1"}
        invalid = [
            ("unknown", {"prompt": "scene"}),
            ("minimax_h3_lightx2v", {"prompt": "scene"}),
            ("minimax_h3_lightx2v_v5", {"prompt": "scene", "images": ["http://images.example/a.jpg"]}),
            ("minimax_h3_lightx2v_v5", {"prompt": "scene", "images": ["https://127.0.0.1/a.jpg"]}),
            ("minimax_h3_z0903", {"prompt": "scene", "images": ["https://images.example/a.jpg"]}),
            ("minimax_h3_b99_003_12s", {"prompt": "scene", "duration": 13,
                                          "images": ["https://images.example/a.jpg"]}),
            ("minimax_h3_b99_001", {"prompt": "scene", "resolution": "480p横"}),
            ("minimax_h3_801", {"prompt": "scene", "images": ["https://images.example/a.jpg"],
                                 "mode": "unknown"}),
            ("minimax_h3_image_audio_to_video", {"prompt": "ignored",
                                                  "images": ["https://images.example/a.jpg"],
                                                  "audios": ["https://audio.example/a.mp3"]}),
        ]
        with patch.dict("os.environ", env, clear=True), patch.object(art_api, "_api") as api:
            for workflow_id, kwargs in invalid:
                with self.subTest(workflow=workflow_id, kwargs=kwargs), self.assertRaises(ValueError):
                    art_api.generate_workflow(workflow_id, **kwargs)
            with self.assertRaises(ValueError):
                art_api.generate_workflow("minimax_h3_z0901", "scene", 5, "1440p横")
            api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
