"""Filesystem and CLI contract tests; never invoke a model or hardware job."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "main-agent-workspace/assets"


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="codex migration ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "project with spaces"
        self.project.mkdir()

    def run_script(self, script, *args, expected=0, env=None):
        result = subprocess.run([sys.executable, "-B", str(ROOT / script), *map(str, args)],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def install(self, *extra, expected=0):
        return self.run_script("scripts/install_codex.py", "--project", self.project,
                               *extra, expected=expected)

    def base_workspace(self, roots=()):
        guidance = (ASSETS / "AGENTS.md.tmpl").read_text()
        for key, value in {"PROJECT_NAME": "Fixture", "ONE_SENTENCE_WHAT_THIS_PROJECT_IS": "Test workspace",
                           "RESOURCE_CAP": "One writer per root."}.items():
            guidance = guidance.replace(f"<{key}>", value)
        (self.project / "AGENTS.md").write_text(guidance)
        scripts = self.project / "scripts"
        scripts.mkdir(exist_ok=True)
        launcher = (ASSETS / "start-main.sh.tmpl").read_text()
        launcher = launcher.replace('  # "/abs/path/to/root"   # <name> (owner: <name>-owner)',
                                    "\n".join(f'  "{root}"' for root in roots))
        (scripts / "start-main.sh").write_text(launcher)

    def owner_workspace(self):
        owner_root = self.base / "external root"
        owner_root.mkdir()
        self.base_workspace([owner_root])
        for name in ("ONBOARDING.md", "HANDOFF.md"):
            (owner_root / name).write_text("Fixture state.\n")
        guidance = self.project / "AGENTS.md"
        guidance.write_text(guidance.read_text().replace("|---|---|---|---|---|",
            f"|---|---|---|---|---|\n| test-owner | {owner_root} | tests | none | fixture |", 1))
        agents = self.project / ".codex/agents"
        agents.mkdir(parents=True)
        definition = (ASSETS / "owner.toml.tmpl").read_text()
        for key, value in {"NAME": "test", "ONE_LINE_SCOPE": "tests", "ABSOLUTE_ROOT": str(owner_root),
                           "EXCLUDED_SCOPE": "nothing", "EXCLUSIONS": "nothing",
                           "WRITERS_RULE": "One writer.", "ROOT_SPECIFIC_RULE": "Use fixtures."}.items():
            definition = definition.replace(f"<{key}>", value)
        owner = agents / "test-owner.toml"
        owner.write_text(definition)
        return owner

    def check(self, expected=0):
        return self.run_script("main-agent-workspace/scripts/check_setup.py", self.project, expected=expected)

    def test_catalog_validation(self):
        result = self.run_script("scripts/validate_codex.py")
        self.assertIn("24 unique Codex skills", result.stdout)

    def test_install_dry_run_and_idempotence(self):
        self.install("--dry-run")
        self.assertFalse((self.project / ".agents").exists())
        self.install()
        links = list((self.project / ".agents/skills").iterdir())
        self.assertEqual(len(links), 24)
        self.assertTrue(all(p.is_symlink() and (p / "SKILL.md").is_file() for p in links))
        self.assertIn("0 links; 24 already current", self.install().stdout)

    def test_collision_preflight_preserves_everything(self):
        existing = self.project / ".agents/skills/writing-skills"
        existing.mkdir(parents=True)
        marker = existing / "user.txt"
        marker.write_text("keep")
        self.install(expected=1)
        self.assertEqual(marker.read_text(), "keep")
        self.assertEqual(list(existing.parent.iterdir()), [existing])

    def test_broken_symlink_is_a_collision(self):
        existing = self.project / ".agents/skills/writing-skills"
        existing.parent.mkdir(parents=True)
        existing.symlink_to("missing")
        self.install(expected=1)
        self.assertEqual(os.readlink(existing), "missing")

    def test_user_install_uses_home(self):
        env = dict(os.environ, HOME=str(self.base))
        self.run_script("scripts/install_codex.py", "--user", env=env)
        self.assertEqual(len(list((self.base / ".agents/skills").iterdir())), 24)

    def test_empty_workspace(self):
        self.base_workspace()
        self.assertIn("0 error(s) · 0 warning(s)", self.check().stdout)

    def test_owner_registration_and_inventory(self):
        owner = self.owner_workspace()
        (owner.parent / "reviewer.toml").write_text('name = "reviewer"\n')
        self.assertIn("All registries agree", self.check().stdout)
        report = json.loads(self.run_script("main-agent-workspace/scripts/inventory.py",
                                           self.project, "--json").stdout)
        self.assertTrue(report["suggested_mode"].startswith("Audit"))
        self.assertIn(".codex/agents (1 owner files)", report["root_markers"])

    def test_malformed_owner_is_reported_without_traceback(self):
        owner = self.owner_workspace()
        owner.write_text('name = "unfinished\n')
        result = self.check(expected=1)
        self.assertIn("invalid .codex/agents/test-owner.toml", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_agent_instructions(self):
        owner = self.owner_workspace()
        owner.write_text('name = "test-owner"\ndescription = "Test"\n')
        self.assertIn("developer_instructions", self.check(expected=1).stdout)

    def test_external_root_missing_from_launcher(self):
        self.owner_workspace()
        (self.project / "scripts/start-main.sh").write_text("SUBPROJECTS=(\n)\n")
        self.assertIn("missing from scripts/start-main.sh", self.check(expected=1).stdout)

    def test_nested_roots_need_scope_exclusions(self):
        parent = self.owner_workspace()
        child_root = self.base / "external root/child"
        child_root.mkdir()
        for name in ("ONBOARDING.md", "HANDOFF.md"):
            (child_root / name).write_text("Fixture state.\n")
        (parent.parent / "child-owner.toml").write_text(
            'name = "child-owner"\ndescription = "Child"\n'
            'developer_instructions = "Own the child directory."\n')
        guidance = self.project / "AGENTS.md"
        guidance.write_text(guidance.read_text().replace("|---|---|---|---|---|",
            f"|---|---|---|---|---|\n| child-owner | {child_root} | child | none | fixture |", 1))
        launcher = self.project / "scripts/start-main.sh"
        launcher.write_text(launcher.read_text().replace("SUBPROJECTS=(", f'SUBPROJECTS=(\n  "{child_root}"'))
        self.assertIn("does not exclude 'child'", self.check().stdout)
        parent.write_text(parent.read_text().replace("except nothing", "except child"))
        self.assertIn("0 warning(s)", self.check().stdout)

    def test_launcher_arguments_and_resume(self):
        binaries = self.base / "bin"
        binaries.mkdir()
        mock = binaries / "codex"
        mock.write_text(f"#!{sys.executable}\nimport json, os, sys\n"
                        "print(json.dumps({'args': sys.argv[1:], 'cwd': os.getcwd()}))\n")
        mock.chmod(0o755)
        env = dict(os.environ, PATH=str(binaries) + os.pathsep + os.environ["PATH"])
        external = self.base / "external root"
        external.mkdir()
        for roots in ([], [external, self.base / "nonexistent"]):
            self.base_workspace(roots)
            for args in ([], ["resume", "--last"]):
                with self.subTest(roots=roots, args=args):
                    result = subprocess.run(["bash", str(self.project / "scripts/start-main.sh"), *args],
                                            cwd=self.base, env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    data = json.loads(result.stdout)
                    expected = (["resume"] if args else []) + ["--cd", str(self.project)]
                    if roots:
                        expected += ["--add-dir", str(external)]
                        self.assertIn("skipped", result.stderr)
                    if args:
                        expected += ["--last"]
                    self.assertEqual(data, {"args": expected, "cwd": str(self.project)})


if __name__ == "__main__":
    unittest.main()
