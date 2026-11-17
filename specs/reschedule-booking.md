---
intent: "Let customers reschedule a booked appointment up to 24 hours before it starts (save the spec as specs/reschedule-booking.md)"
slug: reschedule-booking
status: draft
---

# Spec: Reschedule a booked appointment

## Intent
A customer with a booked appointment can move it to another available time slot, as long as the request is made at least 24 hours before the appointment's current start time. Inside that window the customer cannot reschedule themselves.

## Assumptions
- Customers are signed in and can only reschedule their own appointments.
- The 24-hour cutoff is measured against the appointment's current start time, in the appointment location's time zone.
- Rescheduling changes the existing booking (same booking ID); it does not create a new booking.
- A booking can be rescheduled more than once, provided each request meets the 24-hour cutoff.
- Only bookings with status "confirmed" can be rescheduled.
- The new time must be an open slot for the same service and provider.

## Open questions
- Is exactly 24 hours before the start allowed (inclusive cutoff)? This spec assumes yes.
- Is there a limit on how many times one booking can be rescheduled?
- Must the new slot also be at least 24 hours in the future, or can a customer move an appointment to a slot that starts sooner?
- Do fees, deposits or price differences apply when rescheduling?
- Can the customer change the provider or service while rescheduling, or only the time?
- Is "24 hours" 24 elapsed hours or the same wall-clock time the previous day? Results differ across a daylight-saving change. Blocks a precise test of AC 1.1.2, 1.1.3 and 1.2.7 near DST.
- How far ahead does the slot picker look? AC 2.2.1 assumes 60 days; confirm.
- What message is shown when the save fails because of a server or network error (the booking must stay unchanged)? No criterion can be written until the text is decided.
- What is the exact format and time zone of the start times in the confirmation email?
- What message or code is returned when a customer tries to reschedule another customer's booking (AC 1.2.6)?

## Unit 1: Reschedule eligibility

### Story 1.1: Reschedule outside the cutoff
As a customer, I want to reschedule my appointment when it is more than 24 hours away, so that I can adapt to changes in my plans without cancelling.

#### Acceptance criteria
- **AC 1.1.1** Given a confirmed booking that starts in 48 hours, when the customer opens it, then a "Reschedule" button is visible and enabled.
- **AC 1.1.2** Given a confirmed booking whose server-side start time is exactly 24 hours 0 minutes 0 seconds after the server clock time of the request (clock frozen in the test), when the customer submits a reschedule to an open slot, then the booking's start time is updated to that slot and no error message is shown. (Depends on the inclusive-cutoff open question.)
- **AC 1.1.4** [edge] Given a confirmed booking that starts in 24 hours 1 minute, when the customer submits a reschedule to an open slot, then the booking's start time is updated to that slot and no error message is shown.
- **AC 1.1.3** [edge] Given a confirmed booking that starts in 23 hours 59 minutes, when the customer submits a reschedule, then the request is rejected with the message "Appointments can only be rescheduled up to 24 hours before they start." and the booking time is unchanged.

### Story 1.2: Blocked states
As a customer, I want to be told clearly when I cannot reschedule, so that I know what to do next.

#### Acceptance criteria
- **AC 1.2.1** Given a confirmed booking that starts in 10 hours, when the customer opens it, then the "Reschedule" button is disabled and the text "Rescheduling closed 24 hours before start" is shown.
- **AC 1.2.2** [edge] Given a booking with status "cancelled", when the customer opens it, then no "Reschedule" button is shown.
- **AC 1.2.4** [edge] Given a booking with status "completed", when the customer opens it, then no "Reschedule" button is shown.
- **AC 1.2.5** [edge] Given a booking with status "cancelled", when a reschedule request for it is sent directly to the server, then the request is rejected and the booking's start time and status are unchanged.
- **AC 1.2.6** [edge] Given a confirmed booking owned by customer A, when signed-in customer B sends a reschedule request for it, then the request is rejected and the booking's start time is unchanged.
- **AC 1.2.7** [edge] Given a confirmed booking that starts in 23 hours 59 minutes, when the customer opens it, then the "Reschedule" button is disabled and the text "Rescheduling closed 24 hours before start" is shown.
- **AC 1.2.3** [edge] Given a customer who opened the booking 25 hours before start and submits the reschedule 23 hours before start, when the request reaches the server, then it is rejected with the cutoff message and the booking time is unchanged.

## Unit 2: Choosing and saving the new time

### Story 2.1: Pick a new slot
As a customer, I want to choose from the open slots, so that I can move my appointment to a time that suits me.

#### Acceptance criteria
- **AC 2.1.1** Given the customer clicks "Reschedule", when the slot picker opens, then it lists only open slots for the same service and provider, and the current slot is not listed.
- **AC 2.1.2** Given the customer selects an open slot and confirms, when the save completes, then the booking shows the new start time, keeps the same booking ID, and the old slot becomes open again.
- **AC 2.1.3** [edge] Given two customers select the same last open slot, when both confirm, then exactly one booking is saved to that slot and the other customer sees "That time was just taken. Please choose another." with their original booking unchanged.

### Story 2.2: No available slots
As a customer, I want a clear result when nothing else is available, so that I am not left in a dead end.

#### Acceptance criteria
- **AC 2.2.1** [edge] Given no open slots exist for the next 60 days, when the customer clicks "Reschedule", then the picker shows "No other times are available" and the original booking stays confirmed.
- **AC 2.2.2** [edge] Given the customer closes the picker without confirming, when they return to the booking, then the original start time is unchanged.

## Unit 3: Confirmation and records

### Story 3.1: Confirm the change
As a customer, I want confirmation that my appointment moved, so that I trust the new time.

#### Acceptance criteria
- **AC 3.1.1** Given a successful reschedule, when the save completes, then one confirmation email containing the old start time and the new start time is sent to the booking customer's email address within 1 minute of the save. (Time format and time zone in the email are an open question.)
- **AC 3.1.2** [edge] Given the confirmation email fails to send, when the reschedule is saved, then the new time is still saved and the booking page shows the new time.

### Story 3.2: Audit trail
As a business owner, I want each reschedule recorded, so that I can resolve disputes.

#### Acceptance criteria
- **AC 3.2.1** Given a successful reschedule, when it is saved, then one history entry is stored with the old start time, new start time, customer ID and a timestamp.
- **AC 3.2.2** [edge] Given a reschedule rejected for being inside the 24-hour cutoff, when the rejection is returned, then no history entry is stored and the booking's start time is unchanged.
- **AC 3.2.3** [edge] Given a reschedule rejected because the chosen slot was just taken, when the rejection is returned, then no history entry is stored and no confirmation email is sent.

## Review

**Verdict: draft (not approved).**

- Criteria rewritten: 3 (AC 1.1.2, AC 1.2.2 split by status, AC 3.1.1).
- Criteria added: 6 (AC 1.1.4, 1.2.4, 1.2.5, 1.2.6, 1.2.7, 3.2.3; AC 1.2.4 is the completed-status case split from 1.2.2). 
- Still unresolved:
  - Inclusive 24-hour cutoff is an assumption, not a decision; AC 1.1.2 depends on it.
  - Whether the new slot must also be 24+ hours away blocks AC 2.1.1 (picker contents).
  - 24 elapsed hours vs wall-clock day across DST is undecided.
  - Picker look-ahead window (60 days in AC 2.2.1) is unconfirmed.
  - Error message for a failed save (server/network) is undecided, so no criterion exists for it.
  - Email time format and time zone are undecided (AC 3.1.1).
  - Rejection message for another customer's booking (AC 1.2.6) is undecided.
  - Reschedule limit, fees/deposits and provider/service change remain open.
