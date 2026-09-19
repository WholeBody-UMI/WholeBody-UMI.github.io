"""HTTP contract tests for the local video server. Run: python3 -m unittest discover -s tests"""

from functools import partial
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest

from scripts.serve import MediaHandler


class QuietHandler(MediaHandler):
    def log_message(self, *args):
        pass


class MediaServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = TemporaryDirectory()
        cls.data = bytes(range(256)) * 16
        Path(cls.folder.name, "video.mp4").write_bytes(cls.data)
        Path(cls.folder.name, "empty.mp4").touch()
        handler = partial(QuietHandler, directory=cls.folder.name)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = Thread(target=cls.server.serve_forever, kwargs={"poll_interval": 0.01})
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()
        cls.folder.cleanup()

    def request(self, range_header=None, method="GET", path="/video.mp4?v=audio"):
        connection = HTTPConnection(*self.server.server_address, timeout=3)
        headers = {"Range": range_header} if range_header else {}
        connection.request(method, path, headers=headers)
        response = connection.getresponse()
        result = response.status, {name.lower(): value for name, value in response.getheaders()}, response.read()
        connection.close()
        return result

    def test_full_file(self):
        status, headers, body = self.request()
        self.assertEqual(status, 200)
        self.assertEqual(body, self.data)
        self.assertEqual(headers["accept-ranges"], "bytes")
        self.assertEqual(headers["content-type"], "video/mp4")

    def test_ranges_return_exact_bytes(self):
        for value, start, end in [("bytes=0-1023", 0, 1023), ("bytes=2048-", 2048, 4095),
                                  ("bytes=-512", 3584, 4095), ("bytes=4000-9999", 4000, 4095),
                                  ("bytes=-9999", 0, 4095), ("bytes=0-0", 0, 0)]:
            with self.subTest(value=value):
                status, headers, body = self.request(value)
                self.assertEqual(status, 206)
                self.assertEqual(headers["content-range"], f"bytes {start}-{end}/4096")
                self.assertEqual(int(headers["content-length"]), end - start + 1)
                self.assertEqual(body, self.data[start:end + 1])

    def test_unsatisfiable_ranges(self):
        for value in ["bytes=4096-", "bytes=10-5", "bytes=-0"]:
            with self.subTest(value=value):
                status, headers, body = self.request(value)
                self.assertEqual(status, 416)
                self.assertEqual(headers["content-range"], "bytes */4096")
                self.assertEqual(body, b"")

    def test_range_head(self):
        status, headers, body = self.request("bytes=200-300", method="HEAD")
        self.assertEqual(status, 206)
        self.assertEqual(headers["content-length"], "101")
        self.assertEqual(body, b"")

    def test_empty_file(self):
        status, headers, body = self.request("bytes=0-", path="/empty.mp4")
        self.assertEqual(status, 416)
        self.assertEqual(headers["content-range"], "bytes */0")

    def test_unsupported_ranges_fall_back_to_full_file(self):
        for value in ["bytes=0-1,10-20", "bytes=-", "items=1-2"]:
            with self.subTest(value=value):
                status, _, body = self.request(value)
                self.assertEqual(status, 200)
                self.assertEqual(body, self.data)


if __name__ == "__main__":
    unittest.main()
