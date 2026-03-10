import ast
from pathlib import Path
import unittest


CLI_PATH = Path(__file__).resolve().parents[2] / "cli.py"


class TestCliWatchRegistration(unittest.TestCase):
    def test_root_cli_registers_watch_typer(self) -> None:
        source = CLI_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)

        found = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr != "add_typer":
                continue
            if not isinstance(node.func.value, ast.Name):
                continue
            if node.func.value.id != "app":
                continue

            has_watch_name = any(
                kw.arg == "name"
                and isinstance(kw.value, ast.Constant)
                and kw.value.value == "watch"
                for kw in node.keywords
            )
            if has_watch_name:
                found = True
                break

        self.assertTrue(
            found,
            "astock.cli should register watch typer via app.add_typer(..., name='watch')",
        )


if __name__ == "__main__":
    unittest.main()
