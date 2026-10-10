## A. Baseline impact summary

The immutable baseline is commit `5e15551ee646871b4bed32c982fa17da319d3ee3`.

At that commit, the relevant domain model is centered on `User`, `Room`, `Booking`, and `Setting`.

`Booking` owns the core reservation behavior: it belongs to a `User` and `Room`, validates dates and availability, calculates/holds `total_ht` and `total_ttc` through `HasPriceConcern`, marks cancellation through `cancel!`, and participates in payment and notification callbacks. The verified baseline source shows `Booking` including `HasOwnerConcern`, `HasPriceConcern`, and `Payify::HasPaymentConcern`, with `after_save :create_payment` and `after_create :notify_booking`.

Pricing is currently embedded in the booking model concern. `HasPriceConcern` computes room-price × stay duration and then applies VAT obtained through `room.user.setting.vat`.

Cancellation is currently a single operation: `Booking#cancel!` sets `canceled_at`. There is no cancellation-policy abstraction and no refund rule in application code.

`CrudConcern` remains the reusable CRUD workflow. `BookingsController`, `RoomsController`, and `SettingsController` supply controller-specific hook methods such as `base_class`, `object_class`, `strong_params`, `model_params`, and `use_slug?`.

`ApplicationPolicy` plus `BookingPolicy`, `RoomPolicy`, and `SettingPolicy` provide authorization behavior through Pundit. This is framework-supported policy polymorphism, but was not confirmed as a GoF Strategy in Part 1.

The existing model concerns are Rails `ActiveSupport::Concern` composition mechanisms:

- `HasOwnerConcern` assigns the current user before validation.
- `HasPriceConcern` supplies booking price calculation and pricing callbacks.
- `HasSettingsConcern` gives `User` a setting and creates it after user creation.

The new requirements do **not** exist in the baseline. Therefore everything below is a **proposed evolved design**, not an assertion about current repository contents.

The four requirements create two distinct classes of domain change:

1. **Optional booking add-ons** — breakfast and airport transfer.
2. **Core reservation changes/rules** — room upgrade and cancellation policy.

That distinction is important: treating all four as fields on `Booking` would increase the amount of unrelated responsibility concentrated in one model.

---

## B. Requirement-by-requirement evolution

### Breakfast

#### Domain concept

Breakfast should be modeled as an **additional service/package attached to a booking**, not as a permanent property of `Room` or `User`.

A room may have no breakfast, while a particular booking for that room may request breakfast. Therefore the business fact is associated with the **reservation instance**, not the room itself.

A reasonable evolved abstraction is:

```text
AdditionalService
    ├── BreakfastPackage
    └── AirportTransfer
```

with a booking-to-service relationship.

For example:

```text
Booking 1 ─── * BookingService * ─── 1 AdditionalService
```

This separates the definition of a service from its use on a particular booking.

#### Optionality

A booking simply has zero or more additional services.

That means:

```text
Booking A → no breakfast
Booking B → standard breakfast
Booking C → premium breakfast
```

No `breakfast = true` field is required on `Booking`.

#### Different breakfast prices

A breakfast package can expose its price through the service abstraction.

For example:

```ruby
AdditionalService
  name
  price

BreakfastPackage
  ...
```

or, when package-specific pricing rules exist:

```ruby
BreakfastPackage#price_for(booking)
```

The latter becomes important if breakfast cost depends on guest count, dates, or package tier.

#### Design pressure on the original model

Adding:

```ruby
booking.breakfast = true
booking.breakfast_price = ...
```

would push breakfast selection and pricing into `Booking`.

Adding more packages would likely produce:

```ruby
if breakfast
  ...
elsif airport_transfer
  ...
end
```

and eventually a growing collection of service-specific attributes and branches.

That is precisely the coupling the additional-service abstraction avoids.

#### Pattern conclusion

The abstraction by itself does **not** justify Decorator, Composite, or Strategy.

A collection of `AdditionalService` objects is ordinary composition unless the resulting design establishes the defining collaboration of one of those patterns.

So for breakfast alone:

**Additional-service abstraction: justified.**
**GoF pattern: not yet necessarily justified.**

---

### Airport Transfer

Airport transfer has the same high-level business relationship as breakfast:

```text
Booking
   |
   +-- optional service
```

but its attributes are different.

Possible transfer information includes:

```text
direction: pickup / dropoff / round-trip
airport
vehicle/type
scheduled time
price
```

The exact fields are an application-design choice; the baseline gives no airport-transfer requirements beyond the requested feature.

#### Should breakfast and airport transfer share an abstraction?

Yes, because they share an important business responsibility:

> They are optional, independently selectable services associated with a booking and contributing to booking cost.

They do **not** need to share all implementation details.

A useful abstraction is therefore:

```text
AdditionalService
```

rather than:

```text
BreakfastOrTransfer
```

A concrete service can carry service-specific data.

For example:

```text
AdditionalService
├── BreakfastPackage
└── AirportTransfer
```

#### Does this become Strategy?

Not merely by having:

```ruby
service.price
```

or:

```ruby
service.calculate_price
```

Different services may implement the same interface, but that alone is insufficient for a defensible Strategy claim.

Strategy becomes more defensible when the application has:

- a stable context,
- an interchangeable family of algorithms,
- a strategy abstraction,
- concrete strategies,
- and the context delegates the varying algorithm to the selected strategy.

The proposed additional-service model is primarily **polymorphic composition**, not automatically Strategy.

#### Factory?

Likewise:

```ruby
BreakfastPackage.new
AirportTransfer.new
```

does not constitute Factory.

A Factory becomes relevant only if object-creation decisions are deliberately encapsulated, for example:

```text
AdditionalServiceFactory
    ↓
creates concrete AdditionalService
```

based on a service type/request.

Nothing in the requirement itself mandates that structure.

---

### Room Upgrade

Room upgrade is materially different.

Breakfast and airport transfer are **add-ons**. A room upgrade changes the accommodation being supplied by the booking.

A booking already has:

```ruby
belongs_to :room
```

in the baseline.

An evolved design could represent an upgrade as:

```text
Booking
  original/current room
        ↓
   upgraded room
```

or as an explicit upgrade association.

The important business operations are:

1. determine whether an upgraded room is available for the same dates,
2. determine the price difference,
3. change the accommodation associated with the booking,
4. ensure the resulting booking remains valid.

#### Why not treat room upgrade as `AdditionalService`?

An upgrade is not just another independent add-on.

For example:

```text
Breakfast = extra service
Airport transfer = extra service
Room upgrade = change to the primary accommodation
```

The upgrade must interact with:

- `Room`,
- booking dates,
- room availability,
- room price,
- booking total.

Putting `RoomUpgrade` underneath `AdditionalService` would be possible mechanically, but semantically it risks hiding an important distinction: an upgrade modifies the core resource relationship instead of simply adding a peripheral service.

#### Pricing

The price difference can be represented conceptually as:

```text
upgrade price
= upgraded room price for stay
- original room price for stay
```

This should not be scattered into controllers.

A domain operation such as:

```ruby
Booking#upgrade_to(room)
```

or, preferably for a richer workflow:

```ruby
RoomUpgradeService#apply(...)
```

can encapsulate the transition.

#### Availability

This is where upgrade behavior differs most strongly from breakfast and transfer.

The application must ensure the new room is available for the same dates.

So the upgrade collaboration naturally involves:

```text
Booking
  → Room
  → availability rules
  → pricing
```

rather than simply:

```text
Booking
  → AdditionalService
```

#### Pattern conclusion

Room upgrade itself does not automatically establish State, Strategy, Command, or Decorator.

A dedicated `RoomUpgrade` domain concept is justified because its business responsibility differs from optional services.

A separate upgrade service/use-case object is also reasonable if the workflow becomes sufficiently complex, but that alone is not a GoF pattern claim.

---

### Cancellation Policy

This is the requirement that most strongly justifies a new GoF behavioral pattern.

The baseline has only:

```ruby
Booking#cancel!
```

which writes:

```text
canceled_at = current time
```

The evolved requirements introduce varying cancellation algorithms:

```text
free before deadline
partial refund
no refund
future additional rules
```

Now cancellation behavior varies independently of the booking itself.

Embedding everything in `Booking` would quickly produce logic such as:

```ruby
if policy_type == ...
elsif ...
elsif ...
```

and make `Booking` responsible for both reservation data and a growing family of cancellation algorithms.

That is strong design pressure for Strategy.

### Proposed cancellation design

Use:

```text
CancellationPolicy
```

as the stable abstraction.

Concrete policies might include:

```text
FlexibleCancellationPolicy
PartialRefundCancellationPolicy
NoRefundCancellationPolicy
```

The exact policy set is proposed; it is not present in the baseline.

The policy could define something such as:

```ruby
refund_amount(booking, canceled_at)
```

and optionally:

```ruby
cancellable?(booking, canceled_at)
```

The context can be:

```text
Booking
```

if cancellation remains simple, or a dedicated:

```text
CancellationService
```

if the operation additionally coordinates payment/refunds.

The latter is preferable once payment interaction becomes substantial.

### Strategy role mapping

| Strategy role                    | Evolved application element                                                                               |
| -------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Context                          | `CancellationService`                                                                                     |
| Strategy abstraction             | `CancellationPolicy`                                                                                      |
| Concrete Strategy                | `FlexibleCancellationPolicy`                                                                              |
| Concrete Strategy                | `PartialRefundCancellationPolicy`                                                                         |
| Concrete Strategy                | `NoRefundCancellationPolicy`                                                                              |
| Context → Strategy collaboration | `CancellationService` delegates cancellation/refund-rule calculation to the selected `CancellationPolicy` |
| Context dependency               | `Booking`, payment/refund mechanism                                                                       |

### Why this is genuine Strategy

The defining variation is the **cancellation algorithm**.

The context performs the same business operation:

```text
cancel booking
```

but delegates the variable rule:

```text
how much refund / whether cancellation is free
```

to an interchangeable policy object.

Adding another cancellation rule then means introducing another concrete policy rather than expanding a central conditional.

That is a substantially stronger Strategy collaboration than the baseline policy hierarchy investigated in Part 1.

### Payment interaction

The application already uses Payify and exposes:

```ruby
Booking#payment_pending?
Booking#paid?
amount_to_pay
```

and the controller calls:

```ruby
@object.payment.stripe_init_intent
```

The baseline does not expose Payify's internal refund implementation.

Therefore Part 2 should **not** claim a concrete Stripe refund design.

The proposed evolved flow is:

```text
CancellationService
    ↓
CancellationPolicy
    ↓
refund amount
    ↓
payment/refund boundary
    ↓
Booking#cancel!
```

The exact Payify API for refunds must be verified before Part 3 implementation.

---

## C. Design pressure table

| Requirement         | Original responsibility                                            | New responsibility                                                           | Problem if added directly                                                        | Proposed design response                                                                     |
| ------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Breakfast           | `Booking` calculates total using `HasPriceConcern`                 | Select breakfast package and add its price                                   | `Booking` accumulates service-specific fields/conditionals                       | Introduce `AdditionalService` + `BreakfastPackage`; associate selected services with booking |
| Airport Transfer    | `Booking` represents room/date reservation                         | Capture transfer choice/details and price                                    | More service-specific attributes and branches inside `Booking`                   | Reuse `AdditionalService` abstraction with `AirportTransfer`                                 |
| Room Upgrade        | `Booking` belongs to one `Room`; `HasPriceConcern` uses room price | Check upgraded-room availability, calculate difference, change accommodation | `Booking` must handle resource substitution, availability, and new pricing logic | Model upgrade separately from add-ons; encapsulate upgrade workflow                          |
| Cancellation Policy | `Booking#cancel!` simply sets `canceled_at`                        | Select and execute variable cancellation/refund rule                         | Growing conditional tree in `Booking`; coupling to payment/refund decisions      | Introduce `CancellationPolicy` Strategy and preferably `CancellationService` as context      |

The strongest design pressure is not merely “the class gets bigger.” It is that **multiple independent axes of variation start entering `Booking`**:

- optional service pricing,
- service-specific data,
- accommodation replacement,
- cancellation algorithms,
- payment/refund consequences.

Separating those responsibilities keeps each variation in a more localized place.

---

## D. Proposed evolved architecture

### Core domain

```text
User
 ├── has_many Rooms
 ├── has_many Bookings
 └── has_one Setting

Room
 └── has_many Bookings

Booking
 ├── belongs_to User
 ├── belongs_to Room
 ├── has_many BookingServices
 └── cancellation handled through CancellationService

Setting
 └── belongs_to User
```

### New service model

```text
AdditionalService
 ├── BreakfastPackage
 └── AirportTransfer

BookingService
 ├── belongs_to Booking
 └── belongs_to AdditionalService
```

#### `AdditionalService`

**Responsibility:** Define an optional bookable service/package and its pricing information.

Potential methods:

```text
price_for(booking)
name
```

A common base model or abstract domain class is enough; no artificial interface is necessary.

#### `BreakfastPackage`

**Responsibility:** Represent a breakfast offering/package.

Potential data:

```text
name
price
```

Potential behavior:

```text
price_for(booking)
```

#### `AirportTransfer`

**Responsibility:** Represent an airport transport option and its service-specific data.

Potential data:

```text
direction
airport
price
```

### `BookingService`

**Responsibility:** Represent the selection of an `AdditionalService` for a particular booking.

This association is useful because a service definition and a booking's selected service are different domain facts.

For example:

```text
BreakfastPackage
  Standard Breakfast
  ₹X

Booking #123
  selected service
      ↓
BookingService
      ↓
Standard Breakfast
```

This also provides a natural place for booking-specific captured prices if required later, preventing historical booking totals from depending entirely on today's service catalogue price.

### `RoomUpgrade`

**Responsibility:** Represent the transition from the originally booked room to another room.

Potential methods:

```text
available?
price_difference
apply
```

Whether this should become a persisted entity or remain a service/use-case object depends on whether the system needs historical upgrade records. That is a Part 3 implementation decision informed by the exact requirements.

### `CancellationPolicy`

**Responsibility:** Encapsulate a cancellation/refund rule.

Potential interface:

```text
cancellable?(booking, at:)
refund_amount(booking, at:)
```

Concrete classes implement different rules.

### `CancellationService`

**Responsibility:** Orchestrate the cancellation use case.

Potential workflow:

```text
load booking
→ select policy
→ ask policy for cancellation/refund outcome
→ invoke payment/refund mechanism when applicable
→ mark booking cancelled
```

This prevents `Booking` from becoming both:

- reservation state holder,
- cancellation-rule engine,
- payment/refund coordinator.

### Existing classes that can largely remain unchanged

`User` and `Setting` need no direct conceptual change for these requirements.

`Room` remains the source of room information and room pricing/availability.

`CrudConcern` remains the shared CRUD mechanism.

`ApplicationPolicy` and resource policies can remain responsible for authorization. New policies may be introduced only if the new operations require authorization rules.

`HasOwnerConcern` can remain unchanged.

`HasSettingsConcern` can remain unchanged.

`HasPriceConcern` may need to evolve because the booking total is no longer simply the room price × stay duration.

That is a significant point: the existing concern currently computes:

```text
total_ht = room.day_price × stay length
total_ttc = total_ht × (1 + vat)
```

Once optional services and upgrades affect the booking total, that algorithm needs a clear extension point rather than arbitrary additions to `HasPriceConcern`.

---

## E. Confirmed evolved patterns

### Pattern

**Strategy**

### Category

**GoF Behavioral**

### Intent

Encapsulate interchangeable cancellation algorithms so that the cancellation workflow does not contain a growing collection of policy-specific conditionals.

### Participants

Proposed evolved participants:

- `CancellationService`
- `CancellationPolicy`
- `FlexibleCancellationPolicy`
- `PartialRefundCancellationPolicy`
- `NoRefundCancellationPolicy`
- `Booking`
- payment/refund boundary

### Exact role mapping

| Strategy role           | Evolved application element       |
| ----------------------- | --------------------------------- |
| Context                 | `CancellationService`             |
| Strategy                | `CancellationPolicy`              |
| Concrete Strategy       | `FlexibleCancellationPolicy`      |
| Concrete Strategy       | `PartialRefundCancellationPolicy` |
| Concrete Strategy       | `NoRefundCancellationPolicy`      |
| Context's domain object | `Booking`                         |
| External collaborator   | payment/refund mechanism          |

### Collaborations / interactions

Proposed cancellation flow:

```text
Controller
    ↓
CancellationService
    ↓
CancellationPolicy
    ↓
refund/cancellation decision
    ↓
Payment/Refund boundary
    ↓
Booking cancellation state
```

The crucial variation is:

```text
CancellationPolicy
    ├── free cancellation
    ├── partial refund
    └── no refund
```

while the use case remains the same:

```text
cancel this booking
```

### Why it qualifies

This proposed architecture introduces an actual family of interchangeable algorithms.

The context need not know the details of each cancellation rule. It depends on the policy abstraction and delegates the variable calculation to the selected concrete policy.

Adding a new cancellation rule therefore means adding another concrete implementation rather than changing the cancellation orchestration itself.

That is the defining Strategy collaboration.

### Why alternative classifications were rejected

**Template Method:** rejected for cancellation because the variation is better represented by interchangeable policy objects rather than a fixed superclass algorithm plus subclass hooks.

**State:** rejected because the requirement concerns differing cancellation **rules**, not different objects representing booking states.

**Command:** rejected because a service call such as `cancel` does not become Command unless a command object encapsulates the request independently.

**Observer:** rejected because the requirement does not need subscriber registration/notification.

**Factory:** not inherently required. A factory may eventually be useful to select/instantiate the correct cancellation policy, but object creation alone does not establish Factory.

**Decorator:** rejected because the policy is not wrapping another policy object to augment behavior.

### Status

**Confirmed for the proposed evolved design; proposed until Part 3 implementation exists.**

This distinction is essential: **Strategy is justified by the Part 2 design, but there is no evolved source code yet, so this is a proposed/target pattern, not a claim about the current repository.**

---

### Existing Template Method

**Pattern:** Template Method
**Category:** GoF Behavioral
**Instance:** `CrudConcern`

**Status:** Confirmed and retained from Part 1.

The original collaboration is unchanged conceptually:

```text
CrudConcern
    ↓
shared CRUD algorithm
    ↓
controller-specific hooks
```

The new features do not require replacing it.

---

### Additional-service abstraction

This is **not classified as a GoF pattern** at this stage.

It is a domain abstraction/composition design that creates:

```text
Booking
  → BookingService
      → AdditionalService
          ├── BreakfastPackage
          └── AirportTransfer
```

It may later support other patterns, but the abstraction itself does not prove one.

---

### GRASP assessment

**Information Expert — applicable as a responsibility-assignment principle.**

Examples:

- `Room` knows room-specific data and pricing.
- `Booking` knows its booking dates and room relationship.
- `CancellationPolicy` knows cancellation-rule calculations.
- `AdditionalService` knows service-specific pricing.

This supports high cohesion and localized knowledge, but it is not counted as an additional GoF pattern.

**Protected Variations — strongly applicable to the evolved design.**

The most important protected variation is cancellation rules:

```text
CancellationService
       ↓
CancellationPolicy abstraction
```

The changing rule is protected behind a stable abstraction.

This is best treated as a GRASP design principle supporting the Strategy implementation, rather than as a separate GoF pattern instance.

---

## F. Uncertain candidates

| Candidate                                        | Evidence                                                                                   | Missing evidence                                                                                                | Reason uncertain                                                                                   |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Factory Method for cancellation-policy selection | Multiple concrete cancellation policies would need to be instantiated/selected             | No factory is mandated; policy construction mechanism has not been designed                                     | Could be added in Part 3, but currently unnecessary to prove Strategy                              |
| Factory for additional services                  | Breakfast and airport transfer have common abstraction and may be selected from user input | No dedicated creation abstraction is required                                                                   | Simple polymorphic construction may be sufficient                                                  |
| Builder for booking                              | Booking may eventually require room + services + upgrade + policy                          | No construction sequence with many mandatory/optional steps has yet been established                            | A Builder may be useful later, but not justified by the requirements alone                         |
| Decorator for service pricing                    | Multiple optional services affect total price                                              | Proposed model uses composition/association, not wrapper objects                                                | Could become relevant only if each service wraps an existing price component and forwards behavior |
| Composite for additional services                | Booking contains multiple services                                                         | Services are peers in a collection, not a recursive tree of components with uniform child semantics             | Collection ≠ Composite                                                                             |
| Strategy for service pricing                     | Different services may calculate price differently                                         | The requirement does not yet demand interchangeable pricing algorithms selected independently from service type | Common method/interface is not enough                                                              |
| State for booking cancellation                   | Booking transitions from active to cancelled                                               | No separate state objects or behavior-by-state hierarchy is required                                            | Current requirement focuses on rule variation rather than state representation                     |
| Command for room upgrade                         | Upgrade is a distinct use case                                                             | No command object or deferred execution requirement                                                             | A service/use-case object is enough                                                                |
| Observer for service changes                     | Price totals may react to service selection                                                | No application-defined subscriptions/events                                                                     | Callback/event mechanisms alone would not prove Observer                                           |
| Adapter around Payify refunds                    | Cancellation may need refund integration                                                   | Exact Payify refund interface is not visible in baseline                                                        | Requires inspection of the actual dependency/API before deciding whether translation is needed     |

---

## G. Rejected candidates

| Candidate                                  | Why it may appear relevant                          | Why it does not qualify                                                                                                                                  |
| ------------------------------------------ | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Decorator for breakfast + airport transfer | Optional services “decorate” a booking conceptually | Conceptual augmentation is not GoF Decorator; the proposed design uses booking-service associations, not wrapper objects implementing the same interface |
| Composite for additional services          | A booking can contain many services                 | There is no recursive whole-part hierarchy where individual services and collections share the same component interface                                  |
| Factory Method for `Booking` creation      | Booking construction becomes more complicated       | Complexity alone does not create Factory Method; no creator/product hierarchy or creation-hook collaboration is required                                 |
| Abstract Factory                           | Several domain objects may be created together      | No related product families or family-level factory abstraction are needed                                                                               |
| Builder                                    | A booking may have many optional components         | Optional fields alone do not justify Builder                                                                                                             |
| Observer                                   | Booking lifecycle currently has callbacks           | Rails callbacks are framework lifecycle behavior and do not provide an application-defined observer/subscriber collaboration                             |
| State                                      | Cancellation changes booking status                 | A boolean/timestamp status is not a State-pattern object hierarchy                                                                                       |
| Command                                    | Cancellation and upgrade are actions                | A method/service invocation is not a Command object                                                                                                      |
| Adapter                                    | Payment integration crosses a third-party boundary  | A boundary exists, but the application has not demonstrated incompatible interfaces being translated by an adapter                                       |
| Facade                                     | A service layer could hide payment complexity       | Merely hiding calls behind a service object is insufficient to establish a Facade over a subsystem                                                       |
| Decorator via Rails concerns               | Existing concerns compose model behavior            | `ActiveSupport::Concern` is direct module composition, not object wrapping                                                                               |

---

## H. Before vs After comparison

| Aspect                 | Original Design                                                                                           | Evolved Design                                                                                                                    |
| ---------------------- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Booking responsibility | Reservation data, availability validation, booking pricing, cancellation timestamp, payment-related hooks | Reservation core remains, while optional services, upgrades, and cancellation rules are moved into dedicated collaborators        |
| Pricing                | `HasPriceConcern` computes room-price-based total + VAT                                                   | Base room price plus selected services and upgrade difference; pricing responsibilities can be localized by domain object/service |
| Optional services      | None                                                                                                      | `AdditionalService` with concrete `BreakfastPackage` and `AirportTransfer`, associated through booking-specific selections        |
| Room upgrade           | Not supported                                                                                             | Separate upgrade responsibility interacting with room availability and pricing                                                    |
| Cancellation           | `Booking#cancel!` only sets `canceled_at`                                                                 | `CancellationService` coordinates cancellation and delegates rule variation to `CancellationPolicy`                               |
| Extensibility          | New behavior tends to enter `Booking`/concerns                                                            | New service types and cancellation rules can be introduced behind existing abstractions                                           |
| Coupling               | Booking already couples to pricing, payment callbacks, notification, room and user                        | Varying optional-service and cancellation behavior becomes more localized                                                         |
| Confirmed patterns     | Template Method in `CrudConcern`                                                                          | Existing Template Method retained; Strategy introduced for cancellation policy in the proposed evolved design                     |

The key architectural change is not the number of classes. It is the movement of **independent variation out of `Booking`**.

---

## I. Evolution scenarios

### Scenario 1 — Add a new breakfast package

#### Without the proposed abstraction

A direct implementation could add more fields and conditionals to `Booking`:

```text
Booking
 ├── breakfast_selected
 ├── breakfast_type
 ├── breakfast_price
 └── conditional pricing logic
```

Adding another package then modifies the same model and pricing logic.

#### With the proposed abstraction

```text
BreakfastPackage
      ↓
BookingService
      ↓
Booking
```

Adding:

```text
Premium Breakfast
```

primarily means adding another service definition/configuration or concrete package representation.

The booking core does not need breakfast-specific branching.

---

### Scenario 2 — Add a new airport transfer type

#### Without the proposed abstraction

The booking model/controller would acquire more transfer-specific fields and conditional calculations:

```text
pickup
dropoff
airport
vehicle
price
```

and changes would accumulate around booking creation and pricing.

#### With the proposed abstraction

A new transfer variant remains inside the airport-transfer domain:

```text
AirportTransfer
   ├── Pickup
   ├── Dropoff
   └── RoundTrip
```

The `Booking` collaboration remains: