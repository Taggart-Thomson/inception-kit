---
intent: "Let customers reschedule a booked appointment up to 24 hours before it starts"
slug: reschedule-booking
status: draft
---

# Spec: Reschedule a booked appointment

## Intent
Customers can move an appointment they have already booked to a different time, as long as they do so at least 24 hours before the appointment's current start time.

## Assumptions
- Customers are signed in, or otherwise verified, and can only reschedule their own appointments.
- The 24-hour cutoff is measured against the appointment's current start time, in the appointment location's time zone.
- A reschedule keeps the same service, provider and booking record; only the date and time change.
- The new time must be a slot that is currently available for that service and provider.
- Rescheduling is allowed any number of times, provided each attempt is at least 24 hours before the current start time.
- Exactly 24 hours before start counts as still allowed.
- Rescheduling is not charged a fee, and no payment changes.
- Customers receive a confirmation by the same channel(s) used for booking confirmations.

## Open questions
- Is there a limit on how many times one appointment can be rescheduled?
- Should the new time also have to be at least 24 hours in the future, or may it be any available slot?
- Can the customer change the provider or service while rescheduling, or only the time?
- What should customers inside the 24-hour window see: only a message, or contact details for staff to help?
- Can staff reschedule on a customer's behalf inside the 24-hour window, and is that in scope?
- Should the original slot be released immediately and offered to other customers?
- Do any appointment types (e.g. deposit-paid or custom services) have different or no rescheduling rules?

## Unit 1: Reschedule eligibility rule

### Story 1.1: Know whether an appointment can be rescheduled
As a customer, I want to see whether my appointment can still be rescheduled, so that I know my options before I try.

#### Acceptance criteria
- **AC 1.1.1** Given a booked appointment that starts more than 24 hours from now, when I view it, then a "Reschedule" action is available.
- **AC 1.1.2** [edge] Given a booked appointment that starts exactly 24 hours from now, when I view it, then the "Reschedule" action is available.
- **AC 1.1.3** [edge] Given a booked appointment that starts less than 24 hours from now, when I view it, then the "Reschedule" action is not offered and a message explains that changes are no longer possible online.
- **AC 1.1.4** [edge] Given a cancelled, completed or past appointment, when I view it, then no "Reschedule" action is offered.

### Story 1.2: Enforce the cutoff on the server
As a business owner, I want the 24-hour rule enforced by the system and not just the screen, so that late changes cannot slip through.

#### Acceptance criteria
- **AC 1.2.1** Given an appointment starting in more than 24 hours, when a reschedule request is submitted, then it is accepted for processing.
- **AC 1.2.2** [edge] Given an appointment that crossed inside 24 hours while I had the reschedule screen open, when I submit the new time, then the request is rejected, the appointment is unchanged, and I see a message that the cutoff has passed.
- **AC 1.2.3** [edge] Given a reschedule request for an appointment that belongs to another customer, when it is submitted, then it is rejected and nothing changes.

## Unit 2: Choose a new time and confirm

### Story 2.1: Pick a new available time
As a customer, I want to choose a new date and time from available slots, so that my appointment fits my schedule.

#### Acceptance criteria
- **AC 2.1.1** Given I opened Reschedule on an eligible appointment, when the screen loads, then I see only slots that are available for the same service and provider.
- **AC 2.1.2** Given I select an available slot and confirm, when the change succeeds, then the appointment shows the new date and time and no longer shows the old one.
- **AC 2.1.3** [edge] Given the slot I selected was taken by someone else before I confirmed, when I confirm, then the change is rejected, my original appointment is kept, and I am asked to choose another slot.
- **AC 2.1.4** [edge] Given no slots are available, when I open Reschedule, then I see a message saying so and my original appointment remains booked.
- **AC 2.1.5** [edge] Given I select the same time as my current appointment, when I try to confirm, then I am told nothing would change and no update is made.

### Story 2.2: Free the original slot
As a business owner, I want the old time released when a customer moves, so that it can be booked by someone else.

#### Acceptance criteria
- **AC 2.2.1** Given a successful reschedule, when it completes, then the original slot appears as available to other customers.
- **AC 2.2.2** [edge] Given the reschedule fails for any reason, when the failure occurs, then the original slot stays held for me and the new slot is not reserved.

## Unit 3: Notifications and record keeping

### Story 3.1: Receive confirmation of the change
As a customer, I want a confirmation of my new appointment time, so that I have a record of it.

#### Acceptance criteria
- **AC 3.1.1** Given a successful reschedule, when it completes, then I receive a confirmation stating the new date, time, service and provider, and the previous time.
- **AC 3.1.2** [edge] Given the confirmation cannot be delivered, when the reschedule completes, then the appointment is still changed and the new details are shown on screen.

### Story 3.2: Keep a history of changes
As a staff member, I want to see when and how an appointment was rescheduled, so that I can answer customer questions.

#### Acceptance criteria
- **AC 3.2.1** Given an appointment has been rescheduled, when staff view it, then they see the previous time, the new time, and when the change was made.
- **AC 3.2.2** [edge] Given an appointment has been rescheduled more than once, when staff view it, then every change is listed in order.
