from go_starter import embedded

EXPECTED_TEMPLATE_FILES = {
    ".dockerignore.tmpl",
    ".github/workflows/ci.yaml.tmpl",
    ".gitignore.tmpl",
    ".markdownlint.json.tmpl",
    ".markdownlintignore.tmpl",
    ".shellcheckrc.tmpl",
    "CHANGELOG.md.tmpl",
    "Makefile.tmpl",
    "README.md.tmpl",
    "build/Dockerfile.tmpl",
    "build/build.sh.tmpl",
    "docs/.gitkeep.tmpl",
    "src/cmd/main.go.tmpl",
    "src/go.mod.tmpl",
    "tests/.gitkeep.tmpl",
}


def test_iter_files_lists_every_template_file_including_dotfiles():
    found = {rel for rel, _ in embedded.iter_files(embedded.resource("template"))}
    assert found == EXPECTED_TEMPLATE_FILES


def test_iter_files_is_sorted_and_stable():
    first = [rel for rel, _ in embedded.iter_files(embedded.resource("template"))]
    second = [rel for rel, _ in embedded.iter_files(embedded.resource("template"))]
    assert first == sorted(first) == second


def test_template_uses_only_the_two_tokens():
    tokens = set()
    for _, entry in embedded.iter_files(embedded.resource("template")):
        text = entry.read_text()
        start = 0
        while (start := text.find("{{", start)) != -1:
            end = text.find("}}", start)
            tokens.add(text[start : end + 2])
            start = end
    assert tokens == {"{{GO_MODULE}}", "{{APP_NAME}}"}
