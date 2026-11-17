---
intent: "Export monthly invoices as CSV"
slug: export-monthly-invoices-csv
status: draft
---

# Spec: Export monthly invoices as CSV

## Intent
Users can export all invoices for a chosen month as a CSV file. The file can be opened in spreadsheet and accounting tools.

## Assumptions
- "Monthly" means a calendar month, selected by the user, and invoices are matched by invoice issue date.
- The export is triggered on demand from the product UI; scheduled or emailed exports are out of scope.
- Only users with permission to view invoices can export them, and they can export only invoices in their own account or organisation.
- Each CSV row represents one invoice (not one line item).
- Columns are: invoice number, issue date, due date, customer name, currency, subtotal, tax, total, status.
- The CSV is UTF-8 encoded, comma-delimited, with a header row, and dates are in ISO 8601 (YYYY-MM-DD).
- Monetary amounts are written as plain decimal numbers with no currency symbols or thousands separators.
- Invoices in all statuses (draft, sent, paid, void) are included unless the product owner says otherwise.

## Open questions
- Should the export include line items, and if so, one row per invoice or one row per line item?
- Should draft and void invoices be included?
- Which timezone defines the month boundaries (user, account, or UTC)?
- What is the maximum expected number of invoices per month, and should very large exports be generated asynchronously?
- Which roles are allowed to export invoices?
- Should an export be recorded in an audit log?

## Unit 1: Generate the monthly invoice CSV

### Story 1.1: Export invoices for a selected month
As a finance user, I want to export all invoices for a chosen month as a CSV file, so that I can reconcile and analyse them in a spreadsheet or accounting tool.

#### Acceptance criteria
- **AC 1.1.1** Given I have permission to view invoices and invoices exist in March 2026, when I select March 2026 and choose Export CSV, then a CSV file downloads containing one row per invoice issued in March 2026 and no invoices from other months.
- **AC 1.1.2** Given the export has been generated, when I open the file, then the first row is a header containing the agreed column names and each data row has a value (or an empty cell) for every column.
- **AC 1.1.3** Given the export has been generated, when I open the file, then dates are formatted YYYY-MM-DD and amounts are plain decimals with two decimal places.
- **AC 1.1.4** [edge] Given no invoices exist in the selected month, when I choose Export CSV, then a CSV containing only the header row downloads and I see a message that no invoices were found.
- **AC 1.1.5** [edge] Given an invoice is issued at 00:00 on the first day or 23:59 on the last day of the month (in the agreed timezone), when I export that month, then the invoice appears in that month's file only.

### Story 1.2: Produce a correctly formatted CSV
As a finance user, I want text fields escaped and encoded correctly, so that the file opens without corruption in common tools.

#### Acceptance criteria
- **AC 1.2.1** Given a customer name contains a comma, double quote or line break, when I export, then the field is wrapped in double quotes with embedded quotes doubled and the file parses into the same number of columns on every row.
- **AC 1.2.2** Given a customer name contains non-ASCII characters such as "Zoë Müller", when I open the file in a UTF-8-aware tool, then the name displays unchanged.
- **AC 1.2.3** [edge] Given a text field begins with =, +, - or @, when I export, then the value is prefixed so that spreadsheet applications do not execute it as a formula.
- **AC 1.2.4** [edge] Given an invoice has an empty optional field such as due date, when I export, then that cell is empty and the row keeps the correct number of columns.

## Unit 2: Export entry point and access control

### Story 2.1: Choose a month and start the export
As a finance user, I want to pick a month and start the export from the invoices page, so that I can get the file without help from support.

#### Acceptance criteria
- **AC 2.1.1** Given I am on the invoices page, when I open the export control, then I can select a month and year and the current month is preselected.
- **AC 2.1.2** Given I have selected a month, when I choose Export CSV, then the browser downloads a file named invoices-YYYY-MM.csv.
- **AC 2.1.3** [edge] Given I select a month in the future, when I choose Export CSV, then I see a message that no invoices exist for that period and still receive a header-only file or no file, as the product owner decides.
- **AC 2.1.4** [edge] Given the export fails on the server, when I choose Export CSV, then I see an error message, no partial file downloads, and I can retry.

### Story 2.2: Restrict exports to authorised users
As an account administrator, I want only permitted users to export invoices and only for their own organisation, so that financial data is not exposed.

#### Acceptance criteria
- **AC 2.2.1** Given I am signed in as a user with invoice access, when I view the invoices page, then the Export CSV control is visible and the file contains only my organisation's invoices.
- **AC 2.2.2** [edge] Given I am signed in as a user without invoice access, when I view the invoices page or call the export endpoint directly, then the control is hidden and the endpoint returns a 403 response with no data.
- **AC 2.2.3** [edge] Given I am not signed in or my session has expired, when I request the export, then I am asked to sign in and no data is returned.

## Unit 3: Large exports

### Story 3.1: Export a large month without failure
As a finance user, I want exports with many invoices to complete reliably, so that busy months do not break my reporting.

#### Acceptance criteria
- **AC 3.1.1** Given a month contains 10,000 invoices, when I export it, then the complete file is delivered with all 10,000 rows within the agreed time limit.
- **AC 3.1.2** [edge] Given a month contains more invoices than the synchronous limit, when I export it, then I see a message that the export is being prepared and I can download the file when it is ready.
- **AC 3.1.3** [edge] Given I start the same export twice in quick succession, when both complete, then each file contains identical data and no invoices are duplicated or missing within a file.
