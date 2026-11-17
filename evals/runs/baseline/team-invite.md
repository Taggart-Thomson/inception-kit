---
intent: "Let a workspace admin invite teammates by email and give each a role"
slug: team-invite
status: draft
---

# Spec: Team invitations with roles

## Intent
A workspace admin can invite people to the workspace by email address and choose a role for each invitee. The invitee joins the workspace with that role once they accept.

## Assumptions
- The workspace already has an authentication system and a defined, fixed set of roles (for example Admin, Member, Viewer).
- Only users with the Admin role count as "workspace admins" and may send invitations.
- Invitations are delivered by email containing a unique link; the invitee must accept to join.
- Invitees may or may not already have an account; both cases are supported.
- Invitations expire after a fixed period (assumed 7 days).
- A role is assigned at invitation time and can be changed by an admin after the invitee has joined, but role editing for existing members is out of scope here.
- One email address has at most one pending invitation per workspace.

## Open questions
- Which roles exist, and may an admin invite another Admin?
- Is there a limit on the number of members or pending invitations per workspace (for example plan seat limits)?
- How long should an invitation remain valid?
- Must the invitee sign up or log in with the same email address that was invited?
- Are invitations restricted to certain email domains?

## Unit 1: Send invitations

### Story 1.1: Invite a teammate by email with a role
As a workspace admin, I want to enter a teammate's email address and choose a role, so that they receive an invitation to join with the right access.

#### Acceptance criteria
- **AC 1.1.1** Given I am an admin viewing the invite form, when I enter a valid email, select a role, and submit, then a pending invitation appears in the invitation list with that email and role, and an email is sent to that address.
- **AC 1.1.2** [edge] Given I am an admin, when I submit an email address that is malformed, then the form shows a validation error and no invitation is created.
- **AC 1.1.3** [edge] Given I am an admin, when I submit without selecting a role, then the form shows a validation error and no invitation is created.
- **AC 1.1.4** [edge] Given the email already belongs to a current workspace member, when I submit the invitation, then I see a message that the person is already a member and no invitation is created.
- **AC 1.1.5** [edge] Given a pending invitation exists for the email, when I invite the same email again, then I am told an invitation is already pending and no duplicate is created.
- **AC 1.1.6** [edge] Given I am a user without the Admin role, when I try to open the invite form or call the invite action, then access is denied and no invitation is created.

### Story 1.2: Invite several teammates at once
As a workspace admin, I want to enter multiple email addresses in one submission, so that I can onboard a team quickly.

#### Acceptance criteria
- **AC 1.2.1** Given I am an admin, when I enter several valid emails separated by commas or new lines and choose a role for each, then one invitation is created per email and I see a summary of how many were sent.
- **AC 1.2.2** [edge] Given the list contains both valid and invalid emails, when I submit, then valid ones are sent and each invalid one is reported by address with the reason.
- **AC 1.2.3** [edge] Given the list contains the same email twice, when I submit, then only one invitation is created for it.

## Unit 2: Accept an invitation

### Story 2.1: Join the workspace from an invitation email
As an invited teammate, I want to accept the invitation from the email link, so that I can join the workspace with the role I was given.

#### Acceptance criteria
- **AC 2.1.1** Given I have a valid pending invitation and an existing account, when I open the link and log in, then I am added to the workspace with the invited role and the invitation is marked accepted.
- **AC 2.1.2** Given I have a valid pending invitation and no account, when I open the link and complete sign-up, then my account is created, I am added to the workspace with the invited role, and the invitation is marked accepted.
- **AC 2.1.3** [edge] Given the invitation has expired, when I open the link, then I see a message that it has expired and I am not added to the workspace.
- **AC 2.1.4** [edge] Given the invitation was revoked, when I open the link, then I see a message that it is no longer valid and I am not added.
- **AC 2.1.5** [edge] Given the invitation was already accepted, when I open the link again, then I am not added a second time and am directed to the workspace or login.
- **AC 2.1.6** [edge] Given the link token is altered or unknown, when I open it, then I see a generic invalid-link message that reveals no workspace details.

## Unit 3: Manage pending invitations

### Story 3.1: View pending invitations
As a workspace admin, I want to see all invitations and their status, so that I know who has yet to join.

#### Acceptance criteria
- **AC 3.1.1** Given invitations exist, when I open the invitation list, then each shows email, role, status (pending, accepted, expired, revoked), and date sent.
- **AC 3.1.2** [edge] Given no invitations exist, when I open the list, then I see an empty state with a prompt to invite someone.

### Story 3.2: Resend or revoke an invitation
As a workspace admin, I want to resend or revoke a pending invitation, so that I can fix mistakes or cancel access I no longer want to grant.

#### Acceptance criteria
- **AC 3.2.1** Given a pending invitation, when I choose Resend, then a new email is sent and the expiry period restarts.
- **AC 3.2.2** Given a pending invitation, when I choose Revoke, then its status becomes revoked and its link no longer lets anyone join.
- **AC 3.2.3** [edge] Given an invitation that is accepted, when I view its actions, then Resend and Revoke are unavailable.
- **AC 3.2.4** [edge] Given an invitation that is expired, when I choose Resend, then the invitation is made valid again with the same role and a new email is sent.
