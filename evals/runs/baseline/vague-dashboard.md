---
intent: "Make the dashboard better"
slug: make-dashboard-better
status: draft
---

# Spec: Improve the dashboard

## Intent
Improve the existing dashboard so it is more useful and pleasant for its users. The intent does not say what "better" means, so this spec proposes performance, clarity and usability improvements for confirmation.

## Assumptions
- There is one existing dashboard that users open to see key metrics.
- "Better" means faster loading, easier-to-read information and relevant filtering, not new data sources.
- The current users are signed-in internal users on desktop and mobile browsers.
- No change to who may see which data is intended.

## Open questions
- What does "better" mean to the product owner: speed, visual design, new metrics, or something else?
- Which dashboard and which user group is this for?
- Which metrics matter most to users and should be shown first?
- Is there a target load time or other measurable success criterion?
- Are there known complaints or analytics that prompted this request?

## Unit 1: Faster loading

### Story 1.1: Quick initial load
As a dashboard user, I want the dashboard to load quickly, so that I can see my numbers without waiting.

#### Acceptance criteria
- **AC 1.1.1** Given a user with a normal connection, when they open the dashboard, then the main content is visible within the load-time target agreed with the product owner.
- **AC 1.1.2** [edge] Given one data widget fails or is slow to respond, when the dashboard loads, then the other widgets still display and the failing widget shows an error message with a retry option.

### Story 1.2: Loading feedback
As a dashboard user, I want to see that data is loading, so that I know the page has not frozen.

#### Acceptance criteria
- **AC 1.2.1** Given data is still being fetched, when the dashboard is displayed, then each pending widget shows a loading indicator.
- **AC 1.2.2** [edge] Given a widget returns no data, when loading completes, then it shows an "No data available" message rather than a blank area.

## Unit 2: Clearer presentation

### Story 2.1: Prioritised layout
As a dashboard user, I want the most important metrics at the top, so that I can grasp the key status at a glance.

#### Acceptance criteria
- **AC 2.1.1** Given the dashboard is open, when the user views it without scrolling, then the metrics agreed as highest priority are visible.
- **AC 2.1.2** [edge] Given a narrow phone-width screen, when the dashboard is displayed, then widgets stack in one column with no horizontal page scrolling.

### Story 2.2: Readable values
As a dashboard user, I want numbers and charts labelled with units and dates, so that I can interpret them correctly.

#### Acceptance criteria
- **AC 2.2.1** Given any chart or figure, when it is displayed, then it shows a title, units and the time period it covers.
- **AC 2.2.2** [edge] Given a very large or very small value, when it is displayed, then it is formatted readably (for example 1.2M) and the full value is available on hover or tap.

## Unit 3: Filtering and control

### Story 3.1: Date range filter
As a dashboard user, I want to choose a date range, so that I can focus on the period I care about.

#### Acceptance criteria
- **AC 3.1.1** Given the dashboard is open, when the user selects a date range, then all widgets update to that range.
- **AC 3.1.2** [edge] Given the user selects an end date earlier than the start date, when they apply the filter, then the filter is rejected with a clear message and the previous range remains.

### Story 3.2: Remembered preferences
As a returning user, I want my chosen filters kept, so that I do not have to set them every visit.

#### Acceptance criteria
- **AC 3.2.1** Given a user has set a filter, when they return to the dashboard later, then the same filter is applied.
- **AC 3.2.2** [edge] Given saved preferences are unavailable or invalid, when the dashboard opens, then it falls back to the default view without an error.
