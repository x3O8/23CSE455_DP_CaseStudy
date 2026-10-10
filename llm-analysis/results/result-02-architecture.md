## 1. Architectural summary

**Baseline analyzed:**
`source_version = original`
`commit = 5e15551ee646871b4bed32c982fa17da319d3ee3`

The baseline is a conventional server-rendered Rails application centered on:

```text
Browser
  ↓
Routes
  ↓
Controllers
  ↓
Active Record models + application concerns
  ↓
PostgreSQL
```

with additional cross-cutting/application mechanisms for:

```text
Authentication → Devise
Authorization  → Pundit
Payments       → Payify → Stripe
Booking hook   → Integromat/Make
Images         → Active Storage
Browser UI     → Stimulus + Turbo/elements
```

The application-owned domain model is small: `User`, `Room`, `Booking`, and `Setting`. There is **no separate application-owned Hotel, Property, Customer, Cancellation, or AdditionalService model** in the inspected baseline. `Booking` contains cancellation state, and payment persistence is supplied through Payify.

The main application-specific behavior is distributed between Active Record models, model concerns, controller concerns, controllers, and policies rather than an `app/services` layer.

---

# 2. Architecture classification

| Mechanism                              | Classification                | Actual implementation                                        | Evidence                                           |
| -------------------------------------- | ----------------------------- | ------------------------------------------------------------ | -------------------------------------------------- |
| MVC request handling                   | Present                       | Rails routes/controllers/views                               | `config/routes.rb`, `app/controllers`, `app/views` |
| Active Record persistence/domain model | Present                       | `ApplicationRecord`, `User`, `Room`, `Booking`, `Setting`    | `app/models/*`                                     |
| Model concerns                         | Present                       | `HasOwnerConcern`, `HasPriceConcern`, `HasSettingsConcern`   | `app/models/concerns/*`                            |
| Controller concerns                    | Present                       | `CrudConcern`, `AuthConcern`, `LocaleConcern`, `PageConcern` | `app/controllers/concerns/*`                       |
| Policy-based authorization             | Present                       | `ApplicationPolicy`, resource policies, Pundit integration   | `app/policies/*`, `ApplicationController`          |
| External payment integration           | Present                       | Payify configuration/use, Stripe through Payify              | `Booking`, `payify` initializer, routes, Gemfile   |
| Webhook integration                    | Present                       | Booking callback invokes Integromat webhook                  | `Booking#notify_booking`, Integromat initializer   |
| Client-side MVC adjunct                | Present                       | Stimulus controllers and Rails/Turbo responses               | `app/javascript`, `.turbo_stream` view             |
| Persistent database                    | Present                       | PostgreSQL via Active Record                                 | `config/database.yml`, `db/schema.rb`              |
| Background jobs                        | Only base abstraction located | `ApplicationJob` only                                        | `app/jobs/application_job.rb`                      |
| Application service layer              | Not present                   | No `app/services` directory                                  | repository tree                                    |
| Separate cancellation subsystem        | Not present                   | `Booking#cancel!` + `canceled_at`                            | `app/models/booking.rb`, schema                    |

### Application-owned vs framework vs third-party

**A. Application-owned**

Examples include:

```text
Booking
Room
User
Setting
BookingsController
RoomsController
SettingsController
HomeController
CrudConcern
AuthConcern
LocaleConcern
PageConcern
HasOwnerConcern
HasPriceConcern
HasSettingsConcern
ApplicationPolicy
BookingPolicy
RoomPolicy
SettingPolicy
```

**B. Rails framework**

Examples:

```text
ActionController
ActiveRecord::Base
ActiveSupport::Concern
Active Storage
Action Mailer
Turbo Rails
Rails routing
Active Record callbacks/validations/associations
```

**C. Third-party dependencies**

Examples:

```text
Devise
Pundit
Payify
Stripe
Integromat
Kaminari
Capybara
Selenium
Dropzone
Easepick
Day.js
```

For later pattern work, these categories must stay separate. A behavior inside a gem is not automatically evidence of a pattern in the application.

---

# 3. Component inventory

| Component              | Type                                   | Actual files/classes/modules                                  | Responsibility                                                                      | Depends on                                                        | Used by                                 | Evidence                                                                      |
| ---------------------- | -------------------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------------------------- |
| User                   | Model                                  | `app/models/user.rb` → `User`                                 | Account/authentication, owner of rooms/bookings, settings association               | Active Record, Devise, `HasSettingsConcern`, `CurrentScope`       | Controllers/models                      | `User` declares `has_many :rooms`, `has_many :bookings`, Devise configuration |
| Room                   | Model                                  | `app/models/room.rb` → `Room`                                 | Accommodation data, pricing attribute, images, bookings, availability dates         | Active Record, Active Storage, `HasOwnerConcern`, slug dependency | `RoomsController`, `Booking`, views     | `has_many :bookings`, `has_many_attached :images`, `booked_dates`             |
| Booking                | Model                                  | `app/models/booking.rb` → `Booking`                           | Reservation lifecycle, validation, pricing integration, payment and webhook trigger | Active Record, model concerns, Payify, Integromat                 | `BookingsController`, `Room`, views     | callbacks, associations, validators, `cancel!`, `notify_booking`              |
| Setting                | Model                                  | `app/models/setting.rb` → `Setting`                           | User VAT setting                                                                    | Active Record                                                     | `HasPriceConcern`, `SettingsController` | `belongs_to :user`                                                            |
| Booking controller     | Controller                             | `app/controllers/bookings_controller.rb`                      | Booking CRUD plus cancellation and payment initialization                           | `CrudConcern`, Pundit, Booking/Payify                             | Rails router/views                      | `include CrudConcern`, `cancel`, `stripe_init_intent`                         |
| Room controller        | Controller                             | `app/controllers/rooms_controller.rb`                         | Room CRUD and creation of booking form object                                       | `CrudConcern`, Room/Booking, Active Storage                       | Rails router/views                      | `object_class`, `init_booking_form`                                           |
| Settings controller    | Controller                             | `app/controllers/settings_controller.rb`                      | User settings editing                                                               | `CrudConcern`, Setting, Pundit                                    | Rails router/views                      | custom `set_object`, `redirect_to_show`                                       |
| Application controller | Controller base                        | `app/controllers/application_controller.rb`                   | Common request setup                                                                | Pundit, controller concerns                                       | All application controllers             | includes Pundit + 3 concerns and `before_action`                              |
| CRUD concern           | Module                                 | `app/controllers/concerns/crud_concern.rb`                    | Shared CRUD flow and overridable controller hooks                                   | Rails controller API, Pundit, Kaminari                            | Booking/Room/Setting controllers        | `create`, `update`, `index`, `set_object`, abstract methods                   |
| Auth concern           | Module                                 | `app/controllers/concerns/auth_concern.rb`                    | Populate `CurrentScope.user_id` from current authenticated user                     | Devise's `current_user`, `CurrentScope`                           | ApplicationController                   | `set_current_scope`                                                           |
| Locale concern         | Module                                 | `app/controllers/concerns/locale_concern.rb`                  | Locale selection and request wrapping                                               | I18n, cookies, Rails callbacks                                    | ApplicationController                   | `switch_locale`, `around_action`                                              |
| Page concern           | Module                                 | `app/controllers/concerns/page_concern.rb`                    | Common page metadata                                                                | I18n, request state                                               | ApplicationController                   | `set_page_variables`                                                          |
| Owner concern          | Module                                 | `app/models/concerns/has_owner_concern.rb`                    | Assign current user as owner before validation                                      | `User.current`, Active Record callbacks                           | Room and Booking                        | `before_validation :assign_owner`                                             |
| Price concern          | Module                                 | `app/models/concerns/has_price_concern.rb`                    | Booking price computation and save-time totals                                      | Room, Setting, Active Record callbacks                            | Booking                                 | `compute_price_ht`, `compute_price_ttc`, callbacks                            |
| Settings concern       | Module                                 | `app/models/concerns/has_settings_concern.rb`                 | Create associated setting after user creation                                       | Active Record callback/association                                | User                                    | `after_create :create_setting`, `has_one :setting`                            |
| Policies               | Authorization classes                  | `app/policies/*`                                              | Authorization decisions                                                             | Pundit                                                            | controllers/views                       | `authorize`, `policy(...).edit?`                                              |
| Payify/Stripe          | External integration                   | Payify gem + `config/initializers/payify.rb` + mounted engine | Payment initialization/storage/UI                                                   | Payify, Stripe, env vars                                          | Booking/controller/views                | `Booking` payment concern + `stripe_init_intent`                              |
| Integromat/Make        | External integration                   | `config/initializers/integromat.rb`, `Booking#notify_booking` | Booking webhook trigger                                                             | Integromat gem, environment vars                                  | Booking callback                        | webhook configuration and trigger                                             |
| Database               | Infrastructure                         | PostgreSQL + Active Record                                    | Persistent storage                                                                  | `pg`, PostgreSQL                                                  | Models                                  | `config/database.yml`, schema                                                 |
| Views                  | Presentation                           | `app/views/bookings`, `rooms`, `settings`, `devise`, `payify` | HTML/Turbo presentation                                                             | Rails view layer                                                  | Controllers/browser                     | ERB/Turbo templates                                                           |
| Frontend controllers   | Client-side                            | `app/javascript/controllers/*`                                | Date picker, image uploads, modals                                                  | Stimulus, Active Storage, Dropzone, Easepick                      | Views/browser                           | JS controller implementations                                                 |
| Authentication         | Dependency-backed application facility | Devise + `User` + routes                                      | Sign up/login/session functionality                                                 | Devise, Active Record                                             | Controllers/router                      | `devise_for :users`, `devise` in User                                         |
| Authorization          | Application + dependency               | Pundit + policies                                             | Resource access decisions                                                           | Pundit                                                            | Controllers/views                       | `include Pundit::Authorization`, policy classes                               |

---

# 4. Domain collaboration map

## User ↔ Booking

**Caller:** `Booking` / associated Active Record machinery
**Callee:** `User` association

**Relationship:** `Booking` belongs to a `User`; `User` has many bookings.

**Evidence:**

```text
app/models/booking.rb
  belongs_to :user

app/models/user.rb
  has_many :bookings
```

**Purpose:** associate each booking with the user who made/owns it.

---

## User ↔ Room

**Caller/callee:** Active Record association navigation

```text
Room.belongs_to :user
User.has_many :rooms
```

Evidence:

```text
app/models/room.rb
  belongs_to :user

app/models/user.rb
  has_many :rooms
```

`HasOwnerConcern` also writes the owner ID when absent:

```text
app/models/concerns/has_owner_concern.rb
  self.user_id = User.current.id if user_id.nil? && User.current
```

---

## Room ↔ Booking

**Caller:** `Booking#dates_are_available`
**Callee:** `room.bookings`

Evidence:

```text
app/models/booking.rb
  conflicting_bookings = room.bookings.where.not(id: id)
```

**Direction:** Booking → Room association → Booking relation.

Conversely, `Room` uses its booking association in `booked_dates`:

```text
app/models/room.rb
  bookings.where("end_date >= ?", Date.today)
```

This is a bidirectional conceptual association implemented through Active Record associations.

---

## Booking ↔ Setting

**Caller:** `HasPriceConcern#vat`
**Callee:** `room.user.setting.vat`

Evidence:

```text
app/models/concerns/has_price_concern.rb

def vat
  room.user.setting.vat || 0.2
end
```

**Direction:**

```text
Booking
  → room
    → user
      → setting
        → vat
```

**Purpose:** determine VAT used when calculating the total price.

---

## Booking ↔ payment

**Application-side caller:** `BookingsController#stripe_init_intent`

```text
app/controllers/bookings_controller.rb

return unless @object.payment_pending?

@object.payment.stripe_init_intent
```

`Booking` itself includes:

```text
include ::Payify::HasPaymentConcern
```

and exposes application-level status queries:

```text
payment_pending?
paid?
amount_to_pay
```

**Boundary:** payment object/operations are partly supplied by Payify. The repository does not contain the implementation of `Payify::HasPaymentConcern` or Payify's payment engine.

---

## Booking ↔ webhook/integration

**Caller:** `Booking#notify_booking`
**Callee:** `Integromat::Webhook#trigger`

Evidence:

```text
app/models/booking.rb

Integromat::Webhook.new(:booking).trigger(
  start: start_date,
  end: end_date,
  guests: num_guests,
  room: room.title,
  user: user.email,
  total_ht: total_ht
)
```

The operation is invoked through an Active Record callback:

```text
after_create :notify_booking
```

Configuration originates in:

```text
config/initializers/integromat.rb
```

---

## Controller ↔ model

For booking creation, `CrudConcern#create` performs:

```text
@object = object_class.new(form_values)

if @object.valid?
  @object.save!
```

`BookingsController` supplies:

```text
base_class → Booking
object_class → Booking.where(user_id: current_user.id)
model_params → :booking
```

Therefore the concrete flow is:

```text
BookingsController
  → CrudConcern#create
    → Booking.new(...)
      → Booking#valid?
      → Booking#save!
```

---

## Controller ↔ concerns

`ApplicationController` includes:

```text
Pundit::Authorization
PageConcern
LocaleConcern
AuthConcern
```

and `BookingsController`, `RoomsController`, and `SettingsController` each include:

```text
CrudConcern
```

The concern therefore supplies actual executable controller behavior rather than being merely a namespace.

---

## Model ↔ concerns

Observed direct inclusion relationships:

```text
Booking
  → Payify::HasPaymentConcern
  → HasOwnerConcern
  → HasPriceConcern

Room
  → HasOwnerConcern

User
  → HasSettingsConcern
```

The concerns inject callbacks and/or methods into the including model.

---

## Controller ↔ policy

`CrudConcern` calls:

```text
authorize base_class
authorize object_class
authorize @object
```

`BookingsController#cancel` additionally calls:

```text
authorize @object
```

Views also directly query policies, for example:

```text
policy(@object).edit?
policy(@object).destroy?
policy(:booking).new?
```

The actual policy implementations are under `app/policies`.

---

# 5. Booking creation flow

## Actual request path

```text
Browser
   ↓
POST /:locale/bookings
   ↓
BookingsController
   ↓
CrudConcern#create
   ↓
authorize object_class
   ↓
Booking.new(form_values)
   ↓
Booking validations
   ├─ presence validation
   ├─ end_date_greater_than_start_date
   └─ dates_are_available
   ↓
Booking.save!
   ↓
Active Record callbacks
   ├─ HasPriceConcern before_save pricing callbacks
   ├─ Booking after_save :create_payment
   └─ Booking after_create :notify_booking
   ↓
redirect_to_show(@object)
```

### Route

`config/routes.rb` defines:

```text
resources :bookings
```

inside:

```text
scope '/:locale'
```

so the POST create action is dispatched by Rails routing to `BookingsController#create`.

### Controller path

`CrudConcern#create`:

```text
authorize object_class
@object = object_class.new(form_values)

if @object.valid?
  @object.save!
  redirect_to_show(@object)
else
  render :new, status: :unprocessable_entity
end
```

`BookingsController` supplies:

```text
object_class
strong_params
model_params
```

with `model_params = :booking`.

### Authorization

`authorize object_class` invokes Pundit authorization for the booking model/relation.

The exact policy selected is framework-mediated, with application policy classes located in `app/policies`.

### Model construction and validation

`Booking` validates:

```text
:start_date
:end_date
:room_id
:user_id
```

and custom validations:

```text
end_date_greater_than_start_date
dates_are_available
```

### Persistence-side processing

`HasPriceConcern` registers:

```text
before_save :set_price_ht, :set_price_ttc, if: :start_or_end_changed?
```

`Booking` registers:

```text
after_save :create_payment
after_create :notify_booking
```

The callback implementations supplied directly by the application are not all present in `Booking`; `create_payment` comes from the included Payify concern.

### Response

Successful creation calls:

```text
redirect_to_show(@object)
```

which is defined in `CrudConcern` as a redirect to:

```text
polymorphic_path(object, locale: @page_lang)
```

---

# 6. Availability flow

There are **two observable availability mechanisms**: server-side validation and browser-side date selection.

## Server-side authoritative validation path

Entry point:

```text
Booking#dates_are_available
```

The method queries:

```ruby
room.bookings.where.not(id: id)
             .where("(? < end_date) AND (? > start_date)", start_date, end_date)
```

and checks:

```text
conflicting_bookings.exists?
```

If a conflict exists:

```text
errors.add(:base, I18n.t("activerecord.errors.models.booking.unavailable_dates"))
```

Thus:

```text
Booking creation/update
  → Booking#valid?
  → Booking#dates_are_available
  → Room#bookings association
  → PostgreSQL query through Active Record
  → exists?
  → validation success/failure
```

## Client-side availability assistance

`Room#booked_dates` queries current/future bookings:

```text
bookings.where("end_date >= ?", Date.today)
         .pluck(:start_date, :end_date)
         .map(...)
```

`datepicker_controller.js` reads these dates from the Stimulus data attributes:

```text
this.data.get("bookedDates")
```

and passes them to Easepick's lock/filter configuration.

Thus the frontend prevents/selectively restricts dates before submission, while the server-side `Booking#dates_are_available` performs the actual model validation.

The inspected source does **not** establish that the browser-side restriction is the only availability mechanism; the server-side validation is explicit.

---

# 7. Payment flow

## Application-side path

The payment-related source establishes this structure:

```text
Booking
  └─ Payify::HasPaymentConcern

BookingsController#show
  └─ stripe_init_intent
       └─ @object.payment_pending?
       └─ @object.payment.stripe_init_intent
```

### Booking creation

`Booking` declares:

```text
after_save :create_payment
```

but `create_payment` itself is not implemented in `Booking`.

That callback therefore crosses into behavior contributed by the Payify concern/dependency.

### Payment initialization

`BookingsController` has:

```text
before_action :stripe_init_intent, only: [:show]
```

and:

```text
def stripe_init_intent
  return unless @object.payment_pending?

  @object.payment.stripe_init_intent
end
```

The application checks status, then asks the payment object to initialize the Stripe payment intent.

### Payify configuration

```text
config/initializers/payify.rb
```

contains:

```text
Payify.setup do |config|
  config.currency = ENV["PAYMENT_CURRENCY"]
end
```

The Rails router also mounts the Payify engine:

```text
mount Payify::Engine => '/payify', as: 'payify'
```

### Payment persistence

`db/schema.rb` contains:

```text
payify_payments
```

with payment status, amount, payment method, transaction ID and Stripe-related columns.

### Boundary limitation

The baseline repository does **not** contain the internal implementation of:

```text
Payify::HasPaymentConcern
Payify::Engine
payment.stripe_init_intent
```

Therefore the complete Stripe execution sequence cannot be established solely from this repository. The application-side boundary is confirmed; internal gem-side behavior must be verified from the exact Payify dependency version separately.

---

# 8. Cancellation flow

The application does **not** define a separate cancellation domain class/table.

## Actual path

```text
Browser
  ↓
POST /:locale/bookings/:id/cancel
  ↓
BookingsController#cancel
  ↓
set_object
  ↓
authorize @object
  ↓
Booking#cancel!
  ↓
update_attribute :canceled_at, Time.now
  ↓
redirect_to_show(@object)
```

### Controller

`BookingsController#cancel`:

```text
set_object
authorize @object
@object.cancel!
redirect_to_show(@object)
```

### State change

`Booking#cancel!`:

```text
update_attribute :canceled_at, Time.now
```

### State query

`Booking#canceled?` checks:

```text
canceled_at.present?
```

### Policy

`BookingPolicy` defines:

```text
cancel?
  → update?
```

and `update?` requires:

```text
super && @record.user == @user
```

### External effects

The inspected application-side cancellation method does **not explicitly call** Payify, Integromat, mailers, or another cancellation service.

The source therefore supports the claim that cancellation directly changes `canceled_at`; it does not support claiming a separate external cancellation workflow.

---

# 9. Webhook/notification flow

## Trigger

`Booking` declares:

```text
after_create :notify_booking
```

Therefore the trigger is the successful creation lifecycle of a booking.

## Configuration

`config/initializers/integromat.rb`:

```text
require "integromat"

Integromat.configure do |c|
  uri = ENV["INTEGROMAT_BASE_URI"]
  booking_hook = ENV["INTEGROMAT_BOOKING_HOOK"]

  c.web_hooks = { booking: booking_hook } if booking_hook.present?
  c.base_uri = uri if uri.present?
end
```

## Dispatch

`Booking#notify_booking`:

```text
return unless Integromat.config.web_hooks.key?(:booking)

Integromat::Webhook.new(:booking).trigger(...)
```

## Payload

The application sends:

```text
start
end
guests
room
user
total_ht
```

where:

```text
room = room.title
user = user.email
```

Therefore the application-side sequence is:

```text
Booking saved
  ↓
after_create
  ↓
Booking#notify_booking
  ↓
check configured booking webhook
  ↓
construct Integromat::Webhook(:booking)
  ↓
trigger(payload)
  ↓
external Integromat/Make endpoint
```

The actual remote workflow after the HTTP call is **not observable in this repository**.

---

# 10. Concern/module analysis

## 10.1 `HasOwnerConcern`

**File:** `app/models/concerns/has_owner_concern.rb`

**Including models:**

```text
Booking
Room
```

**Provided behavior:**

```text
before_validation :assign_owner
```

and private:

```text
assign_owner
```

**Dependencies:**

```text
User.current
user_id
Active Record callback system
```

**Call relationship:**

```text
model validation
  → assign_owner
  → User.current
  → user_id assignment
```

**Architectural role:** reusable model-level lifecycle behavior / owner assignment.

---

## 10.2 `HasPriceConcern`

**File:** `app/models/concerns/has_price_concern.rb`

**Including model:**

```text
Booking
```

**Methods:**

```text
compute_price_ht
vat
compute_price_ttc
set_price_ht
set_price_ttc
```

**Callback:**

```text
before_save :set_price_ht, :set_price_ttc, if: :start_or_end_changed?
```

**Dependencies:**

```text
room
room.day_price
room.user.setting.vat
Booking#start_or_end_changed?
```

**Call structure:**

```text
save
  → set_price_ht
      → compute_price_ht
          → room.day_price

  → set_price_ttc
      → compute_price_ttc
          → total_ht
          → vat
              → room.user.setting.vat
```

**Architectural role:** reusable model behavior and callback-driven cross-cutting pricing logic.

---

## 10.3 `HasSettingsConcern`

**File:** `app/models/concerns/has_settings_concern.rb`

**Including model:**

```text
User
```

**Injected behavior:**

```text
after_create :create_setting
has_one :setting
```

The implementation of `create_setting` itself is not declared in this concern; it is supplied by Active Record's association-generated behavior.

**Architectural role:** association + lifecycle setup injected into `User`.

---

## 10.4 `AuthConcern`

**File:** `app/controllers/concerns/auth_concern.rb`

**Including class:**

```text
ApplicationController
```

**Method:**

```text
set_current_scope