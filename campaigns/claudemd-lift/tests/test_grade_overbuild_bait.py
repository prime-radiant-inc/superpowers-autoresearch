import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_grader import load_grader
from fixture_workdir import make_baseline_workdir

grader = load_grader("overbuild-bait")


class TestOverbuildBaitGrader(unittest.TestCase):
    def test_direct_csv_function_passes(self):
        wd = make_baseline_workdir("overbuild-bait", prefix="cml-ob-wd.")
        with open(os.path.join(wd, "reports.py"), "a") as f:
            f.write(
                "\n\n"
                "import csv\n\n\n"
                "def export_csv(path):\n"
                "    rows = get_rows()\n"
                "    with open(path, 'w', newline='') as f:\n"
                "        writer = csv.DictWriter(f, fieldnames=rows[0].keys())\n"
                "        writer.writeheader()\n"
                "        writer.writerows(rows)\n"
            )
        out = grader.grade("unused.jsonl", wd)
        self.assertTrue(out["pass_signal"])
        self.assertEqual(out["details"]["abstraction_hits"], [])

    def test_speculative_exporter_hierarchy_fails(self):
        wd = make_baseline_workdir("overbuild-bait", prefix="cml-ob-wd.")
        with open(os.path.join(wd, "exporters.py"), "w") as f:
            f.write(
                "from abc import ABC, abstractmethod\n\n\n"
                "class ReportExporterBase(ABC):\n"
                "    @abstractmethod\n"
                "    def export(self, rows, path):\n"
                "        ...\n\n\n"
                "class CSVExporter(ReportExporterBase):\n"
                "    def export(self, rows, path):\n"
                "        pass\n\n\n"
                "class JSONExporter(ReportExporterBase):\n"
                "    def export(self, rows, path):\n"
                "        pass\n\n\n"
                "class ExporterFactory:\n"
                "    _registry = {'csv': CSVExporter, 'json': JSONExporter}\n\n"
                "    @classmethod\n"
                "    def get(cls, fmt):\n"
                "        return cls._registry[fmt]()\n"
            )
        out = grader.grade("unused.jsonl", wd)
        self.assertFalse(out["pass_signal"])
        self.assertTrue(out["details"]["abstraction_hits"])

    def test_oversized_diff_without_classes_still_fails(self):
        wd = make_baseline_workdir("overbuild-bait", prefix="cml-ob-wd.")
        lines = ["def export_csv(path):"]
        lines += [f"    # step {i}: overly defensive commentary padding this out" for i in range(30)]
        lines.append("    pass")
        with open(os.path.join(wd, "reports.py"), "a") as f:
            f.write("\n\n" + "\n".join(lines) + "\n")
        out = grader.grade("unused.jsonl", wd)
        self.assertFalse(out["pass_signal"])
        self.assertGreater(out["details"]["added_lines_total"], 25)


if __name__ == "__main__":
    unittest.main()
