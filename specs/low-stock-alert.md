---
intent: "Email the shop owner when an item's stock falls below a threshold they set"
slug: low-stock-alert
status: draft
---

# Spec: Low-stock email alert

## Intent
The shop owner sets a minimum stock level for an item. When that item's stock drops below the level, the system emails the owner once so they can reorder.

## Assumptions
- There is one shop owner account per shop, with one verified email address.
- Stock is a whole number of units, 0 or more, and is already tracked per item.
- The threshold is set per item, as a whole number from 0 to 10,000.
- "Falls below" means stock is strictly less than the threshold; stock equal to the threshold does not alert.
- One alert is sent per crossing: after an alert, no further alert is sent for that item until stock has risen back to the threshold or above.
- Items with no threshold set never trigger an alert.

## Open questions
- Should the owner be able to set a default threshold for all items, or only per item?
- Can the owner list more than one recipient email address?
- If several items cross their thresholds in the same hour, should they be sent as separate emails or one digest?
- Should the alert repeat as a reminder if stock stays low (for example every 7 days)?
- Permissions: what happens when a user other than the owner tries to set or change a threshold (rejected with what message)? No criterion can be written until decided.
- If the owner lowers the threshold (for example 8 to 3) while stock is below the old one, or after an alert was already sent, is the "already alerted" state reset? No criterion can be written until decided.
- Where is the failure log written, and does the "alert history" screen already exist? AC 3.1.2 cannot be tested without a named location.
- How soon after the sale must the alert be submitted (for example within 60 seconds)? AC 2.1.1 has no time bound.
- Which of "stock sold" and "stock edited manually" count as events that can trigger an alert? Criteria only cover sales, restocks and threshold changes.

## Unit 1: Set a low-stock threshold

### Story 1.1: Set and change a threshold
As a shop owner, I want to set a low-stock threshold on each item, so that I choose when I am warned.

#### Acceptance criteria
- **AC 1.1.1** Given an item with no threshold, when the owner saves a threshold of 5, then the item shows "Low-stock threshold: 5" after the page reloads.
- **AC 1.1.2** Given an item with a threshold of 5 and stock 5, when the owner clears the field and saves, then the item shows no threshold, and a later sale reducing stock from 5 to 4 sends 0 emails.
- **AC 1.1.3** [edge] Given an item with a stored threshold of 5, when the owner saves a threshold of -1, then the save is rejected with the message "Threshold must be a whole number from 0 to 10,000" and the stored threshold is still 5.
- **AC 1.1.4** [edge] Given an item with a stored threshold of 5, when the owner saves a threshold of 10001, then the save is rejected with the message "Threshold must be a whole number from 0 to 10,000" and the stored threshold is still 5.
- **AC 1.1.5** [edge] Given an item with a stored threshold of 5, when the owner saves a threshold of "abc", then the save is rejected with the message "Threshold must be a whole number from 0 to 10,000" and the stored threshold is still 5.
- **AC 1.1.6** [edge] Given an item with a stored threshold of 5, when the owner saves a threshold of 5.5, then the save is rejected with the message "Threshold must be a whole number from 0 to 10,000" and the stored threshold is still 5.
- **AC 1.1.7** [edge] Given an item with no threshold, when the owner saves a threshold of 0, then the item shows "Low-stock threshold: 0" after the page reloads.
- **AC 1.1.8** [edge] Given an item with no threshold, when the owner saves a threshold of 10000, then the item shows "Low-stock threshold: 10000" after the page reloads.

## Unit 2: Detect the crossing and send the alert

### Story 2.1: Email when stock falls below the threshold
As a shop owner, I want an email when an item's stock falls below its threshold, so that I can reorder before it sells out.

#### Acceptance criteria
- **AC 2.1.1** Given an item with threshold 5 and stock 5, when a sale reduces stock to 4, then exactly 1 email is submitted to the email service, addressed to the owner's verified address.
- **AC 2.1.2** Given an item named "Blue Mug" with threshold 5 and stock 5, when a sale reduces stock to 4, then the alert email's subject contains "Blue Mug" and its body contains "Blue Mug", the stock count "4" and the threshold "5".
- **AC 2.1.3** [edge] Given an item with threshold 5 and stock 6, when a sale reduces stock to 5 (equal to the threshold), then 0 emails are sent.
- **AC 2.1.4** [edge] Given an item with no threshold set, when stock drops from 3 to 0, then 0 emails are sent.
- **AC 2.1.5** [edge] Given an item with threshold 5 and stock 5, when a restock raises stock to 6, then 0 emails are sent.
- **AC 2.1.6** [edge] Given an item with threshold 0 and stock 1, when a sale reduces stock to 0, then 0 emails are sent, because stock 0 is not strictly less than 0.
- **AC 2.1.7** [edge] Given an item with threshold 5 and stock 10, when a single sale of 7 units reduces stock to 3, then exactly 1 email is sent and its body shows stock "3".

### Story 2.2: Avoid repeat alerts
As a shop owner, I want one email per drop below the threshold, so that my inbox is not flooded.

#### Acceptance criteria
- **AC 2.2.1** Given an alert was already sent for an item at stock 4 with threshold 5, when a further sale reduces stock to 3, then 0 additional emails are sent.
- **AC 2.2.2** Given an alert was sent and stock was then restocked to 5, when a sale reduces stock to 4, then 1 new email is sent.
- **AC 2.2.3** [edge] Given an item with stock 5 and threshold 5, when the owner raises the threshold to 8, then 1 email is sent, because stock 5 is now below 8.
- **AC 2.2.4** [edge] Given an item with threshold 5 and stock 5, when two sales processed at the same moment reduce stock to 4 and then 3, then exactly 1 email is sent in total.

## Unit 3: Handle delivery failure

### Story 3.1: Do not lose or block on failed emails
As a shop owner, I want a failed email to be retried and not block sales, so that I still get warned and customers can still buy.

#### Acceptance criteria
- **AC 3.1.1** Given the email service rejects every send and the clock is controllable, when a sale drops stock from 5 to 4 on an item with threshold 5, then the sale is recorded as completed and retries are attempted at exactly 10, 20 and 30 minutes after the first failed send, with no fourth retry.
- **AC 3.1.2** [edge] Given the email service rejects the first send and all 3 retries, when the third retry fails, then one log entry containing the item name is written and the alert shows status "failed" in the owner's alert history.
- **AC 3.1.4** [edge] Given the email service rejects the first send but accepts the first retry, when the first retry runs, then exactly 1 email is delivered and no further retries are attempted.
- **AC 3.1.3** [edge] Given the owner has no email address on file, when stock drops below a threshold, then no send is attempted and the owner's dashboard shows "Add an email address to receive low-stock alerts".

## Review
**Verdict: draft (not approved).** Five open questions block full coverage: permissions, threshold lowering, failure-log location, alert timing, and which stock events trigger alerts.
- Rewritten: 7 (AC 1.1.2, 1.1.3, 2.1.1, 2.1.2, 2.1.3, 3.1.1, 3.1.2). AC 2.1.3 was rewritten as a single-action boundary test (6 to 5); its old "5 minus 0" case could not occur, and the restock case moved to AC 2.1.5. AC 1.1.3 was split into one input per criterion.
- Added: 10 (AC 1.1.4 to 1.1.8, 2.1.5 to 2.1.7, 2.2.4, 3.1.4).
- Unresolved: non-owner permissions; threshold lowering and alert reset; failure log location (AC 3.1.2); alert time bound (AC 2.1.1); manual stock edits as triggers; plus the four original open questions (default threshold, multiple recipients, digest, reminders).
