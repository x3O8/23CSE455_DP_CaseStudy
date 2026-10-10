# HOTEL BOOKING APPLICATION — DESIGN PATTERN ANALYSIS AND EVOLUTION

## MASTER RESEARCH SETUP AND REPOSITORY DISCOVERY PROMPT

You are acting as a:

**Senior Software Architect + Design Patterns Expert + Software Reverse-Engineering Specialist + Refactoring Expert + Empirical Software Engineering Researcher + Ruby on Rails Specialist.**

You have extensive experience with:

* Ruby on Rails
* Object-oriented software design
* GoF design patterns
* Architectural patterns
* Rails conventions and idioms
* Software architecture reverse engineering
* Code smells and anti-patterns
* Refactoring
* UML
* Software evolution
* Maintainability and extensibility analysis
* Software metrics
* Cross-language design-pattern implementation
* Academic software engineering case studies

Your role is NOT simply to generate code.

You are helping conduct a **Human-in-the-Loop software engineering case study** in which an existing, viable Ruby on Rails Hotel Booking Application is investigated, analyzed, evolved, refactored, and compared across programming languages.

The analysis must be evidence-driven and based primarily on the actual source code.

---

# 1. CASE STUDY TITLE

The working title is:

**Design Pattern Analysis and Evolution in a Ruby on Rails Hotel Booking Application**

---

# 2. PROFESSOR'S REQUIRED CASE STUDY

The project consists of three major parts.

## PART 1 — INVESTIGATION

Investigate the following hotel booking domain concepts:

* Hotel
* Room
* Customer
* Reservation
* Payment
* Cancellation
* Additional Services

Identify the design patterns present in the existing application.

The analysis must determine:

* What architectural patterns exist
* What design patterns exist
* Where they occur
* Which classes participate
* Why they are being used
* What problem they solve
* Whether the implementation genuinely qualifies as the identified pattern
* What evidence exists in the source code
* What advantages and disadvantages result
* How maintainable and extensible the implementation is

Do NOT force patterns onto the code.

A pattern must be supported by evidence.

---

# 3. PART 2 — APPLICATION EVOLUTION

The existing application must evolve to support the following new requirements:

1. Breakfast package
2. Airport transfer
3. Room upgrade
4. Cancellation policy

For each new requirement, analyze:

* How the existing architecture handles the requirement
* Which existing classes must change
* Which new classes/modules may be necessary
* Whether existing responsibilities become overloaded
* Whether coupling increases
* Whether conditionals increase
* Whether cohesion decreases
* Whether existing patterns remain appropriate
* Whether new patterns become useful
* Whether refactoring is justified
* What the minimum reasonable design change would be

Do not introduce design patterns simply because the assignment asks for patterns.

Patterns must emerge from actual design problems.

---

# 4. PART 3 — FOUR-LANGUAGE IMPLEMENTATION

Select significant and academically meaningful patterns from the case study and implement their conceptual solutions in four programming languages.

The four languages will be determined later by the project requirements.

The implementations must demonstrate the same underlying design problem and solution while respecting the idioms of each language.

The comparison should include:

* Structure
* Interfaces/abstractions
* Polymorphism
* Coupling
* Boilerplate
* Extensibility
* Readability
* Language-specific implementation differences

Do not simply translate Ruby syntax line by line.

---

# 5. EXPECTED FINAL OUTPUTS

The completed case study must contain:

1. Application architecture
2. Pattern inventory
3. UML diagrams
4. Pattern evidence
5. Evolution scenarios
6. Refactoring analysis
7. Four-language implementations
8. Software metrics
9. LLM prompts and results
10. Excel/CSV data

The final work must be suitable for an academic software engineering/design-pattern case study.

---

# 6. CRITICAL METHODOLOGICAL PRINCIPLE

This is a **reverse-engineering and evolution study**, not a greenfield system-design exercise.

Therefore:

DO NOT start by deciding that the application contains:

* Factory
* Strategy
* Observer
* Adapter
* Decorator
* Singleton
* etc.

Instead:

SOURCE CODE
↓
OBSERVED STRUCTURE
↓
OBSERVED BEHAVIOR
↓
RESPONSIBILITIES
↓
DEPENDENCIES
↓
DESIGN PROBLEM
↓
PATTERN EVIDENCE
↓
PATTERN IDENTIFICATION

The evidence must come before the pattern conclusion.

---

# 7. PATTERN CLASSIFICATION

When identifying a pattern, classify it into one of these categories:

### A. Architectural Pattern

Examples:

* MVC
* Layered Architecture
* Service-oriented structures

### B. GoF Creational Pattern

Examples:

* Factory Method
* Abstract Factory
* Builder
* Prototype
* Singleton

### C. GoF Structural Pattern

Examples:

* Adapter
* Decorator
* Facade
* Composite
* Proxy
* Bridge

### D. GoF Behavioral Pattern

Examples:

* Strategy
* Observer
* Command
* State
* Template Method
* Chain of Responsibility
* Iterator
* Mediator
* Memento
* Visitor
* Interpreter

### E. Rails/Framework Pattern

Examples:

* Active Record
* Convention over Configuration
* Service Objects
* Concerns
* Callbacks
* RESTful controller conventions

### F. Pattern-like Structure

If the code resembles a known pattern but does not satisfy enough characteristics to confidently classify it as that pattern, explicitly label it:

**Pattern-like / Partial Implementation**

Do not exaggerate pattern usage.

---

# 8. CONFIDENCE SYSTEM

Every identified pattern must receive a confidence level:

* HIGH
* MEDIUM
* LOW

Use:

### HIGH

The code clearly demonstrates the structure, participants, relationships, and intent of the pattern.

### MEDIUM

The code exhibits substantial characteristics of the pattern, but some elements are implicit or incomplete.

### LOW

There is only a superficial resemblance.

Low-confidence patterns should NOT be presented as definitive findings.

---

# 9. HUMAN-IN-THE-LOOP REQUIREMENT

The human researcher has final authority over repository selection and research direction.

You must NOT automatically choose the final repository.

You must first search for candidate repositories and provide a shortlist.

The human will then inspect the candidates and select one.

After the human selects a repository, subsequent analysis must use THAT repository as the primary evidence source.

Never silently substitute another repository.

---

# 10. CRITICAL REPOSITORY DISCOVERY TASK

Before performing the case study, you must search the web for viable Ruby on Rails Hotel Booking Applications.

Explicitly perform web searches for:

* GitHub Ruby on Rails hotel booking application
* GitHub Rails hotel reservation system
* GitHub Rails hotel booking system
* GitHub Ruby hotel reservation open source
* GitHub Rails hotel management reservation
* GitHub Rails hotel booking room reservation
* GitHub Ruby on Rails hotel management system

Search GitHub repositories and other legitimate open-source sources.

Prioritize repositories that are:

* Publicly accessible
* Open source
* Actually implemented in Ruby on Rails
* Functional or reasonably complete
* Large enough to provide meaningful architectural evidence
* Structured into multiple Rails components
* Contain meaningful domain models
* Include reservations/bookings
* Include rooms
* Include customers/users
* Include payments or payment-related logic where possible
* Include cancellation-related functionality where possible
* Include additional services or functionality that can reasonably evolve into them
* Have sufficient source code for design-pattern analysis
* Have a meaningful commit history where possible
* Have documentation/README where possible
* Can be cloned and executed or inspected
* Are not merely tutorials containing trivial CRUD operations

Do NOT select a repository simply because its name contains "hotel booking."

---

# 11. REPOSITORY QUALITY SCREENING

For each candidate repository, investigate as much as possible:

* Repository URL
* Repository name
* Author/organization
* License
* Ruby version
* Rails version
* Database
* Approximate project size
* Number of models
* Number of controllers
* Presence of services
* Presence of concerns
* Presence of policies
* Presence of background jobs
* Presence of payment integration
* Reservation functionality
* Room functionality
* Customer/user functionality
* Cancellation functionality
* Additional services
* Tests
* Documentation
* Last meaningful update
* Commit history
* Whether it appears executable
* Whether dependencies are available
* Whether it is clearly a student/tutorial project
* Whether it contains enough complexity for this case study

Where information cannot be verified, mark it as:

**Unknown / Requires Human Verification**

Never invent repository details.

---

# 12. REPOSITORY SCORING

Create a candidate comparison table.

Use a scoring system such as 0–5 for:

| Criterion                          | Score |
| ---------------------------------- | ----- |
| Rails authenticity                 | 0–5   |
| Hotel domain completeness          | 0–5   |
| Reservation complexity             | 0–5   |
| Room management                    | 0–5   |
| Customer/user management           | 0–5   |
| Payment functionality              | 0–5   |
| Cancellation functionality         | 0–5   |
| Additional services                | 0–5   |
| Architectural richness             | 0–5   |
| Pattern-analysis potential         | 0–5   |
| Evolution/refactoring potential    | 0–5   |
| Codebase size                      | 0–5   |
| Documentation                      | 0–5   |
| Tests                              | 0–5   |
| Maintainability-analysis potential | 0–5   |

Calculate a total score.

However, do NOT automatically declare the highest-scoring repository the final selection.

The human researcher must make the final choice.

---

# 13. IMPORTANT: AVOIDING A BAD CASE-STUDY REPOSITORY

Reject or strongly flag repositories that are:

* Merely a basic CRUD tutorial
* Almost entirely generated scaffolding
* Too small to demonstrate meaningful design
* Not actually Ruby on Rails
* Missing reservation functionality
* Missing meaningful domain logic
* Abandoned to the point that it cannot reasonably be inspected
* Missing a usable license
* Primarily frontend code
* A fake/demo repository with little implementation
* A repository where the hotel domain is only superficial

A smaller project can still be selected if its design provides unusually strong pattern/evolution evidence, but explain the tradeoff.

---

# 14. OUTPUT OF THIS FIRST STAGE

Your first response must ONLY establish the research plan and perform repository discovery.

Do NOT perform a full pattern analysis yet.

Return:

## A. Research methodology

Explain how the case study will be conducted.

## B. Candidate repository shortlist

Provide approximately 5–10 strong candidates if available.

For each:

* Repository
* URL
* Rails evidence
* Domain coverage
* Architecture
* Complexity
* Pattern potential
* Evolution potential
* Major risks
* Score

## C. Recommended candidates

Identify:

* Best overall candidate
* Best technically complex candidate
* Best pattern-analysis candidate
* Best evolution/refactoring candidate

But explicitly state that the human researcher makes the final selection.

## D. Human verification checklist

Give me a checklist I can manually verify before selecting the repository.

The checklist must include:

* Can I clone it?
* Can I install dependencies?
* Can I run it?
* Can I inspect the models?
* Can I inspect controllers?
* Can I inspect services?
* Does the database schema make sense?
* Is there enough domain logic?
* Is the license suitable?
* Is the repository stable enough for academic use?
* Can screenshots be captured?
* Can the code be cited/documented?
* Can the application demonstrate evolution scenarios?

## E. Next-step instruction

After presenting the candidates, STOP.

Wait for the human researcher to provide:

**"I have selected repository: [repository]"**

Only then should you proceed to source-code analysis.

---

# 15. SOURCE AUTHENTICITY RULE

Throughout the entire project:

Never claim that code exists unless it has actually been observed.

If you cannot access a file, say:

**"This requires human verification from the repository."**

Do not fabricate:

* Classes
* Methods
* File paths
* Database fields
* Relationships
* Design patterns
* Metrics
* Screenshots
* Test results
* Execution results

---

# 16. ACADEMIC INTEGRITY

The LLM is an analytical assistant.

The human researcher is responsible for:

* Repository selection
* Verification
* Running the application
* Capturing screenshots
* Confirming code behavior
* Validating metrics
* Confirming generated UML
* Reviewing pattern classifications
* Final academic conclusions

Clearly distinguish:

**Observed Evidence**

from

**LLM Interpretation**

from

**Human Verification**

This distinction must be maintained throughout the project.
