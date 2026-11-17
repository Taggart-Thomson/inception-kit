---
intent: "Email the shop owner when an item's stock falls below a threshold they set"
slug: low-stock-alert
status: draft
---

# Spec: Low-stock email alerts

## Intent
The shop owner can set a stock threshold for an item. When the item's stock falls below that threshold, the system sends the owner an email so they can restock.

## Assumptions
- Each shop has one owner account with a verified email address that receives alerts.
- Thresholds are set per item; an item with no threshold set triggers no alerts.
- "Falls below" means stock drops from at or above the threshold to strictly below it.
- Stock levels are already tracked in the system and change through sales, manual adjustments and returns.
- Only one alert is sent per crossing; further decreases while the item stays below the threshold do not send more emails.
- The alert re-arms once stock returns to or above the threshold.
- Threshold is a whole number of 0 or more.

## Open questions
- Should alerts also be sent to additional recipients (staff, multiple owners), or only the owner?
- Should the owner be able to turn alerts off for an item without clearing its threshold?
- Should an item hitting zero stock send a distinct "out of stock" email, or is the low-stock email enough?
- Should multiple items crossing their thresholds in a short period be batched into one digest email?
- Is there a default threshold for items where the owner has not set one?

## Unit 1: Set and manage item thresholds

### Story 1.1: Set a low-stock threshold
As a shop owner, I want to set a low-stock threshold on an item, so that I control when I am warned about it.

#### Acceptance criteria
- **AC 1.1.1** Given an item with no threshold, when the owner enters a threshold of 5 and saves, then the item shows a threshold of 5 on reload.
- **AC 1.1.2** [edge] Given the owner is editing a threshold, when they enter a negative number, a decimal or non-numeric text and save, then the save is rejected with a clear message and the previous value is unchanged.
- **AC 1.1.3** [edge] Given the owner is editing a threshold, when they enter 0 and save, then the threshold is saved as 0.

### Story 1.2: Change or remove a threshold
As a shop owner, I want to change or clear an item's threshold, so that alerts stay relevant as my business changes.

#### Acceptance criteria
- **AC 1.2.1** Given an item with a threshold of 5, when the owner changes it to 10 and saves, then future alert checks use 10.
- **AC 1.2.2** Given an item with a threshold, when the owner clears it and saves, then the item has no threshold and no alert is sent when its stock drops.
- **AC 1.2.3** [edge] Given an item with stock 7 and a threshold of 5, when the owner raises the threshold to 10, then the item is treated as below threshold and one alert is sent.

## Unit 2: Detect threshold crossings and send the alert email

### Story 2.1: Receive an email when stock falls below threshold
As a shop owner, I want an email when an item's stock falls below my threshold, so that I can reorder before running out.

#### Acceptance criteria
- **AC 2.1.1** Given an item with threshold 5 and stock 5, when a sale reduces stock to 4, then one email is sent to the owner's address.
- **AC 2.1.2** Given an alert email is sent, when the owner opens it, then it shows the item name, current stock and the threshold.
- **AC 2.1.3** Given an item with threshold 5 and stock 8, when stock is reduced to 6, then no email is sent.
- **AC 2.1.4** [edge] Given an item with threshold 5 and stock 5, when stock stays at 5 after an action, then no email is sent (equal to threshold is not below).
- **AC 2.1.5** [edge] Given an item with no threshold, when its stock drops to 0, then no email is sent.
- **AC 2.1.6** [edge] Given a manual stock adjustment lowers stock below the threshold, when it is saved, then an alert is sent the same as for a sale.

### Story 2.2: Avoid repeated alerts
As a shop owner, I want only one email per drop below the threshold, so that my inbox is not flooded.

#### Acceptance criteria
- **AC 2.2.1** Given an item already below its threshold and alerted, when stock falls further, then no additional email is sent.
- **AC 2.2.2** Given an alerted item, when stock is restocked to the threshold or above and later drops below again, then a new email is sent.
- **AC 2.2.3** [edge] Given two sales reduce an item below the threshold at nearly the same moment, when both are processed, then only one email is sent.

## Unit 3: Delivery reliability

### Story 3.1: Handle email delivery problems
As a shop owner, I want alerts not to be lost or to break sales when email fails, so that I can trust the feature.

#### Acceptance criteria
- **AC 3.1.1** Given the email service is temporarily unavailable, when an alert is due, then the sale still completes and the alert is retried until it is delivered or retries are exhausted.
- **AC 3.1.2** [edge] Given all retries fail, when the final attempt fails, then the failure is recorded in a log visible to the shop's administrators and the item is not marked as alerted.
- **AC 3.1.3** [edge] Given the owner has no valid email address on file, when an alert is due, then no email is sent and the owner sees a notice in the shop dashboard asking them to add an address.
