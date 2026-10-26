import unittest
from unittest.mock import patch

from h3_cloud_mcp import comfy
from h3_cloud_mcp.workflow import build_t2va


class WorkflowTests(unittest.TestCase):
    def test_graph_connects_generated_video_and_audio(self):
        graph = build_t2va("A rainy city street", seed=42)
        self.assertEqual(graph["5"]["inputs"]["length"], 124)
        self.assertEqual(graph["12"]["inputs"]["samples"], ["10", 0])
        self.assertEqual(graph["13"]["inputs"]["audio"], ["12", 0])
        self.assertEqual(graph["14"]["inputs"]["video"], ["13", 0])
        self.assertEqual(graph["8"]["inputs"]["noise_seed"], 42)
        for node in graph.values():
            for value in node["inputs"].values():
                if isinstance(value, list):
                    self.assertIn(value[0], graph)

    def test_rejects_expensive_or_invalid_shapes(self):
        for kwargs in ({"width": 1281}, {"frames": 125}, {"steps": 51}, {"seed": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_t2va("test", **kwargs)

    def test_requires_private_tunnel(self):
        with patch.dict("os.environ", {"COMFYUI_URL": "http://example.com:8188"}):
            with self.assertRaises(ValueError):
                comfy.base_url()

    def test_reads_completed_video_and_queue(self):
        job = "a1b2-c3"
        with patch.object(comfy, "request", return_value={job: {"status": {"status_str": "success"}, "outputs": {"14": {"videos": [{"filename": "clip.mp4", "type": "output"}]}}}}):
            self.assertEqual(comfy.status(job)["videos"][0]["filename"], "clip.mp4")
        with patch.object(comfy, "request", side_effect=[{}, {"queue_running": [[0, job, {}]]}]):
            self.assertEqual(comfy.status(job)["state"], "running")


if __name__ == "__main__":
    unittest.main()
