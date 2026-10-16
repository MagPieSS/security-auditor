import unittest

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from mask_secrets import mask_line  # noqa: E402

# Fake values shaped like real ones. None of these are live.
OPENAI_KEY = "sk-proj-Ab3dEf6hIj9kLm2nOp5qRs8tUv1wXy4z"
AWS_ID = "AKIAIOSFODNN7EXAMPLE"


class MaskTest(unittest.TestCase):
    def test_long_key_keeps_only_last_4(self):
        out = mask_line(f'const key = "{OPENAI_KEY}";')
        self.assertNotIn(OPENAI_KEY, out)
        self.assertNotIn(OPENAI_KEY[:-4], out)
        self.assertIn("****" + OPENAI_KEY[-4:], out)

    def test_grep_location_stays_readable(self):
        out = mask_line(f"src/lib/openai.ts:12:  apiKey: '{OPENAI_KEY}',")
        self.assertTrue(out.startswith("src/lib/openai.ts:12:"))
        self.assertNotIn(OPENAI_KEY, out)

    def test_short_named_password_is_fully_hidden(self):
        out = mask_line("DB_PASSWORD=hunter22")
        self.assertNotIn("hunter22", out)
        self.assertNotIn("er22", out)

    def test_password_inside_url_is_hidden(self):
        out = mask_line("DATABASE_URL=postgres://admin:hunter22@db.example.com/app")
        self.assertNotIn("hunter22", out)

    def test_aws_access_key_id_is_hidden(self):
        out = mask_line(f"aws_access_key_id = {AWS_ID}")
        self.assertNotIn(AWS_ID, out)

    def test_gitleaks_json_secret_field_is_hidden(self):
        out = mask_line(f'  "Secret": "{OPENAI_KEY}",')
        self.assertNotIn(OPENAI_KEY, out)

    def test_plain_code_is_untouched(self):
        line = "export default function handler(req, res) {"
        self.assertEqual(mask_line(line), line)


if __name__ == "__main__":
    unittest.main()
