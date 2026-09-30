from go_starter.main import main


def test_main_prints_greeting(capsys):
    main([])

    assert "hello, world" in capsys.readouterr().out
