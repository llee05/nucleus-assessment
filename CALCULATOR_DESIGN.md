# Calculator app: 50-minute design

Build a single-page calculator using **Python, Flask, and an HTML/CSS form**. The browser submits two numbers and an operation; Python calculates the result and returns the updated page. This meets the challenge's frontend and backend requirements while keeping most of the work in Python.

## Stack

| Part | Choice | Reason |
| --- | --- | --- |
| Backend | Python + Flask | A small app needs only one route and a calculation function. |
| Frontend | HTML, Jinja template, plain CSS | Flask renders the form, result, and errors; JavaScript is optional. |
| Arithmetic | Python's built-in `decimal.Decimal` | Constructing decimals from strings avoids binary floating-point surprises such as `0.1 + 0.2`. |
| Tests | Python's built-in unittest + Flask test client | Check arithmetic and form submissions without running a browser or installing a test framework. |
| Development | Python virtual environment, Flask development server | Simple local setup with few dependencies. |

Flask includes Jinja and supports form handling and template rendering; see the [Flask quickstart](https://flask.palletsprojects.com/en/stable/quickstart/). Python's [Decimal documentation](https://docs.python.org/3/library/decimal.html) explains decimal arithmetic and precision. Flask documents its [test client](https://flask.palletsprojects.com/en/stable/testing/) for testing requests.

## First version

- Two labelled number fields supporting negative numbers and decimals.
- An operation selector: addition, subtraction, multiplication, division.
- A **Calculate** button; pressing Enter also submits the form.
- A visible result, or a helpful error beside the form.
- A **Clear** link to `/` that returns to an empty form.
- A compact layout that fits a phone screen.

Use a two-number form for this version. A keypad, expression parsing, scientific functions, history, accounts, and deployment are future additions. The app needs no database because each calculation is independent.

## Page layout

```text
          Calculator

  First number    [ -3.5          ]
  Operation       [ Add        v ]
  Second number   [  2            ]

  [ Calculate ]   Clear

  Result: -1.5
```

Use explicit `<label>` elements, a submit button, and a result region with `aria-live="polite"`. Show errors as text with `role="alert"`. Preserve the submitted values so users can correct mistakes. A normal page reload after submission is acceptable.

## Request flow and backend

```text
Browser form → POST / → validate → calculate → render HTML with result/error
```

| Request | Behavior |
| --- | --- |
| `GET /` | Return the empty calculator page, status 200. |
| `POST /` | Read `first_number`, `operation`, and `second_number`; return the populated page with a result, status 200. |
| Invalid `POST /` | Return the populated page with an error and no previous result, status 400. |

Keep responsibilities small:

- The route reads form fields and renders `index.html` with `values`, `result`, and `error`.
- A helper such as `calculate(first_number, operation, second_number)` validates the strings and returns a formatted result, or raises `ValueError` with a user-facing message.
- An explicit operation allowlist (`add`, `subtract`, `multiply`, `divide`) selects the arithmetic. Never use `eval()` to run input.

### Number and error rules

1. Trim whitespace. Require both operands and limit each to 32 characters on the server and in the form.
2. Accept signed, ordinary decimal numbers such as `12`, `-3.5`, and `.5`. Reject scientific notation, expressions, `NaN`, and infinity. Use a full-string decimal-format check before constructing `Decimal` directly from the input strings.
3. Validate the operation on the server even though the form uses a dropdown.
4. Reject division by zero, including `0.0`, with **“Cannot divide by zero.”**
5. Calculate with a decimal precision of 28 significant digits. Repeating results such as `1 / 3` are rounded; this is a documented limitation.
6. Display ordinary decimal notation, remove trailing fractional zeros, and display negative zero as `0`. For example, `5.00` becomes `5`, while `50` stays `50`.

Use specific messages such as **“Enter both numbers,” “Enter valid decimal numbers,”** and **“Choose a supported operation.”** Retain Jinja's default HTML escaping when displaying submitted values.

## Files to create

```text
app.py                    # Flask route and calculation helper
templates/index.html      # Form, result, and error display
static/style.css          # Small responsive layout
tests/test_app.py         # Arithmetic tests; add request tests with the route
requirements.txt          # Tested dependency versions
.gitignore                # Ignore .venv/, caches, and editor files
```

Update the existing `README.md` with setup, run, and test instructions, supported behavior, and limitations. Keep the helper in `app.py` for now; this app is small enough to understand in one file.

## 50-minute build plan

| Minutes | Work | Checkpoint |
| --- | --- | --- |
| 0–5 | Create the environment, install Flask, add a basic route. | A page opens locally. |
| 5–18 | Write validation, arithmetic, and the POST handler. | A submitted calculation returns a result. |
| 18–30 | Build the form, result/error display, Clear link, and basic CSS. | All four operations work through the browser. |
| 30–42 | Add focused tests and manually check keyboard/mobile layout. | Happy paths and error cases pass. |
| 42–50 | Fix remaining issues, document setup, and answer the challenge follow-ups. | A reviewer can run and assess the submission. |

If time slips, simplify styling and preserve the time for validation and documentation. Stop adding features once the core form works.

### Setup and run

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Flask
```

Once `app.py` exists:

```bash
python -m flask --app app run --debug
```

Open `http://127.0.0.1:5000`. Use this server for local development. Record the working package versions in `requirements.txt` so a reviewer can install them with `python -m pip install -r requirements.txt`.

Run the tests with:

```bash
python -m unittest discover -s tests -v
```

## Completion checks

| Case | Expected outcome |
| --- | --- |
| `2 + 3`, `7 - 10`, `-4 × 2`, `7 / 2` | `5`, `-3`, `-8`, `3.5` |
| `0.1 + 0.2` | `0.3` |
| `1 / 3` | Rounded decimal result, no crash |
| Division by `0` or `0.0` | Helpful error, status 400 |
| Missing, invalid, or overlong operand | Helpful error, status 400 |
| `NaN`, `Infinity`, or an unsupported operation sent directly | Rejected by the backend |
| Initial page and a valid form submission | Status 200; correct form/result rendered |
| An error followed by a valid calculation | Error clears and the new result appears |
| Clear, Enter key, narrow browser window | Empty form, keyboard submission, usable layout |

Automate arithmetic and request behavior; check layout and keyboard behavior manually.

## Submission notes

The challenge asks for a public GitHub repository and follow-up answers. Before submitting, confirm the README commands work and the repository is publicly accessible. Record what actually works, what remains unfinished, the challenges encountered, and possible future features. Preserve the real AI prompts and outputs, including this design request, and explain where they helped or needed correction. Write these reflections after implementation so they describe the result accurately.
