from importlib.metadata import version

import pytest

from go_starter import skillinstall


def test_install_writes_the_skill_under_the_home_skills_dir(fake_home):
    dest = skillinstall.install()

    assert dest == fake_home / ".claude" / "skills" / "go-starter"
    assert (dest / "SKILL.md").read_text().startswith("---\nname: go-starter\n")
    assert (dest / "agents" / "openai.yaml").exists()


def test_install_creates_missing_parent_directories(fake_home):
    assert not (fake_home / ".claude").exists()

    skillinstall.install()

    assert (fake_home / ".claude" / "skills" / "go-starter" / "SKILL.md").exists()


def test_install_writes_version_stamp(installed_skill):
    lines = (installed_skill / "VERSION").read_text().splitlines()

    assert lines == [version("go-starter"), skillinstall.content_hash()]


def test_install_replaces_a_stale_copy(fake_home):
    stale = skillinstall.skill_dir() / "old.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale")

    skillinstall.install()

    assert not stale.exists()


def test_content_hash_is_stable_and_prefixed():
    assert skillinstall.content_hash() == skillinstall.content_hash()
    assert skillinstall.content_hash().startswith("sha256:")


def test_check_passes_after_install(installed_skill):
    skillinstall.check()


def test_check_fails_when_not_installed(fake_home):
    with pytest.raises(skillinstall.SkillCheckError, match="not installed"):
        skillinstall.check()


def test_check_fails_when_hash_differs(installed_skill):
    (installed_skill / "VERSION").write_text("0.0.0\nsha256:deadbeef\n")

    with pytest.raises(
        skillinstall.SkillCheckError, match="outdated .*installed by 0.0.0"
    ):
        skillinstall.check()


def test_check_fails_when_version_file_missing(installed_skill):
    (installed_skill / "VERSION").unlink()

    with pytest.raises(
        skillinstall.SkillCheckError, match="outdated .*installed by unknown"
    ):
        skillinstall.check()
