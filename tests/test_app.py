"""Run with: python3 -m unittest discover -s tests -v."""

import unittest
from decimal import ROUND_DOWN, getcontext, localcontext

from app import app, calculate


class CalculateTests(unittest.TestCase):
    def test_arithmetic_and_display(self):
        cases = [
            ("2", "add", "3", "5"),
            ("7", "subtract", "10", "-3"),
            ("-4", "multiply", "2", "-8"),
            ("7", "divide", "2", "3.5"),
            ("0.1", "add", "0.2", "0.3"),
            ("0.3", "subtract", "0.1", "0.2"),
            ("0.1", "multiply", "0.2", "0.02"),
            ("0.3", "divide", "0.1", "3"),
            ("0008", "add", "0002", "10"),
            ("0001.50", "multiply", "0002.00", "3"),
            ("-0008", "divide", "0002", "-4"),
            (" +001.50 ", "add", " .5 ", "2"),
            ("-.5", "add", "+.25", "-0.25"),
            ("12.", "add", "0", "12"),
            ("1.2300", "add", "0", "1.23"),
            ("5.00", "add", "0", "5"),
            ("50", "multiply", "1", "50"),
            ("100.00", "add", "0", "100"),
            ("0000", "add", "0.00", "0"),
            ("-0.00", "multiply", "2", "0"),
            ("0", "divide", "-2", "0"),
            ("1", "divide", "3", "0." + "3" * 28),
            ("2", "divide", "3", "0." + "6" * 27 + "7"),
            ("1", "divide", "1000000000000", "0.000000000001"),
            ("9" * 32, "add", "1", "1" + "0" * 32),
        ]
        for first, operation, second, expected in cases:
            with self.subTest(first=first, operation=operation, second=second):
                self.assertEqual(calculate(first, operation, second), expected)

    def test_division_by_zero(self):
        for zero in ("0", "0.0", "-0.00", "+0000", ".0"):
            with self.subTest(zero=zero):
                with self.assertRaisesRegex(ValueError, "^Cannot divide by zero\\.$"):
                    calculate("1", "divide", zero)

    def test_missing_numbers(self):
        for first, second in (("", "1"), ("1", ""), ("   ", "1")):
            with self.subTest(first=first, second=second):
                with self.assertRaisesRegex(ValueError, "^Enter both numbers\\.$"):
                    calculate(first, "add", second)

    def test_invalid_numbers_in_either_position(self):
        for invalid in (
            "hello", ".", "-", "1.2.3", "1 + 2", "1/2", "1e3", "1_000",
            "NaN", "sNaN", "Infinity", "-Infinity", "0x10", "1,5", "1 2",
            "１２", None, 0.1,
        ):
            for first, second in ((invalid, "1"), ("1", invalid)):
                with self.subTest(first=first, second=second):
                    with self.assertRaisesRegex(ValueError, "^Enter valid decimal numbers\\.$"):
                        calculate(first, "add", second)

    def test_operand_length_limit(self):
        for first, second in (("1" * 33, "1"), ("1", "1" * 33)):
            with self.subTest(first=first, second=second):
                with self.assertRaisesRegex(ValueError, "^Use at most 32 characters per number\\.$"):
                    calculate(first, "add", second)

    def test_unsupported_operations(self):
        for operation in ("", "power", "__import__('os')", None):
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(ValueError, "^Choose a supported operation\\.$"):
                    calculate("1", operation, "2")

    def test_precision_is_local_and_predictable(self):
        with localcontext() as context:
            context.prec = 2
            context.rounding = ROUND_DOWN
            self.assertEqual(calculate("2", "divide", "3"), "0." + "6" * 27 + "7")
            self.assertEqual(getcontext().prec, 2)
            self.assertEqual(getcontext().rounding, ROUND_DOWN)


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_initial_page_and_stylesheet(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Your answer will appear here.", response.text)
        self.assertNotIn('id="result-value"', response.text)
        with self.client.get("/static/style.css") as stylesheet:
            self.assertEqual(stylesheet.status_code, 200)

    def test_form_uses_calculation_logic_for_all_operations(self):
        for operation, expected in (
            ("add", "4.5"), ("subtract", "-1.5"),
            ("multiply", "4.5"), ("divide", "0.5"),
        ):
            with self.subTest(operation=operation):
                response = self.client.post("/", data={
                    "first_number": "0001.50", "operation": operation, "second_number": "3",
                })
                self.assertEqual(response.status_code, 200)
                self.assertIn(f'>{expected}</output>', response.text)
                self.assertIn('value="0001.50"', response.text)

    def test_form_validation_errors(self):
        for data, message in (
            ({}, "Enter both numbers."),
            ({"first_number": "7", "operation": "divide", "second_number": "0.0"},
             "Cannot divide by zero."),
            ({"first_number": "1", "operation": "power", "second_number": "2"},
             "Choose a supported operation."),
        ):
            with self.subTest(data=data):
                response = self.client.post("/", data=data)
                self.assertEqual(response.status_code, 400)
                self.assertIn(message, response.text)
                self.assertIn('role="alert"', response.text)
                self.assertNotIn('id="result-value"', response.text)

    def test_errors_clear_after_correction_and_clear_link_resets(self):
        self.client.post("/", data={
            "first_number": "1", "operation": "divide", "second_number": "0",
        })
        corrected = self.client.post("/", data={
            "first_number": "0.1", "operation": "add", "second_number": "0.2",
        })
        self.assertEqual(corrected.status_code, 200)
        self.assertIn('>0.3</output>', corrected.text)
        self.assertNotIn('role="alert"', corrected.text)
        cleared = self.client.get("/")
        self.assertNotIn('id="result-value"', cleared.text)
        self.assertIn('placeholder="e.g. 12.5" value=""', cleared.text)

    def test_submitted_values_are_html_escaped(self):
        response = self.client.post("/", data={
            "first_number": '<script>alert("x")</script>',
            "operation": "add", "second_number": "1",
        })
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("<script>", response.text)
        self.assertIn("&lt;script&gt;", response.text)


if __name__ == "__main__":
    unittest.main()
