"""서버를 띄워 실제 HTTP로 확인하는 최소 테스트. 실행: python -m unittest test_app.py"""
import json, os, subprocess, sys, time, unittest, urllib.request

PORT = 3917

class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "app.py")], env={**os.environ, "PORT": str(PORT)}, stdout=subprocess.PIPE)
        cls.p.stdout.readline(); time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.p.terminate(); cls.p.wait(); cls.p.stdout.close()

    def req(self, path, data=None):
        r = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(data).encode() if data is not None else None, headers={"content-type": "application/json"})
        try:
            with urllib.request.urlopen(r) as res:
                return res.status, json.loads(res.read())
        except urllib.error.HTTPError as e:
            with e:
                return e.code, json.loads(e.read())

    def test_health(self):
        self.assertEqual(self.req("/api/health"), (200, {"ok": True}))

    def test_add_and_list(self):
        code, item = self.req("/api/items", {"text": "a"})
        self.assertEqual(code, 201)
        self.assertIn(item, self.req("/api/items")[1])

    def test_rejects_empty(self):
        self.assertEqual(self.req("/api/items", {"text": " "})[0], 400)

if __name__ == "__main__":
    unittest.main()
