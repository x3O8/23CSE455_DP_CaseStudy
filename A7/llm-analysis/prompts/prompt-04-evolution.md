# Prompt 04 — Part 2 Evolution Analysis and Design Pattern Introduction

## Context

You are continuing a Design Patterns Case Study on the Ruby on Rails hotel booking application at:

https://github.com/andrewdsilva/rails-room-booking/tree/main

The original baseline has already been investigated and verified.

Use this immutable baseline:

- `source_version = original`
- commit = `5e15551ee646871b4bed32c982fa17da319d3ee3`

### Verified Part 1 conclusion

At the original commit, the only clearly confirmed GoF application-level pattern is:

**Template Method — `CrudConcern` shared CRUD workflow with resource-specific controller hooks.**

Relevant participants:

- `CrudConcern`
- `BookingsController`
- `RoomsController`
- `SettingsController`

The following were investigated but **must not be presented as confirmed GoF patterns** unless new evidence in the evolved design justifies them:

- Strategy
- Observer
- Adapter
- Facade
- Decorator
- Factory Method
- Abstract Factory
- Command
- State

The application also uses important Rails/framework mechanisms such as:

- Active Record
- ActiveSupport concerns
- Pundit policies
- Active Record callbacks
- Payify payment integration
- Active Storage

These should remain distinguished from GoF patterns.

---

# Objective

Perform **Part 2 of the case study**.

Analyze how the existing hotel booking application must evolve when the following four requirements are introduced:

1. **Breakfast package**
2. **Airport transfer**
3. **Room upgrade**
4. **Cancellation policy**

The goal is NOT simply to add four database fields or four methods.

The goal is to determine:

- what new domain concepts are required,
- what existing classes/responsibilities must change,
- where the original design starts becoming difficult to maintain,
- which design patterns become justified by the new requirements,
- how the architecture evolves,
- and how the evolution can be demonstrated with concrete source/design evidence.

Do not artificially introduce patterns merely because they are expected in a design-pattern assignment.

---

# Part 1 — Reconstruct the Relevant Baseline

Briefly restate only the baseline facts necessary for understanding the evolution.

Focus on:

- `User`
- `Room`
- `Booking`
- `Setting`
- existing booking creation
- existing pricing behavior
- existing payment behavior
- existing cancellation behavior
- existing `CrudConcern`
- existing model concerns
- existing policies
- relevant callbacks/integrations

Do NOT repeat the entire Part 1 architecture report.

Use the verified baseline commit:

`5e15551ee646871b4bed32c982fa17da319d3ee3`

Clearly distinguish:

- actual existing code,
- proposed Part 2 design,
- assumptions required because the original application does not contain the new requirements.

---

# Part 2 — Requirement-by-Requirement Evolution

Analyze each requirement separately.

## A. Breakfast Package

Determine:

- What domain concept should represent breakfast?
- Is breakfast a property of a room, booking, customer, or an additional service?
- How would price calculation change?
- What happens if breakfast is optional?
- What happens if different breakfast packages have different prices?
- What existing classes/methods would need modification?
- Would adding breakfast directly to `Booking` create undesirable coupling?

Consider possible designs such as:

- additional service abstraction,
- composition,
- strategy,
- decorator,
- association with a service/package object,
- or another appropriate design.

**Do not select a pattern simply because it sounds appropriate.**

For every proposed pattern, demonstrate the actual collaboration it would create.

---

# Part 3 — Airport Transfer

Analyze:

- airport pickup/drop-off requirements,
- transfer type,
- transfer pricing,
- optionality,
- booking association,
- whether airport transfer should be modeled independently from breakfast,
- whether multiple additional services should share a common abstraction.

Determine whether the design should introduce something such as:

`AdditionalService`

with concrete services such as:

- `BreakfastPackage`
- `AirportTransfer`

If so, explain the responsibility and collaboration precisely.

Investigate whether the evolved design provides evidence for:

- Strategy
- Factory
- Composite
- Decorator
- or another pattern.

Again, only confirm a pattern if its defining collaboration is actually present.

---

# Part 4 — Room Upgrade

Analyze the room upgrade requirement.

Consider:

- upgrading from one room category/type to another,
- availability of the upgraded room,
- price difference,
- interaction with the existing `Room` and `Booking`,
- whether upgrade behavior should be encapsulated,
- whether room pricing rules may vary.

Determine whether this requirement changes the design differently from optional additional services.

Explicitly compare:

**Room Upgrade vs Breakfast/Airport Transfer**

Explain why they should or should not use the same abstraction.

---

# Part 5 — Cancellation Policy

Analyze the cancellation policy carefully.

The original system has cancellation behavior in:

`Booking#cancel!`

with `canceled_at`.

Now introduce policies such as:

- free cancellation before a deadline,
- partial refund,
- no refund,
- different rules depending on room/booking/package,
- potentially different policies in the future.

Determine:

- whether cancellation rules should remain inside `Booking`,
- whether they should be extracted into a separate abstraction,
- how the cancellation policy is selected,
- how refund calculation interacts with payment,
- whether the design now provides a genuine Strategy pattern.

This section is particularly important.

If Strategy becomes justified here, provide a rigorous role mapping such as:

| Strategy role      | Evolved application element        |
| ------------------ | ---------------------------------- |
| Context            | `Booking` / cancellation service   |
| Strategy interface | `CancellationPolicy`               |
| Concrete strategy  | `FlexibleCancellationPolicy`, etc. |

Only use this mapping if the proposed architecture actually implements those responsibilities.

---

# Part 6 — Identify Design Pressure

Create a clear table showing how the four requirements create pressure on the original design.

Use a structure like:

| Requirement | Original responsibility | New responsibility | Problem if added directly | Proposed design response |
| ----------- | ----------------------- | ------------------ | ------------------------- | ------------------------ |

Look specifically for:

- growing `Booking` complexity,
- excessive conditionals,
- pricing logic becoming scattered,
- cancellation logic becoming difficult to extend,
- tight coupling between Booking and optional services,
- violation of Single Responsibility Principle,
- difficulty adding future services,
- difficulty changing policies independently.

Do not claim SOLID violations without showing the concrete design pressure.

---

# Part 7 — Pattern Discovery in the Evolved Design

This is the most important part.

Determine which patterns are **actually justified after evolution**.

Investigate at least:

### Creational

- Factory Method
- Abstract Factory
- Builder

### Structural

- Decorator
- Composite
- Adapter
- Facade

### Behavioral

- Strategy
- Template Method
- State
- Command
- Observer

### GRASP

Where useful:

- Information Expert
- Creator
- Controller
- Polymorphism
- Low Coupling
- High Cohesion
- Protected Variations

For every candidate classify it as:

- **CONFIRMED**
- **UNCERTAIN**
- **REJECTED**

Do not force the four requirements to produce four different patterns.

It is acceptable if only one or two patterns become strongly justified.

---

# Part 8 — Existing Pattern vs New Pattern

Explicitly analyze how the original confirmed Template Method pattern is affected.

Answer:

1. Does `CrudConcern` remain unchanged?
2. Does it need new hooks?
3. Does Part 2 introduce any new Template Method usage?
4. Which new patterns complement the existing Template Method?
5. Does the evolution reduce or increase controller/model complexity?

Make the distinction between:

**existing pattern retained**

and

**new pattern introduced because of changing requirements**.

---

# Part 9 — Proposed Evolved Architecture

Produce a proposed architecture for the evolved application.

At minimum consider whether the domain should contain concepts such as:

```text
User
Room
Booking
Setting
AdditionalService
BreakfastPackage
AirportTransfer
RoomUpgrade
CancellationPolicy

```

Do not assume all of these classes are necessary.

For every proposed class/module explain:

- responsibility,
- relationships,
- important methods,
- dependencies,
- why it exists.

Also identify which original classes remain unchanged.

---

# Part 10 — UML / Design Diagrams

Generate PlantUML for the most important evolved structures.

At minimum provide:

### 1. Evolved class diagram

Show:

- Booking
- Room
- User
- relevant new abstractions
- concrete services/policies
- important relationships
- pattern roles

### 2. Cancellation Strategy diagram

Only if Strategy is confirmed.

### 3. Additional-service structure

Only if a meaningful pattern/abstraction exists.

### 4. One representative sequence diagram

For example:

**Booking with breakfast + airport transfer**

or

**Booking cancellation using a cancellation policy**

Choose whichever demonstrates the most important evolved collaboration.

Do not generate unnecessary diagrams.

---

# Part 11 — Before vs After Comparison

Create a concise comparison:

| Aspect                 | Original Design | Evolved Design |
| ---------------------- | --------------- | -------------- |
| Booking responsibility |                 |                |
| Pricing                |                 |                |
| Optional services      |                 |                |
| Room upgrade           |                 |                |
| Cancellation           |                 |                |
| Extensibility          |                 |                |
| Coupling               |                 |                |
| Confirmed patterns     |                 |                |

Explain the architectural consequences, not just the class count.

---

# Part 12 — Pattern Evidence Table

Produce a table that can later be converted into `patterns.csv`.

Use these columns:

```text
source_version
pattern_name
pattern_type
instance_name
participant_roles
source_locations
intent_and_evidence
status

```

For Part 2, use:

`source_version = evolved`

For proposed design elements where no actual source code exists yet, clearly mark them as:

`proposed`

Do NOT fabricate file paths or line numbers for code that does not yet exist.

---

# Part 13 — Evolution Scenarios

Create at least these scenarios:

### Scenario 1

Add a new breakfast package.

Explain exactly what needs to change.

### Scenario 2

Add a new airport transfer type.

Explain exactly what needs to change.

### Scenario 3

Add another cancellation policy.

Explain exactly what needs to change.

### Scenario 4

Add another room upgrade option.

Explain exactly what needs to change.

For each scenario compare:

**without the proposed pattern**

vs.

**with the proposed pattern**

Focus on number/location of changes, coupling, and responsibility—not invented numerical metrics.

---

# Part 14 — Important Restrictions

Follow these strictly.

1. Do not invent existing classes or source files.
2. Do not invent line numbers.
3. Do not claim the evolved design already exists in the repository.
4. Clearly separate:
   - baseline facts,
   - proposed evolution,
   - inferred design,
   - pattern classification.
5. Do not call something Strategy merely because there is an interface.
6. Do not call something Factory merely because an object is created.
7. Do not call optional services Decorators unless there is genuine wrapper-based composition.
8. Do not call callbacks Observer.
9. Do not call Rails concerns Decorator.
10. Do not count Active Record, Rails MVC, or Pundit as GoF patterns.
11. Do not manufacture patterns to satisfy an expected number.
12. Do not use pattern names as justification; prove the collaboration.
13. If multiple designs are plausible, compare them and explain why one was selected.
14. Keep the original verified Template Method evidence unchanged.
15. Do not modify the baseline commit or reinterpret the original application to contain Part 2 features.

---

# Final Output Format

Return ONLY these sections:

## A. Baseline impact summary

## B. Requirement-by-requirement evolution

- Breakfast
- Airport Transfer
- Room Upgrade
- Cancellation Policy

## C. Design pressure table

## D. Proposed evolved architecture

## E. Confirmed evolved patterns

For each confirmed pattern provide:

- Pattern
- Category
- Intent
- Participants
- Exact role mapping
- Collaborations/interactions
- Why it qualifies
- Why alternative classifications were rejected
- Status

## F. Uncertain candidates

Table with:

- Candidate
- Evidence
- Missing evidence
- Reason uncertain

## G. Rejected candidates

Table with:

- Candidate
- Why it may appear relevant
- Why it does not qualify

## H. Before vs After comparison

## I. Evolution scenarios

## J. PlantUML diagrams

## K. Part 2 patterns.csv-ready evidence table

## L. Final Part 2 conclusion

The conclusion must clearly state:

1. Which original responsibilities became problematic.
2. Which abstractions were introduced.
3. Which patterns are genuinely justified.
4. Which patterns were considered but rejected.
5. How the evolved design is more extensible.
6. Which design elements should be implemented in Part 3.
7. The exact classes/modules/patterns that Part 3 should implement.

Do not proceed to Part 3 implementation. This prompt is only for **Part 2 analysis and design evolution**.