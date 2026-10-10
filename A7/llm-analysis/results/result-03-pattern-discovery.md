## A. CONFIRMED PATTERNS

| Pattern                                    | Category                                  | Instance                                                   | Participants                                                                                                                                                                              | Source locations                                                                                                                                                                                           | Evidence                                                                                                                                                                                                                                                                                  |
| ------------------------------------------ | ----------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Template Method                            | GoF Behavioral                            | `CrudConcern` shared CRUD workflow with controller hooks   | `CrudConcern`; `BookingsController`; `RoomsController`; `SettingsController`; hook methods `base_class`, `object_class`, `strong_params`, `model_params`, `use_slug?`, `redirect_to_show` | `app/controllers/concerns/crud_concern.rb:12–55, 84–105`; `app/controllers/bookings_controller.rb:16–39`; `app/controllers/rooms_controller.rb:7–38`; `app/controllers/settings_controller.rb:5–35`        | The common CRUD algorithms are implemented once, while participating controllers provide overridable methods that the algorithm invokes.                                                                                                                                                  |
| Strategy                                   | GoF Behavioral                            | Policy-specific authorization behavior selected by Pundit  | `ApplicationPolicy`; `BookingPolicy`; `RoomPolicy`; `SettingPolicy`; `ApplicationController` via `Pundit::Authorization`                                                                  | `app/policies/application_policy.rb:3–36`; `app/policies/booking_policy.rb:1–7`; `app/policies/room_policy.rb:1–5`; `app/policies/setting_policy.rb:1–5`; `app/controllers/application_controller.rb:1–10` | **Not confirmed.** The source has interchangeable policy objects and a common interface, but the selection mechanism is supplied by Pundit and the application does not define the Strategy abstraction itself. Therefore this candidate is **not promoted** as a confirmed GoF Strategy. |
| Template Method                            | GoF Behavioral                            | `ApplicationPolicy` inheritance hierarchy                  | `ApplicationPolicy`; `BookingPolicy`; `RoomPolicy`; `SettingPolicy`                                                                                                                       | `app/policies/application_policy.rb:7–28`; resource policy files                                                                                                                                           | **Not confirmed separately.** Although subclasses override `update?`, there is no superclass algorithm that invokes subclass-defined hooks in the Template Method sense.                                                                                                                  |
| Composite reuse via ActiveSupport concerns | Rails-specific idiom                      | `HasOwnerConcern`, `HasPriceConcern`, `HasSettingsConcern` | Concern modules; including models `Booking`, `Room`, `User`                                                                                                                               | `app/models/booking.rb:1–7`; `app/models/room.rb:1–2`; `app/models/user.rb:1–2`; concern files                                                                                                             | This is a genuine Rails composition/reuse mechanism, but not a defensible GoF Decorator/Composite/etc. instance.                                                                                                                                                                          |
| Active Record                              | Architectural / Rails framework mechanism | Domain persistence objects                                 | `ApplicationRecord`; `Booking`; `Room`; `User`; `Setting`                                                                                                                                 | model files; schema                                                                                                                                                                                        | Framework-provided architectural mechanism, not a new application-level GoF pattern claim.                                                                                                                                                                                                |

### Detailed confirmed record 1

**Pattern:** Template Method
**Category:** GoF Behavioral
**Instance:** `CrudConcern` shared CRUD workflow for resource controllers

**Intent:**
Provide one reusable CRUD algorithm while allowing each participating controller to supply resource-specific operations and configuration.

**Participants:**

- `CrudConcern`
- `BookingsController`
- `RoomsController`
- `SettingsController`

**Role mapping:**

| Textbook role              | Actual source symbol           |
| -------------------------- | ------------------------------ |
| Abstract algorithm holder  | `CrudConcern`                  |
| Template operation         | `CrudConcern#create`           |
| Template operation         | `CrudConcern#update`           |
| Template operation         | `CrudConcern#index`            |
| Template operation         | `CrudConcern#show`             |
| Template operation         | `CrudConcern#destroy`          |
| Hook / primitive operation | `CrudConcern#base_class`       |
| Hook / primitive operation | `CrudConcern#object_class`     |
| Hook / primitive operation | `CrudConcern#strong_params`    |
| Hook / primitive operation | `CrudConcern#model_params`     |
| Hook / primitive operation | `CrudConcern#use_slug?`        |
| Hook                       | `CrudConcern#redirect_to_show` |
| Concrete participant       | `BookingsController`           |
| Concrete participant       | `RoomsController`              |
| Concrete participant       | `SettingsController`           |

**Interactions:**

`CrudConcern#create` performs a fixed sequence:

`authorize object_class`
→ `object_class.new(form_values)`
→ `valid?`
→ `save!`
→ `redirect_to_show(@object)`

The algorithm does not know whether the controller represents a booking, room, or setting. It invokes methods such as `object_class`, `form_values`, and `redirect_to_show`, whose effective behavior is supplied by the including controller.

For example:

`BookingsController#base_class` → `Booking`
`RoomsController#base_class` → `Room`
`SettingsController#base_class` → `Setting`

Likewise, `BookingsController#use_slug?` and `SettingsController#use_slug?` return `false`, while `CrudConcern` provides the default `true`.

**Source locations:**

- `app/controllers/concerns/crud_concern.rb:12–17` — `index`
- `app/controllers/concerns/crud_concern.rb:19–23` — `show`
- `app/controllers/concerns/crud_concern.rb:25–29` — `new`
- `app/controllers/concerns/crud_concern.rb:31–43` — `create`
- `app/controllers/concerns/crud_concern.rb:45–59` — `edit` / `update`
- `app/controllers/concerns/crud_concern.rb:61–67` — `destroy`
- `app/controllers/concerns/crud_concern.rb:69–82` — shared redirect/template support
- `app/controllers/concerns/crud_concern.rb:84–105` — configurable hook methods and object lookup
- `app/controllers/bookings_controller.rb:16–39`
- `app/controllers/rooms_controller.rb:7–38`
- `app/controllers/settings_controller.rb:5–35`

**Evidence:**

- All three controllers explicitly `include ::CrudConcern`.
- The concern contains the complete CRUD control flow.
- The concern intentionally leaves resource-specific methods such as `base_class` and `object_class` to participating controllers.
- The controllers provide concrete implementations of those methods.
- `CrudConcern` itself contains `raise NotImplementedError` for `base_class` and `object_class`, which is strong evidence that these are extension points rather than accidental method duplication.

**Why it qualifies:**
This is the strongest application-level GoF collaboration in the repository. The defining feature is not merely “shared code” or “inheritance”; it is the presence of a reusable algorithm whose steps depend on overridable operations supplied by concrete participants. The same CRUD algorithm executes with different resource-specific hooks.

One nuance should be stated in the report: this is implemented through **Ruby module inclusion and method overriding**, rather than a classical abstract superclass hierarchy. The behavioral structure nevertheless matches the Template Method idea.

**Verification status:**
**Confirmed at commit `5e15551ee646871b4bed32c982fa17da319d3ee3`.**

---

### Detailed confirmed record 2

There is **no second GoF pattern I would safely promote to confirmed status from the inspected baseline**.

The remaining candidates are either Rails mechanisms, ordinary code reuse, or plausible but incomplete analogies. That distinction is important for a defensible Part 1.

---

## B. UNCERTAIN CANDIDATES

| Candidate                             | Evidence suggesting it                                                                                                      | Missing evidence                                                                                                                            | Reason uncertain                                                                                                                                |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Strategy                              | `ApplicationPolicy` defines a common policy API and concrete policy classes implement resource-specific authorization rules | Application code does not define or select a family of interchangeable algorithms; Pundit performs policy lookup/selection                  | Could be described conceptually as strategy-like polymorphism, but the repository does not itself establish the full GoF Strategy collaboration |
| Strategy via `CrudConcern` hooks      | Controllers supply different implementations of `base_class`, `object_class`, `use_slug?`, etc.                             | These are configuration/extension hooks for one algorithm, not independently substitutable algorithms encapsulated behind a strategy object | More accurately explained as Template Method                                                                                                    |
| Policy inheritance as Template Method | Subclasses call `super` from `update?`                                                                                      | No superclass algorithm invokes a collection of subclass hooks; `ApplicationPolicy#update?` is just a reusable predicate                    | Ordinary inheritance/polymorphic override rather than Template Method                                                                           |
| Observer / Event Notification         | `Booking` has `after_create :notify_booking`, and `notify_booking` calls `Integromat::Webhook#trigger`                      | No application-defined event subject, observer registration, or observer collection is present                                              | The callback is Rails lifecycle behavior followed by a direct integration call                                                                  |
| Observer                              | `after_save :create_payment` plus external payment object                                                                   | No observer interface or subject/observer registration is visible in application source                                                     | `after_save` is an Active Record lifecycle callback, not sufficient evidence for GoF Observer                                                   |
| Adapter                               | `Booking#notify_booking` uses `Integromat::Webhook` rather than raw HTTP code                                               | No application-defined target interface or alternative incompatible adaptee is shown                                                        | The repository demonstrates library usage, not an Adapter collaboration                                                                         |
| Facade                                | `Booking#notify_booking` makes a small call into `Integromat::Webhook`                                                      | No subsystem complexity is encapsulated behind an application-defined facade                                                                | It is a direct library call                                                                                                                     |
| Decorator                             | Models gain behavior through `include` of concerns                                                                          | No wrapping object or same-interface object composition exists                                                                              | ActiveSupport concerns are mixins, not GoF Decorators                                                                                           |
| Decorator                             | `Payify::HasPaymentConcern` adds payment behavior to `Booking`                                                              | No wrapper object is shown; payment behavior is injected by a third-party module                                                            | Cannot establish Decorator roles from the available source                                                                                      |
| Factory Method                        | `base_class` returns `Booking`, `Room`, or `Setting`                                                                        | Returned value is a class constant used by the CRUD mechanism; no product hierarchy/factory-product collaboration exists                    | Naming/function resembles a factory hook, but defining factory collaboration is absent                                                          |
| Command                               | Controller actions such as `cancel` invoke `cancel!`                                                                        | No command object encapsulating a request exists                                                                                            | Direct method call, not Command                                                                                                                 |
| State                                 | `canceled?`, `payment_pending?`, `paid?` expose status-dependent behavior                                                   | No state objects or polymorphic state transitions are present                                                                               | State is represented by fields/payment status predicates                                                                                        |
| GRASP Controller                      | `BookingsController` coordinates request handling and delegates to model/policy                                             | This is largely normal MVC/Rails controller behavior                                                                                        | May be discussed as GRASP Controller at an architectural level, but should not be confused with a distinctive application pattern instance      |
| GRASP Polymorphism                    | Policy subclasses override `update?`                                                                                        | Only simple inheritance overrides are present                                                                                               | Evidence is weaker than for the CRUD Template Method                                                                                            |
| GRASP Information Expert              | `Booking#dates_are_available`, `Booking#cancel!`, `Room#booked_dates` operate on domain data                                | This is a responsibility-assignment principle rather than a structural pattern                                                              | Safe only as a responsibility principle, not as a named GoF pattern                                                                             |

---

## C. REJECTED CANDIDATES

| Candidate                   | Observed mechanism                                      | Why it does not qualify                                                                                                                                                                    |
| --------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GoF Observer                | `Booking#notify_booking` registered with `after_create` | `after_create` is Active Record lifecycle callback machinery. The application does not define Subject/Observer participants, registration, or notification dispatch to multiple observers. |
| GoF Observer for payment    | `after_save :create_payment`                            | A callback invokes behavior during persistence; there is no observer collection or event-subscription collaboration in application code.                                                   |
| GoF Adapter                 | `Integromat::Webhook.new(:booking).trigger(...)`        | The application calls the third-party API object directly. No target interface + adapter wrapping an incompatible adaptee is visible.                                                      |
| GoF Facade                  | `Booking#notify_booking`                                | This method does not expose a meaningful simplified interface over a multi-component subsystem; it is essentially one integration call with a guard and payload construction.              |
| GoF Decorator               | `include HasOwnerConcern`, `include HasPriceConcern`    | Ruby module inclusion adds methods directly to the class; there is no wrapper object forwarding to a wrapped component.                                                                    |
| GoF Decorator via Payify    | `include Payify::HasPaymentConcern`                     | Same issue, plus the implementation is outside the repository. The source proves composition through a dependency, not the Decorator collaboration.                                        |
| GoF Composite               | `Room#has_many :bookings`                               | An Active Record association is not a recursive uniform component hierarchy.                                                                                                               |
| GoF Factory Method          | `CrudConcern#base_class`                                | It returns a model class used by the CRUD workflow, but there is no product-family creation hierarchy or factory-vs-concrete-product relationship.                                         |
| GoF Abstract Factory        | `base_class` values for Booking/Room/Setting            | No related product families are created by a factory abstraction.                                                                                                                          |
| GoF Command                 | `BookingsController#cancel`                             | The request is handled directly; there is no command object representing the action.                                                                                                       |
| GoF State                   | `Booking#canceled?`, `payment_pending?`, `paid?`        | State is encoded in attributes/payment status and predicates, without separate state objects or transition polymorphism.                                                                   |
| GoF Memento                 | Booking persistence / Active Record                     | Database persistence is not an application-implemented snapshot/restore collaboration.                                                                                                     |
| GoF Chain of Responsibility | Rails `before_action` / `after_*` callbacks             | Callback chains are framework execution infrastructure, not an explicitly modeled chain of handler objects in this application.                                                            |
| GoF Prototype               | `object_class.new(...)`                                 | Creating a fresh Active Record object is ordinary object construction, not cloning an existing prototype.                                                                                  |
| GoF Singleton               | `User.current` / `CurrentScope.user_id`                 | A class method accessing current request scope is not a Singleton object implementation.                                                                                                   |
| Inheritance as pattern      | `BookingPolicy < ApplicationPolicy` etc.                | Inheritance by itself does not establish a named design pattern.                                                                                                                           |
| Concerns as Decorator       | ActiveSupport::Concern                                  | Concerns are modular code composition/reuse. Calling them Decorators would misrepresent the actual structure.                                                                              |
| Callbacks as Observer       | Active Record callbacks generally                       | Lifecycle hooks alone do not satisfy Observer's subject/subscriber collaboration.                                                                                                          |
| Payify as Adapter           | `Payify::HasPaymentConcern`                             | The application source does not expose the third-party internal classes or a translated target interface.                                                                                  |
| Payify as Facade            | `payment.stripe_init_intent`                            | The source only shows an API call into a third-party payment object. The subsystem hidden behind it is not defined here.                                                                   |

---

## D. FINAL BASELINE INVENTORY

**Total confirmed pattern types:** **1**

**Total confirmed pattern instances:** **1**

**Confirmed pattern type:**

- GoF Behavioral — **Template Method**

**Confirmed instance:**

- **`CrudConcern` shared CRUD workflow with resource-specific controller hooks**

**Concrete participant classes/modules/functions:**

- `CrudConcern`
- `CrudConcern#index`
- `CrudConcern#show`
- `CrudConcern#new`
- `CrudConcern#create`
- `CrudConcern#edit`
- `CrudConcern#update`
- `CrudConcern#destroy`
- `CrudConcern#base_class`
- `CrudConcern#object_class`
- `CrudConcern#strong_params`
- `CrudConcern#model_params`
- `CrudConcern#use_slug?`
- `CrudConcern#redirect_to_show`
- `BookingsController`
- `BookingsController#base_class`
- `BookingsController#object_class`
- `BookingsController#strong_params`
- `BookingsController#model_params`
- `BookingsController#use_slug?`
- `RoomsController`
- `RoomsController#base_class`
- `RoomsController#object_class`
- `RoomsController#strong_params`
- `RoomsController#model_params`
- `SettingsController`
- `SettingsController#base_class`
- `SettingsController#object_class`
- `SettingsController#strong_params`
- `SettingsController#model_params`
- `SettingsController#use_slug?`
- `SettingsController#set_object`
- `SettingsController#redirect_to_show`

**Unique participant symbols:** **33**

**Uncertain candidate count:** **13**

**Rejected candidate count:** **21**

The counts above treat each clearly distinguishable candidate listed in sections B and C as one candidate, while the confirmed inventory contains one pattern instance.

---

## E. PART 1 EVIDENCE TABLE

| source_version | pattern_name    | pattern_type   | instance_name                      | participant_roles                                                                                                                                                                                                                                                             | source_locations                                                                                                                                                                            | intent_and_evidence                                                                                                                                                                                                                                                  |
| -------------- | --------------- | -------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| original       | Template Method | GoF Behavioral | `CrudConcern` shared CRUD workflow | Abstract/shared algorithm → `CrudConcern#index/new/create/edit/update/destroy`; hooks → `base_class`, `object_class`, `strong_params`, `model_params`, `use_slug?`, `redirect_to_show`; concrete participants → `BookingsController`, `RoomsController`, `SettingsController` | `app/controllers/concerns/crud_concern.rb:12–105`; `app/controllers/bookings_controller.rb:1–39`; `app/controllers/rooms_controller.rb:1–38`; `app/controllers/settings_controller.rb:1–35` | The concern supplies fixed CRUD algorithms while each controller supplies resource-specific hook implementations. `base_class` and `object_class` are explicitly abstracted, including `raise NotImplementedError`, which demonstrates intentional extension points. |

---

## F. RESEARCH CONCLUSION

1. **Patterns safe to use in the final case study**

The safest formal pattern claim from the baseline is:

**GoF Template Method — implemented through `CrudConcern` and controller hook methods.**

This is supported by an actual reusable algorithm plus explicit extension points and multiple concrete participants.

The repository also contains useful **Rails-specific mechanisms** that can be discussed separately:

- ActiveSupport concerns for modular composition
- Active Record domain/persistence architecture
- Pundit policy-based authorization
- Active Record lifecycle callbacks
- mounted Payify engine
- Active Storage associations

These should be described as framework mechanisms or Rails idioms, not inflated into GoF patterns.

2. **Candidates that should NOT be claimed**

Do not claim the following as confirmed patterns from this baseline:

**Observer**, **Adapter**, **Facade**, **Decorator**, **Factory Method**, **Abstract Factory**, **Command**, or **State**.

The evidence does not demonstrate their defining collaborations.

Also avoid claiming **Strategy** solely from the policy hierarchy. The policy classes are certainly polymorphic, but the repository delegates policy lookup/selection to Pundit and does not itself expose the complete Strategy collaboration strongly enough for a professor-proof GoF claim.

3. **Most important files for the next verification step**

The highest-value files are:

`app/controllers/concerns/crud_concern.rb`
`app/controllers/bookings_controller.rb`
`app/controllers/rooms_controller.rb`
`app/controllers/settings_controller.rb`

These establish the confirmed pattern.

For supporting architectural/framework analysis:

`app/models/booking.rb`
`app/models/concerns/has_owner_concern.rb`
`app/models/concerns/has_price_concern.rb`
`app/models/concerns/has_settings_concern.rb`
`app/policies/application_policy.rb`
`app/policies/booking_policy.rb`
`app/policies/room_policy.rb`
`app/policies/setting_policy.rb`
`config/routes.rb`
`config/initializers/payify.rb`
`config/initializers/integromat.rb`

The strongest Part 1 conclusion is therefore **not a large catalog of patterns**. At the pinned original commit, there is one clearly defensible GoF pattern: **Template Method in `CrudConcern`**, surrounded by several important Rails/framework mechanisms that should be documented separately rather than misclassified.