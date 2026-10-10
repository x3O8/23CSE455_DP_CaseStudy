# Prompt 05 — Part 3 Cross-Language Pattern Implementation and Metrics

## Context

You are completing Part 3 of a Design Patterns Case Study based on the Ruby on Rails hotel booking application:

https://github.com/andrewdsilva/rails-room-booking/tree/main

The immutable original baseline is:

- `source_version = original`
- commit = `5e15551ee646871b4bed32c982fa17da319d3ee3`

Part 1 established one confirmed GoF pattern in the original application:

**Template Method — `CrudConcern` shared CRUD workflow with resource-specific controller hooks.**

Part 2 established the following evolved design:

### Existing pattern retained

**Template Method**

- `CrudConcern`
- `BookingsController`
- `RoomsController`
- `SettingsController`

### New evolved pattern

**Strategy — Cancellation Policy**

Proposed roles:

- Context → `CancellationService`
- Strategy → `CancellationPolicy`
- Concrete Strategies:
  - `FlexibleCancellationPolicy`
  - `PartialRefundCancellationPolicy`
  - `NoRefundCancellationPolicy`

### Evolved domain abstractions

- `AdditionalService`
- `BookingService`
- `BreakfastPackage`
- `AirportTransfer`
- `RoomUpgrade`
- `CancellationService`
- `CancellationPolicy`

Important distinction:

`AdditionalService`, `BookingService`, and `RoomUpgrade` are domain abstractions, **not automatically GoF patterns**.

Do not introduce additional GoF patterns unless the implementation genuinely establishes their defining collaboration.

---

# Objective

Implement the important design-pattern concepts from the case study in **FOUR languages other than Ruby**:

1. **Java**
2. **Python**
3. **JavaScript**
4. **C++**

Do NOT implement the patterns in Ruby for Part 3 because Ruby is the source language of the original repository.

The goal is to demonstrate that the identified design patterns are language-independent design solutions, while also showing how their implementation differs across languages.

The implementations do NOT need to recreate the entire Rails application.

Instead, create a **small but complete hotel-booking domain example** that demonstrates:

- the original Template Method idea,
- the evolved Strategy-based cancellation policy,
- optional additional services,
- room upgrade,
- booking pricing,
- cancellation workflow.

The code must be executable or close to directly executable in each language.

---

# Part 1 — Define a Common Cross-Language Domain

Before writing language-specific code, establish a **language-neutral reference design**.

Use approximately this conceptual model:

```text
Booking
 ├── Room
 ├── BookingService*
 │      └── AdditionalService
 │             ├── BreakfastPackage
 │             └── AirportTransfer
 │
 ├── RoomUpgrade
 │
 └── cancellation through CancellationService
                         │
                         ▼
                CancellationPolicy
                  ├── FlexibleCancellationPolicy
                  ├── PartialRefundCancellationPolicy
                  └── NoRefundCancellationPolicy

```

Also demonstrate the original Template Method concept:

```text
Abstract/shared CRUD workflow
            │
            ▼
      concrete resource-specific behavior

```

Because the original Rails implementation uses `CrudConcern` rather than a classical abstract class, explain how the same **design intent** is represented in each target language.

---

# Part 2 — Implementation Scope

For every language, implement at least:

## Domain classes

- `Booking`
- `Room`
- `AdditionalService`
- `BreakfastPackage`
- `AirportTransfer`
- `BookingService`
- `RoomUpgrade`

## Strategy pattern

- `CancellationPolicy`
- `FlexibleCancellationPolicy`
- `PartialRefundCancellationPolicy`
- `NoRefundCancellationPolicy`
- `CancellationService`

## Template Method

Create a small resource-management example corresponding conceptually to the original:

```text
CrudWorkflow
 ├── BookingController
 ├── RoomController
 └── SettingsController

```

The implementation should demonstrate:

- a common workflow,
- resource-specific operations,
- extension points/hooks.

Do NOT simply copy Ruby syntax into another language.

Use the idioms of each language appropriately.

---

# Part 3 — Java Implementation

Create a complete Java implementation.

Requirements:

- Use appropriate Java classes/interfaces/abstract classes.
- Represent Strategy using a Java interface or appropriate abstraction.
- Represent Template Method using an abstract class where appropriate.
- Demonstrate polymorphism.
- Demonstrate booking with:
  - breakfast,
  - airport transfer,
  - room upgrade.
- Demonstrate cancellation using at least three cancellation strategies.

Include:

1. source code,
2. `main` demonstration,
3. expected output,
4. pattern-role mapping.

Keep the example reasonably compact.

---

# Part 4 — Python Implementation

Create a complete Python implementation.

Requirements:

- Use idiomatic Python.
- Use `abc.ABC` / `@abstractmethod` only where appropriate.
- Demonstrate Strategy using Python's normal polymorphism.
- Demonstrate Template Method appropriately.
- Demonstrate the same hotel-booking scenarios as Java.

Include:

1. source code,
2. runnable demonstration,
3. expected output,
4. pattern-role mapping.

Do not unnecessarily force Java-style interfaces into Python.

---

# Part 5 — JavaScript Implementation

Create a complete JavaScript implementation.

Use modern JavaScript.

Requirements:

- Use ES6+ classes where appropriate.
- Demonstrate Strategy through object/class polymorphism.
- Demonstrate Template Method in a way that is natural to JavaScript.
- Demonstrate:
  - breakfast,
  - airport transfer,
  - room upgrade,
  - cancellation policies.

Include:

1. source code,
2. runnable example,
3. expected output,
4. pattern-role mapping.

Do not use a framework such as React or Node-specific infrastructure unless genuinely necessary.

A simple standalone JavaScript program is sufficient.

---

# Part 6 — C++ Implementation

Create a complete C++ implementation.

Requirements:

- Use appropriate C++ classes.
- Use abstract base classes/interfaces where appropriate.
- Demonstrate Strategy through polymorphism.
- Demonstrate Template Method using inheritance and protected hooks where appropriate.
- Demonstrate the same booking scenarios.

Include:

1. source code,
2. `main()`,
3. expected output,
4. pattern-role mapping.

Use modern C++ practices where practical.

---

# Part 7 — Template Method Mapping

This is important because the original pattern was discovered in Ruby.

Explain how the original:

```text
CrudConcern
    ↓
shared CRUD algorithm
    ↓
controller hooks

```

maps into each language.

Create a table:

| Language      | Template Method abstraction | Concrete participants | Hook/extension mechanism        |
| ------------- | --------------------------- | --------------------- | ------------------------------- |
| Ruby baseline | `CrudConcern`               | Controllers           | Ruby module + method overriding |
| Java          |                             |                       |                                 |
| Python        |                             |                       |                                 |
| JavaScript    |                             |                       |                                 |
| C++           |                             |                       |                                 |

Do not claim the four implementations are identical internally.

The goal is to preserve the **design intent**, not the exact syntax.

---

# Part 8 — Strategy Mapping

Create the equivalent table:

| Language   | Context | Strategy | Concrete Strategies | Delegated variation |
| ---------- | ------- | -------- | ------------------- | ------------------- |
| Java       |         |          |                     |                     |
| Python     |         |          |                     |                     |
| JavaScript |         |          |                     |                     |
| C++        |         |          |                     |                     |

For every language, prove that:

```text
CancellationService
        ↓
CancellationPolicy
        ↓
selected cancellation algorithm

```

actually occurs in the implementation.

---

# Part 9 — Demonstration Scenarios

Every language must demonstrate the same conceptual scenarios.

## Scenario A — Basic booking

Create a booking for a room.

## Scenario B — Booking with breakfast

Add a breakfast package and show its effect on the booking total.

## Scenario C — Booking with airport transfer

Add an airport transfer and show its effect on the booking total.

## Scenario D — Room upgrade

Upgrade the booking to another room and show the price difference.

## Scenario E — Flexible cancellation

Cancel using the flexible policy and demonstrate the refund result.

## Scenario F — Partial refund

Cancel using the partial-refund policy and demonstrate the refund result.

## Scenario G — No refund

Cancel using the no-refund policy and demonstrate the refund result.

## Scenario H — Add a new cancellation policy

Show how another cancellation policy could be added without modifying the main cancellation workflow.

This last scenario is particularly important for proving Strategy.

---

# Part 10 — Cross-Language Equivalence

After all four implementations, provide a comparison table:

| Design element                    | Java | Python | JavaScript | C++ |
| --------------------------------- | ---- | ------ | ---------- | --- |
| Strategy abstraction              |      |        |            |     |
| Concrete strategies               |      |        |            |     |
| Context                           |      |        |            |     |
| Template Method                   |      |        |            |     |
| Additional services               |      |        |            |     |
| Room upgrade                      |      |        |            |     |
| Polymorphism mechanism            |      |        |            |     |
| Main language-specific difference |      |        |            |     |

Explain which differences are caused by language characteristics rather than design differences.

---

# Part 11 — Metrics

Produce meaningful code/design metrics for each implementation.

At minimum calculate or report:

- total lines of code,
- number of classes,
- number of interfaces/abstract classes where applicable,
- number of concrete strategies,
- number of methods,
- number of dependencies between major components,
- number of conditional branches in cancellation logic,
- number of files.

Do NOT invent measurements.

If exact LOC or other metrics are not manually verified, provide a clearly marked estimate or explain how the metric should be calculated from the final files.

Prefer metrics that demonstrate the design benefit.

For example:

### Before Strategy

```text
CancellationService
    └── multiple conditional branches

```

### After Strategy

```text
CancellationService
    └── delegates to CancellationPolicy

```

If you provide a numerical metric, ensure it is calculated from the actual code produced.

---

# Part 12 — Pattern Verification

After implementing the code, independently verify whether the implementations genuinely satisfy the patterns.

For each language classify:

- Template Method → CONFIRMED / UNCERTAIN / REJECTED
- Strategy → CONFIRMED / UNCERTAIN / REJECTED

For each classification provide:

- participants,
- role mapping,
- key interactions,
- exact class/method names,
- why the implementation qualifies.

Do not automatically mark a pattern confirmed merely because the class was named after the pattern.

---

# Part 13 — Testing / Execution

Where possible, provide simple test cases or executable demonstrations.

At minimum test:

1. normal booking,
2. breakfast,
3. airport transfer,
4. room upgrade,
5. flexible cancellation,
6. partial refund,
7. no refund,
8. addition of a new cancellation policy.

Do NOT claim that code was executed unless execution actually occurred.

If execution is unavailable, explicitly label the output as:

**Expected output**

rather than:

**Actual output**

Do not fabricate test results.

---

# Part 14 — Part 3 Evidence Table

Produce a CSV-ready table with:

```text
language
pattern_name
pattern_type
instance_name
context
strategy_or_template_role
concrete_participants
key_methods
interaction_description
implementation_file
status

```

Use the actual filenames/classes generated in the answer.

For example:

```text
Java,Strategy,Cancellation Policy,...
Python,Strategy,Cancellation Policy,...
JavaScript,Strategy,Cancellation Policy,...
C++,Strategy,Cancellation Policy,...

```

---

# Part 15 — Repository Structure

Propose the exact GitHub repository structure for the final implementation.

For example:

```text
design-patterns-case-study/
│
├── README.md
├── report/
│   └── case-study-report.pdf
│
├── data/
│   ├── patterns.csv
│   ├── evidence.csv
│   └── metrics.csv
│
├── uml/
│
├── part1/
│   └── baseline-analysis/
│
├── part2/
│   └── evolution-design/
│
├── part3/
│   ├── java/
│   ├── python/
│   ├── javascript/
│   └── cpp/
│
└── llm-analysis/
    ├── prompts/
    └── results/

```

Adapt this structure if a better organization is justified.

Do not create the GitHub repository yet.

---

# Part 16 — Final Part 3 Recommendations

End with a concise implementation summary containing:

### A. Patterns implemented

- Template Method
- Strategy

### B. Domain abstractions implemented

- AdditionalService
- BreakfastPackage
- AirportTransfer
- BookingService
- RoomUpgrade
- CancellationService
- CancellationPolicy and concrete policies

### C. Four target languages

- Java
- Python
- JavaScript
- C++

### D. Files that should eventually be placed in GitHub

Give the exact filenames.

### E. Anything that remains unresolved

Especially identify:

- Payify/Stripe refund behavior,
- anything that cannot be verified from the original repository,
- any assumptions made in the simplified implementation.

---

# Critical Restrictions

1. **Ruby is NOT one of the four implementation languages.**
2. The four implementation languages are exactly:
   - Java
   - Python
   - JavaScript
   - C++
3. Do not recreate the entire Rails application.
4. Implement a compact, language-independent domain demonstration.
5. Do not introduce unnecessary design patterns.
6. Do not claim a pattern merely because a class/interface has a pattern-related name.
7. Do not fabricate execution results.
8. Do not fabricate metrics.
9. Clearly distinguish:
   - original repository evidence,
   - proposed Part 2 design,
   - actual Part 3 implementation.
10. Keep the four implementations conceptually equivalent so they can be compared in the final report.
11. Use idiomatic constructs for each language rather than mechanically translating syntax.
12. The original Ruby Template Method must be explained as the inspiration/baseline, while the four implementations demonstrate the same design intent in other languages.
13. Strategy must demonstrate actual delegation from the cancellation context to interchangeable policy implementations.
14. Do not introduce a Factory solely to instantiate strategies unless there is a genuine design reason.
15. Do not introduce Decorator, Observer, Adapter, Composite, Builder, State, or other patterns unless their defining collaborations genuinely arise.
16. Keep the code compact enough that it can reasonably be included in a student case-study repository.
17. Do not proceed to writing the final case-study report yet.

# Final Output Order

Return the result in exactly this order:

1. Common reference design
2. Java implementation
3. Python implementation
4. JavaScript implementation
5. C++ implementation
6. Template Method cross-language mapping
7. Strategy cross-language mapping
8. Demonstration scenarios and expected outputs
9. Cross-language comparison
10. Metrics
11. Pattern verification
12. Testing status
13. Part 3 CSV-ready evidence
14. Proposed GitHub structure
15. Final Part 3 implementation summary