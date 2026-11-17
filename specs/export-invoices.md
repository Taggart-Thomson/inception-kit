---
intent: "Export monthly invoices as CSV (save the spec as specs/export-invoices.md)"
slug: export-invoices
status: draft
---

# Spec: Export monthly invoices as CSV

## Intent
A finance user can pick a calendar month and download all invoices issued in that month as a single CSV file, for use in spreadsheets and accounting tools.

## Assumptions
- The primary user is a finance or accounting staff member (role "Finance admin") who already has access to the invoice data.
- "Monthly" means a calendar month, selected as YYYY-MM, and an invoice belongs to the month of its issue date in UTC.
- Each invoice is exported as one row; line items are not exported.
- Columns are: invoice_number, customer_name, issue_date (YYYY-MM-DD), due_date (YYYY-MM-DD), currency (ISO 4217), subtotal, tax, total, status.
- Money values are decimals with exactly 2 digits after the point and no currency symbol or thousands separator.
- The file is UTF-8, comma-delimited, has a header row and uses CRLF line endings (RFC 4180).
- One export covers at most 50,000 invoices.
- The export is on demand from the application; scheduled or emailed exports are out of scope.

## Open questions
- Should the month be based on issue date, due date or payment date? (Assumed: issue date.)
- Which invoice statuses are included (draft, void, paid, unpaid)? (Assumed: all except draft.)
- Do invoices in multiple currencies go in one file, or one file per currency? (Assumed: one file, with a currency column.)
- Are line items, or any other fields, required in the export?
- Which roles may export, and must exports be audit-logged?
- Is 50,000 invoices per month a sufficient limit for the largest customer?
- What HTTP status and screen behaviour apply to a future month (AC 1.2.1) and to a month over the limit (AC 3.2.2)? Not stated, so the tests cannot check the status code.
- Under what hardware, data store and network conditions must the 60-second target in AC 3.2.1 hold?
- Does an empty month produce a header-only download (as AC 1.1.3 states) or no file at all?
- What happens with negative amounts (credit notes), amounts with more than 2 decimals, and leading tab or carriage-return characters in names?
- Does an export denied with 401 or 403 need an audit entry?

## Unit 1: Month selection and file generation

### Story 1.1: Export a chosen month
As a finance admin, I want to choose a month and download its invoices as a CSV file, so that I can reconcile them in a spreadsheet.

#### Acceptance criteria
- **AC 1.1.1** Given 3 non-draft invoices issued in 2026-10 and 2 issued in 2026-11, when I export 2026-10, then the downloaded file is named invoices-2026-10.csv and contains 1 header row and exactly 3 data rows.
- **AC 1.1.2** [edge] Given invoice A issued at 2026-10-31T23:59:59Z and invoice B issued at 2026-11-01T00:00:00Z, when I export 2026-10, then the file has exactly 1 data row and its invoice_number is that of invoice A.
- **AC 1.1.3** [edge] Given no invoices were issued in 2026-09, when I export 2026-09, then the downloaded file invoices-2026-09.csv contains exactly 1 line (the header row) and the screen shows the message "No invoices found for 2026-09".
- **AC 1.1.4** [edge] Given 2 draft invoices and 1 paid invoice issued in 2026-10, when I export 2026-10, then the file has exactly 1 data row and it is the paid invoice (depends on the open question on included statuses).

### Story 1.2: Reject invalid or future months
As a finance admin, I want clear errors for months that cannot be exported, so that I do not download a wrong or empty file by mistake.

#### Acceptance criteria
- **AC 1.2.1** [edge] Given today is 2026-11-17, when I request the month 2026-12, then no file is produced and the message "Cannot export a future month" is shown.
- **AC 1.2.2** [edge] Given a request with the month value "2026-13", when I submit it, then the response is HTTP 400 with the message "Month must be in YYYY-MM format" and no file is produced.
- **AC 1.2.3** Given the request time is 2026-11-17T10:00:00Z and non-draft invoices issued at 2026-10-31T23:59:59Z, 2026-11-01T00:00:00Z and 2026-11-17T09:59:59Z, when I export 2026-11, then the file has exactly 2 data rows, being the invoices issued at 2026-11-01T00:00:00Z and 2026-11-17T09:59:59Z.
- **AC 1.2.4** [edge] Given a request with the month value "" (empty) or no month value, when I submit it, then the response is HTTP 400 with the message "Month must be in YYYY-MM format" and no file is produced.
- **AC 1.2.5** [edge] Given a request with the month value "2026-00", when I submit it, then the response is HTTP 400 with the message "Month must be in YYYY-MM format" and no file is produced.

## Unit 2: CSV content and format

### Story 2.1: Consistent columns and values
As a finance admin, I want a fixed column layout with formatted values, so that the file imports into accounting tools without manual cleanup.

#### Acceptance criteria
- **AC 2.1.1** Given any successful export, when I read the file's first line, then it is exactly "invoice_number,customer_name,issue_date,due_date,currency,subtotal,tax,total,status" followed by CRLF.
- **AC 2.1.2** Given an invoice with subtotal 1234.5, tax 123.45 and total 1357.95 in EUR, when it is exported, then its row contains the values 1234.50, 123.45 and 1357.95 and the currency value EUR.
- **AC 2.1.3** [edge] Given an invoice with no due date, when it is exported, then the due_date field is empty and the row still has exactly 9 fields.
- **AC 2.1.4** [edge] Given an invoice with subtotal 0, tax 0 and total 0, when it is exported, then its row contains the values 0.00, 0.00 and 0.00.

### Story 2.2: Safe escaping of text
As a finance admin, I want special characters handled correctly, so that rows are not broken or turned into spreadsheet formulas.

#### Acceptance criteria
- **AC 2.2.1** [edge] Given a customer named `Smith, "Jones" & Co`, when it is exported, then the field appears as `"Smith, ""Jones"" & Co"` and the row parses to 9 fields.
- **AC 2.2.2** [edge] Given customers named "=SUM(1)", "+1", "-1" and "@a", when they are exported, then their customer_name fields are exactly "'=SUM(1)", "'+1", "'-1" and "'@a", and a customer named "A=B" is exported unchanged.
- **AC 2.2.3** Given a customer named "Zoë Müller", when the file bytes are inspected, then the name is encoded as UTF-8 (ë = C3 AB, ü = C3 BC), the file does not start with a byte order mark, and decoding as UTF-8 gives "Zoë Müller".

## Unit 3: Access, limits and delivery

### Story 3.1: Restrict export to permitted users
As a compliance officer, I want only finance admins to export invoices, so that customer billing data is not exposed to other staff.

#### Acceptance criteria
- **AC 3.1.1** Given I am signed in without the finance admin role, when I request an export, then the response is HTTP 403 and no file is produced.
- **AC 3.1.2** [edge] Given I am not signed in, when I request an export, then the response is HTTP 401 and no file is produced.
- **AC 3.1.3** Given I am a finance admin, when I complete an export of 2026-10, then exactly 1 audit log entry is recorded with my user id, the month 2026-10 and a row count equal to the number of data rows in the file (depends on the open question on audit logging).

### Story 3.2: Handle large months
As a finance admin, I want large months to export reliably or fail with a clear message, so that I know whether my file is complete.

#### Acceptance criteria
- **AC 3.2.1** Given a month with 50,000 non-draft invoices, when I export it, then the file contains 50,000 data rows and the download completes within 60 seconds measured from the request to the last byte received (test environment and network to be fixed; see open questions).
- **AC 3.2.2** [edge] Given a month with 50,001 non-draft invoices, when I export it, then no partial file is produced and the message "Month exceeds the 50,000 invoice limit" is shown.
- **AC 3.2.3** [edge] Given the data store is unavailable, when I export a month, then the response is HTTP 503, no partial file is downloaded and the message "Export failed, please try again" is shown.

## Review
- Verdict: draft (not approved). The wording of the criteria is now testable, but several criteria depend on decisions nobody has made.
- Rewrote 8 criteria: 1.1.2, 1.1.3, 1.2.3, 2.1.1, 2.2.2, 2.2.3, 3.1.3, 3.2.1.
- Added 4 criteria, all [edge]: 1.1.4, 1.2.4, 1.2.5, 2.1.4.
- Unresolved: which statuses are included (AC 1.1.4, 3.2.1, 3.2.2).
- Unresolved: roles allowed and audit logging (AC 3.1.x).
- Unresolved: HTTP status for future month and over-limit (AC 1.2.1, 3.2.2).
- Unresolved: conditions for the 60-second target (AC 3.2.1).
- Unresolved: empty-month behaviour, negative or over-precision amounts, other leading characters, and audit of denied requests.
