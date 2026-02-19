"""Tests for scripts/ — validate.py, version_bump.py"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate
import version_bump

# --------------------
# helpers
# --------------------


def _make_skill(root, name, *, version="0.1.0", category="development", frontmatter=None):
    skill_dir = root / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    if frontmatter is None:
        frontmatter = (
            f"---\nname: {name}\ndescription: Test skill\n"
            f"version: {version}\ncategory: {category}\n---\n\n## Instructions\nTODO\n"
        )
    (skill_dir / "SKILL.md").write_text(frontmatter)


class _TmpDirMixin:
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


# --------------------
# validate.py: parse_frontmatter
# --------------------


class TestParseFrontmatter(_TmpDirMixin, unittest.TestCase):
    def _write(self, content):
        p = self.tmpdir / "SKILL.md"
        p.write_text(content)
        return p

    def test_valid(self):
        fm = validate.parse_frontmatter(
            self._write("---\nname: test\ndescription: hello\n---\n\n## Body\n")
        )
        self.assertEqual(fm["name"], "test")
        self.assertEqual(fm["description"], "hello")

    def test_no_frontmatter(self):
        self.assertEqual(
            validate.parse_frontmatter(self._write("# No frontmatter\n")), {}
        )

    def test_unclosed(self):
        self.assertEqual(
            validate.parse_frontmatter(self._write("---\nname: test\n")), {}
        )

    def test_quoted_value(self):
        fm = validate.parse_frontmatter(
            self._write('---\ndescription: "hello world"\n---\n')
        )
        self.assertEqual(fm["description"], "hello world")

    def test_single_quoted_value(self):
        fm = validate.parse_frontmatter(
            self._write("---\ndescription: 'hello world'\n---\n")
        )
        self.assertEqual(fm["description"], "hello world")


# --------------------
# validate.py: full validation
# --------------------


class TestValidation(_TmpDirMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        validate.ROOT = self.tmpdir
        validate.SKILLS_DIR = self.tmpdir / "skills"

    def _run(self):
        validate.errors = []
        validate.validate_skills()
        return validate.errors

    def test_valid_structure(self):
        _make_skill(self.tmpdir, "my-skill")
        self.assertEqual(self._run(), [])

    def test_missing_skills_dir(self):
        errors = self._run()
        self.assertTrue(any("skills/" in e for e in errors))

    def test_bad_version_format(self):
        _make_skill(self.tmpdir, "my-skill", version="bad")
        errors = self._run()
        self.assertTrue(any("not semantic" in e for e in errors))

    def test_missing_skill_md(self):
        (self.tmpdir / "skills" / "empty-skill").mkdir(parents=True)
        errors = self._run()
        self.assertTrue(any("missing SKILL.md" in e for e in errors))

    def test_missing_frontmatter_field(self):
        _make_skill(
            self.tmpdir, "my-skill",
            frontmatter="---\nname: test\n---\n\n## Body\n",
        )
        errors = self._run()
        self.assertTrue(any("description" in e for e in errors))

    def test_non_kebab_folder(self):
        _make_skill(self.tmpdir, "BadName")
        errors = self._run()
        self.assertTrue(any("not kebab-case" in e for e in errors))


# --------------------
# version_bump.py
# --------------------


class TestVersionBump(unittest.TestCase):
    def test_bump_patch(self):
        self.assertEqual(version_bump.bump_patch("0.1.0"), "0.1.1")

    def test_high_patch(self):
        self.assertEqual(version_bump.bump_patch("1.2.99"), "1.2.100")

    def test_zero(self):
        self.assertEqual(version_bump.bump_patch("0.0.0"), "0.0.1")


class TestParseFrontmatterVersion(unittest.TestCase):
    def test_valid(self):
        text = "---\nname: test\nversion: 1.2.3\n---\n\n## Body\n"
        self.assertEqual(version_bump.parse_frontmatter_version(text), "1.2.3")

    def test_no_frontmatter(self):
        self.assertIsNone(version_bump.parse_frontmatter_version("# No frontmatter"))

    def test_no_version_field(self):
        text = "---\nname: test\n---\n"
        self.assertIsNone(version_bump.parse_frontmatter_version(text))


class TestUpdateFrontmatterVersion(_TmpDirMixin, unittest.TestCase):
    def test_replaces_version(self):
        p = self.tmpdir / "SKILL.md"
        p.write_text("---\nname: test\nversion: 0.0.1\n---\n\n## Body\n")
        version_bump.update_frontmatter_version(p, "0.0.2")
        self.assertIn("version: 0.0.2", p.read_text())
        self.assertNotIn("0.0.1", p.read_text())

    def test_preserves_body(self):
        p = self.tmpdir / "SKILL.md"
        p.write_text("---\nname: test\nversion: 1.0.0\n---\n\n## Instructions\nDo stuff\n")
        version_bump.update_frontmatter_version(p, "1.0.1")
        self.assertIn("## Instructions\nDo stuff", p.read_text())


if __name__ == "__main__":
    unittest.main()
