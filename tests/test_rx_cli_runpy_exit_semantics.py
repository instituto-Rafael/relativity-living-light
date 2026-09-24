from __future__ import annotations

import unittest
from unittest import mock

import rx.cli as cli


class RxCliRunpyExitSemanticsTests(unittest.TestCase):
    def test_tool_args_accepts_successful_system_exit_and_restores_argv(self):
        original = cli.sys.argv[:]
        with mock.patch.object(cli.runpy, "run_path", side_effect=SystemExit(0)) as run_path:
            result = cli._tool_args("dummy.py", ["--write"])
        self.assertIsNone(result)
        self.assertEqual(cli.sys.argv, original)
        run_path.assert_called_once()

    def test_tool_propagates_nonzero_system_exit(self):
        with mock.patch.object(cli.runpy, "run_path", side_effect=SystemExit(3)):
            with self.assertRaises(SystemExit) as caught:
                cli._tool("dummy.py")
        self.assertEqual(caught.exception.code, 3)

    def test_module_accepts_successful_system_exit(self):
        with mock.patch.object(cli.runpy, "run_module", side_effect=SystemExit(None)):
            self.assertIsNone(cli._module("dummy.module"))

    def test_successful_tool_exit_does_not_prevent_next_tool(self):
        calls = []

        def fake_run_path(path, run_name=None):
            calls.append(str(path))
            if len(calls) == 1:
                raise SystemExit(0)
            return {"ok": True}

        with mock.patch.object(cli.runpy, "run_path", side_effect=fake_run_path):
            cli._tool_args("first.py", [])
            cli._tool_args("second.py", [])
        self.assertEqual(len(calls), 2)
        self.assertTrue(calls[0].endswith("tools/first.py"))
        self.assertTrue(calls[1].endswith("tools/second.py"))


if __name__ == "__main__":
    unittest.main()
