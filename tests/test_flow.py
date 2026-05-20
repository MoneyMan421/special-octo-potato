import unittest

from app.main import controller, evaluator, handle_request
from observability.audit import AuditLogger


class FlowTests(unittest.TestCase):
    def test_run_id_is_included_in_all_logs(self) -> None:
        records = []
        logger = AuditLogger(sink=records.append)

        handle_request({"message": "hello"}, logger=logger)

        self.assertGreaterEqual(len(records), 2)
        run_ids = {record["run_id"] for record in records}
        self.assertEqual(len(run_ids), 1)
        for record in records:
            self.assertIn("run_id", record)
            self.assertIsInstance(record, dict)

    def test_policy_warning_does_not_block_or_change_output(self) -> None:
        records = []
        logger = AuditLogger(sink=records.append)
        payload = {"password": "redacted"}

        result = handle_request(payload, logger=logger)

        self.assertEqual(result, payload)
        warning_events = [r for r in records if r["event"] == "policy_warning"]
        self.assertEqual(len(warning_events), 1)

    def test_stagnation_detection_and_flow_injection(self) -> None:
        context = {
            "iteration": 1,
            "direction": "forward",
            "last_plan": "forward:step-1",
            "last_output": {"message": "same"},
        }

        evaluation = evaluator(context, "forward:step-1", {"message": "same"})
        action = controller(context, evaluation)

        self.assertTrue(evaluation["stagnant"])
        self.assertEqual(action, "direction_shift")
        self.assertEqual(context["direction"], "shift-2")
        self.assertEqual(context["mutation_count"], 1)


if __name__ == "__main__":
    unittest.main()
