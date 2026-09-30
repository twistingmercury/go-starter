from go_starter.main import main


def test_scaffolds_into_a_new_target_dir(tmp_path, installed_skill, capsys):
    target = tmp_path / "new" / "proj"

    assert main(["--module", "github.com/acme/tool", str(target)]) == 0
    assert (
        (target / "src/go.mod").read_text().startswith("module github.com/acme/tool\n")
    )
    assert "BIN_NAME ?= tool\n" in (target / "Makefile").read_text()
    assert capsys.readouterr().out.strip() == f"Scaffolded tool in {target.resolve()}"


def test_honors_explicit_app_name(tmp_path, installed_skill):
    target = tmp_path / "proj"

    assert (
        main(["--module", "github.com/acme/tool", "--app-name", "acme", str(target)])
        == 0
    )
    assert "BIN_NAME ?= acme\n" in (target / "Makefile").read_text()


def test_refuses_to_run_without_the_skill(tmp_path, fake_home, capsys):
    target = tmp_path / "proj"

    assert main(["--module", "github.com/acme/tool", str(target)]) == 1
    assert "not installed" in capsys.readouterr().err
    assert not target.exists()


def test_rejects_bad_module_before_writing(tmp_path, installed_skill, capsys):
    target = tmp_path / "proj"

    assert main(["--module", "https://github.com/acme/tool", str(target)]) == 1
    assert "error: module path" in capsys.readouterr().err
    assert not target.exists()


def test_rejects_underivable_app_name_with_a_hint(tmp_path, installed_skill, capsys):
    target = tmp_path / "proj"

    assert main(["--module", "github.com/Acme/MyTool", str(target)]) == 1
    assert "--app-name" in capsys.readouterr().err
    assert not target.exists()


def test_refuses_non_empty_target_and_writes_nothing(tmp_path, installed_skill, capsys):
    target = tmp_path / "proj"
    target.mkdir()
    (target / "notes.txt").touch()

    assert main(["--module", "github.com/acme/tool", str(target)]) == 1
    assert "blocking entry: notes.txt" in capsys.readouterr().err
    assert [p.name for p in target.iterdir()] == ["notes.txt"]


def test_target_that_is_a_file_is_an_error_not_a_traceback(
    tmp_path, installed_skill, capsys
):
    target = tmp_path / "afile"
    target.touch()

    assert main(["--module", "github.com/acme/tool", str(target)]) == 1
    assert capsys.readouterr().err.startswith("error: ")


def test_install_skill_prints_the_path_and_exits_zero(fake_home, capsys):
    assert main(["--install-skill"]) == 0
    assert capsys.readouterr().out.strip() == str(
        fake_home / ".claude/skills/go-starter"
    )
