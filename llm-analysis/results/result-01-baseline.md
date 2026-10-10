# Baseline Reproducibility Record — `rails-room-booking`

**Repository inspected:** `andrewdsilva/rails-room-booking`
**Inspection basis:** GitHub repository contents, Git history, dependency lockfile, configuration, application source, tests, schema/migrations, and supplied faculty instructions.
**Pattern analysis:** intentionally **not performed** in this baseline task.

A key point for the case study: the repository's current default branch is `main`, but the reproducible baseline below is pinned to the exact HEAD commit rather than the moving branch.

## A. Baseline identification table

| Item                    | Baseline finding                                                                                      | Evidence                                           |
| ----------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Repository owner        | `andrewdsilva`                                                                                        | GitHub repository metadata                         |
| Repository name         | `rails-room-booking`                                                                                  | GitHub repository metadata                         |
| Full repository         | `andrewdsilva/rails-room-booking`                                                                     | GitHub repository metadata                         |
| Visibility              | Public                                                                                                | GitHub repository metadata                         |
| Default branch          | `main`                                                                                                | Repository metadata                                |
| Current HEAD on `main`  | `5e15551ee646871b4bed32c982fa17da319d3ee3`                                                            | Latest repository commit                           |
| HEAD commit date        | 2023-07-16 04:45:38 UTC                                                                               | Git commit metadata                                |
| HEAD commit message     | `Merge pull request #7 from bretheskevin/docker-sql` / `Add PostgreSql database with docker-compose.` | Git commit metadata                                |
| Relevant latest change  | PostgreSQL + Docker/Docker Compose support                                                            | HEAD diff                                          |
| Repository releases     | None returned                                                                                         | GitHub `/releases`                                 |
| Repository tags         | No tag result was established from the inspection available                                           | Not sufficient to claim tags exist or do not exist |
| License metadata        | GitHub API reports `license: null`; README contains an MIT license badge/link                         | Repository metadata + README                       |
| Source-version identity | immutable commit, not `main`                                                                          | Required by case-study instructions                |

The selected HEAD is particularly important because commit `5e15551...` is the commit that introduced the PostgreSQL/Docker setup and is the current `main` HEAD. Its diff explicitly changes the application from SQLite to PostgreSQL, adds database environment variables, and updates Docker configuration. Therefore that commit, rather than an earlier SQLite commit, is the appropriate current repository baseline.

**Proposed immutable baseline:**

```text
source_version = original
baseline_commit = 5e15551ee646871b4bed32c982fa17da319d3ee3
baseline_ref = main@5e15551ee646871b4bed32c982fa17da319d3ee3
```

The faculty instructions explicitly require the exact baseline commit and prohibit relying on a moving branch alone.

## B. Environment table

| Item                             | Observed value                                                                                                       | Source                                     |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| Language                         | Ruby                                                                                                                 | Repository metadata                        |
| Ruby declared version            | `2.7.5`                                                                                                              | `Gemfile`                                  |
| Ruby locked version              | `ruby 2.7.5p203`                                                                                                     | `Gemfile.lock`                             |
| Rails declared constraint        | `~> 7.0.4`                                                                                                           | `Gemfile`                                  |
| Rails locked version             | `7.0.6`                                                                                                              | `Gemfile.lock`                             |
| Bundler                          | `2.4.17`                                                                                                             | `Gemfile.lock`                             |
| Database adapter                 | PostgreSQL                                                                                                           | `Gemfile`, `config/database.yml`           |
| PostgreSQL adapter gem           | `pg 1.5.3`                                                                                                           | `Gemfile.lock`                             |
| Production/development/test DBs  | `rails_room_booking_development`, `rails_room_booking_test`, `rails_room_booking_production`                         | `config/database.yml`                      |
| Web server                       | Puma                                                                                                                 | `Gemfile`, lockfile                        |
| Puma locked version              | `5.6.6`                                                                                                              | `Gemfile.lock`                             |
| Test framework                   | RSpec / RSpec Rails                                                                                                  | `Gemfile`, `spec/rails_helper.rb`          |
| RSpec Rails                      | `6.0.3`                                                                                                              | `Gemfile.lock`                             |
| System test stack                | Capybara + Selenium WebDriver + Webdrivers                                                                           | `Gemfile`, lockfile                        |
| Authorization                    | Pundit `2.3.0`                                                                                                       | `Gemfile.lock`                             |
| Authentication                   | Devise `4.9.2`                                                                                                       | `Gemfile.lock`                             |
| Payments                         | Payify `0.1.18`, Stripe `8.5.0`                                                                                      | `Gemfile.lock`                             |
| External automation/webhook      | Integromat `0.1.0`                                                                                                   | `Gemfile.lock`                             |
| Money handling                   | Money `6.16.0`                                                                                                       | `Gemfile.lock`                             |
| Pagination                       | Kaminari `1.2.2`                                                                                                     | `Gemfile.lock`                             |
| Image processing                 | `image_processing 1.12.2`, MiniMagick, ruby-vips                                                                     | `Gemfile.lock`                             |
| Front-end/framework dependencies | Bootstrap, Turbo Rails, Stimulus Rails, JS/CSS bundling, Importmap                                                   | `Gemfile` / lockfile                       |
| I18n                             | `i18n-js`, `rails-i18n`                                                                                              | `Gemfile` / lockfile                       |
| Asset pipeline                   | Sprockets Rails                                                                                                      | `Gemfile`                                  |
| Docker base image                | `ruby:2.7.5`                                                                                                         | `Dockerfile`                               |
| Docker services                  | `app`, `db`                                                                                                          | `docker-compose.yml`                       |
| Database container               | `postgres` image                                                                                                     | `docker-compose.yml`                       |
| Application port                 | `3000`                                                                                                               | `Dockerfile`, `docker-compose.yml`, README |
| Bundled environment management   | `dotenv-rails`                                                                                                       | `Gemfile`                                  |
| Static-analysis/lint             | RuboCop is declared in README as a project dependency/tool, but the Gemfile inspected does not contain a RuboCop gem | README + Gemfile                           |
| CI environment                   | No CI execution result was established in this baseline inspection                                                   | Not established                            |

The README declares Ruby 2.7.5 and Rails 7.0.4, while the lockfile fixes Rails at 7.0.6 and Ruby at 2.7.5p203. For reproducibility, the **lockfile values should be treated as the dependency-resolution baseline**, not the looser README description.

The README's documented installation flow is:

```text
bundle install
rails db:create
rails db:migrate
rails db:seed
rails s
```

and its Docker flow uses `docker-compose build`, `docker-compose up`, followed by the database setup commands.

## C. Repository/module inventory

### Top-level/application structure

The application has the normal Rails structure plus explicit domain/security/integration areas:

| Directory                  | Status                               | Baseline role                                                                               |
| -------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------- |
| `app/models`               | inspected                            | Domain/persistence models                                                                   |
| `app/models/concerns`      | inspected                            | Reusable application model modules                                                          |
| `app/controllers`          | inspected                            | HTTP/controller layer                                                                       |
| `app/controllers/concerns` | inspected                            | Shared controller behavior                                                                  |
| `app/policies`             | inspected                            | Authorization rules                                                                         |
| `app/views`                | partially inspected                  | Booking/room/settings/UI views                                                              |
| `app/jobs`                 | inspected                            | Rails job layer; only `application_job.rb` present                                          |
| `app/mailers`              | inspected                            | Rails mailer layer; only `application_mailer.rb` present                                    |
| `app/javascript`           | partially inspected                  | Stimulus/browser-side behavior                                                              |
| `app/assets`               | partially inspected                  | Asset pipeline/resources                                                                    |
| `config`                   | inspected for relevant configuration | Routes, DB, environment, initializers                                                       |
| `db/schema.rb`             | inspected                            | Current schema representation                                                               |
| `db/migrate`               | inspected                            | Database evolution history                                                                  |
| `spec`                     | inspected                            | RSpec test suite                                                                            |
| `lib`                      | inspected                            | Rails tasks/assets; no application services directory                                       |
| `vendor`                   | not comprehensively inspected        | Dependency/vendor assets; outside primary application design scope unless directly relevant |

### Models actually present

The repository contains these application model files:

```text
app/models/application_record.rb
app/models/booking.rb
app/models/room.rb
app/models/setting.rb
app/models/user.rb
```

There is also:

```text
app/models/concerns/has_owner_concern.rb
app/models/concerns/has_price_concern.rb
app/models/concerns/has_settings_concern.rb
```

No separate application model for **Hotel**, **Property**, **Customer**, **Payment**, **Cancellation**, or **AdditionalService** was found during this baseline inventory. The actual domain vocabulary includes `Room`, `Booking`, `User`, `Setting`, and Payify's payment model/table.

### Controllers actually present

```text
app/controllers/application_controller.rb
app/controllers/home_controller.rb
app/controllers/bookings_controller.rb
app/controllers/rooms_controller.rb
app/controllers/settings_controller.rb
app/controllers/payify/...
```

Shared controller concerns:

```text
app/controllers/concerns/auth_concern.rb
app/controllers/concerns/crud_concern.rb
app/controllers/concerns/locale_concern.rb
app/controllers/concerns/page_concern.rb
```

`BookingsController` delegates much of its CRUD behavior through `CrudConcern`, while adding booking-specific cancellation and payment initialization behavior. This is an observed implementation fact for later source analysis, **not a pattern classification**.

### Services/modules

No `app/services` directory was found.

Application modules that are relevant to later source analysis include:

```text
HasOwnerConcern
HasPriceConcern
HasSettingsConcern
AuthConcern
CrudConcern
LocaleConcern
PageConcern
```

This is important because later pattern analysis must treat these as actual modules/functions rather than inventing service classes.

### Jobs

Only:

```text
app/jobs/application_job.rb
```

was found. No domain-specific background job was identified during the inventory.

### Mailers

Only:

```text
app/mailers/application_mailer.rb
```

was found. No booking-specific mailer was identified.

### External integrations/configuration

Two application-level integrations are explicitly represented:

**Payify/Stripe**

- `Gemfile`: `payify`
- `Gemfile.lock`: Payify `0.1.18`, Stripe `8.5.0`
- `config/initializers/payify.rb`
- `config/routes.rb`: Payify engine mounted at `/payify`
- Payify migration files under `db/migrate`

**Integromat/Make**

- `Gemfile`: `integromat`
- `Gemfile.lock`: `integromat 0.1.0`
- `config/initializers/integromat.rb`
- `Booking` contains booking-notification/webhook logic

The README explicitly documents both online Stripe payment and a booking webhook integration with Integromat/Make.

### Policies

Actual policy files:

```text
app/policies/application_policy.rb
app/policies/booking_policy.rb
app/policies/room_policy.rb
app/policies/setting_policy.rb
```

No `user_policy.rb` was found.

### Views/components relevant to booking

Booking views:

```text
app/views/bookings/_booking.html.erb
app/views/bookings/_form.html.erb
app/views/bookings/index.html.erb
app/views/bookings/new.turbo_stream.erb
app/views/bookings/show.html.erb
```

Room views include:

```text
app/views/rooms/index.html.erb
app/views/rooms/new.html.erb
app/views/rooms/show.html.erb
```

Settings views include:

```text
app/views/settings/_form.html.erb
app/views/settings/new.html.erb
```

Authentication views are under:

```text
app/views/devise/
```

Payment-specific views exist under:

```text
app/views/payify/
```

The repository also has front-end Stimulus controllers for application behavior, including:

```text
app/javascript/controllers/application.js
app/javascript/controllers/datepicker_controller.js
app/javascript/controllers/image_uploader_controller.js
app/javascript/controllers/index.js
app/javascript/controllers/modal_controller.js
```

## D. Initial domain model inventory

This is a **domain inventory only**, not a pattern analysis.

| Domain concept        | Actual implementation                                              | Evidence in schema/source                  | Status                            |
| --------------------- | ------------------------------------------------------------------ | ------------------------------------------ | --------------------------------- |
| User/customer/account | `User`                                                             | `app/models/user.rb`, `users` table        | Confirmed entity                  |
| Room/accommodation    | `Room`                                                             | `app/models/room.rb`, `rooms` table        | Confirmed entity                  |
| Booking/reservation   | `Booking`                                                          | `app/models/booking.rb`, `bookings` table  | Confirmed entity                  |
| Property/hotel        | No separate `Hotel`/`Property` model found                         | Room appears to represent accommodation    | No separate entity                |
| Payment               | Payify integration/model                                           | `payify_payments` table and Payify concern | Dependency-integrated entity      |
| Cancellation          | No separate cancellation class/table                               | `Booking#cancel!`, `canceled_at`           | Booking state                     |
| Pricing               | `HasPriceConcern`, booking totals, `Room#day_price`, `Setting#vat` | model source/schema                        | Embedded pricing logic            |
| Availability          | `Booking#dates_are_available`, `Room#booked_dates`                 | model source                               | Booking/room behavior             |
| Additional services   | No corresponding model/table found                                 | schema/domain inventory                    | Not present                       |
| Notification/webhook  | Integromat webhook from `Booking`                                  | initializer + booking model                | Integration behavior              |
| Authentication        | Devise-backed `User`                                               | `User`, routes, migration, initializer     | Framework/dependency-backed       |
| Authorization         | Pundit policies                                                    | `app/policies/*`                           | Application code using dependency |
| Persistence           | Active Record + PostgreSQL                                         | models/schema/database config              | Rails framework                   |
| Image storage         | Active Storage                                                     | room model/schema/storage config           | Rails framework                   |

The schema currently contains tables for `users`, `rooms`, `bookings`, `settings`, Payify payments, and Active Storage. The booking table contains dates, guest count, room/user references, total prices, and `canceled_at`. The room table contains accommodation attributes, pricing, location, and owner reference.

## E. Test inventory

### Framework

The test stack is RSpec/RSpec Rails.

Evidence:

```text
Gemfile
  gem "rspec-rails"

Gemfile.lock
  rspec-rails 6.0.3
  rspec-core 3.12.2
  rspec-expectations 3.12.3
  rspec-mocks 3.12.6
```

### Test infrastructure

Relevant files:

```text
spec/rails_helper.rb
spec/spec_helper.rb
spec/support/chrome.rb
spec/factories.rb
spec/factories/bookings.rb
spec/factories/rooms.rb
spec/factories/users.rb
```

`rails_helper.rb` configures Active Record transactional fixtures and automatically loads support files.

`spec/support/chrome.rb` configures Selenium/Chrome for system tests, using headless Chrome by default unless `SHOW_BROWSER=true`.

### Discovered specifications

The model test inventory includes:

```text
spec/models/booking_spec.rb
spec/models/room_spec.rb
```

The inspected `booking_spec.rb` checks:

- booking price calculation;
- VAT-inclusive calculation;
- required booking dates;
- invalid date ordering;
- valid non-conflicting dates;
- rejection of conflicting bookings.

`room_spec.rb` checks room creation and the `room_type` value.

No controller/system/request spec was established from the inspected tree in this baseline pass.

### Test command

The README explicitly specifies:

```bash
rspec
```

for the test suite.

The repository also has the infrastructure for browser/system tests through Capybara/Selenium, although an actual system-test specification was not established in the inspected inventory.

### Actual test execution

**Not run.**

Therefore:

```text
test_result = not_run
reason = Repository inspection task only; no execution environment was established during baseline source inspection.
```

This follows the faculty requirement not to fabricate test results or runtime measurements.

## F. Reproducibility checklist

| Check                                          | Status  | Evidence/requirement                                                       |
| ---------------------------------------------- | ------- | -------------------------------------------------------------------------- |
| Repository URL recorded                        | ✓       | GitHub repository                                                          |
| Owner/name recorded                            | ✓       | `andrewdsilva/rails-room-booking`                                          |
| Default branch recorded                        | ✓       | `main`                                                                     |
| Immutable baseline SHA recorded                | ✓       | `5e15551ee646871b4bed32c982fa17da319d3ee3`                                 |
| Commit date recorded                           | ✓       | 2023-07-16 04:45:38 UTC                                                    |
| Lockfile preserved                             | ✓       | `Gemfile.lock`                                                             |
| Ruby version identified                        | ✓       | `2.7.5p203`                                                                |
| Rails version identified                       | ✓       | `7.0.6`                                                                    |
| Bundler version identified                     | ✓       | `2.4.17`                                                                   |
| Database identified                            | ✓       | PostgreSQL                                                                 |
| Database env variables identified              | ✓       | `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT` |
| `.env` requirement identified                  | ✓       | README / Docker setup                                                      |
| Dockerfile inspected                           | ✓       | Ruby 2.7.5 image                                                           |
| Docker Compose inspected                       | ✓       | app + PostgreSQL                                                           |
| Startup command identified                     | ✓       | `rails s` / Docker `rails server -b 0.0.0.0`                               |
| Database setup commands identified             | ✓       | `rails db:create`, `db:migrate`, `db:seed`                                 |
| Test framework identified                      | ✓       | RSpec                                                                      |
| Test command identified                        | ✓       | `rspec`                                                                    |
| System-test dependencies identified            | ✓       | Capybara/Selenium/Webdrivers                                               |
| Lint/static analysis documented                | Partial | README says RuboCop; no RuboCop dependency was found in Gemfile            |
| License verified from metadata                 | No      | GitHub metadata says `license:null`                                        |
| README license claim recorded                  | ✓       | README shows MIT badge/link                                                |
| Baseline source modified                       | No      | Repository only inspected                                                  |
| Runtime test result recorded honestly          | ✓       | `not_run`                                                                  |
| Exact source version suitable for future diffs | ✓       | immutable commit                                                           |

The supplied faculty instructions also require README documentation of source commits, environment versions, commands, inspected modules, LOC/complexity/timing rules, and limitations.

## G. Proposed exact baseline source_version identifier

Use this consistently in every Part 1 record:

```text
source_version = original
commit_sha = 5e15551ee646871b4bed32c982fa17da319d3ee3
```

Recommended human-readable baseline label for your internal README:

```text
Original — 5e15551ee646871b4bed32c982fa17da319d3ee3
```

Do **not** subsequently replace this with `main`, `latest`, `HEAD`, or another moving reference.

The baseline commit is the merge commit that added PostgreSQL/Docker support. Its recorded commit date is **2023-07-16**, and its diff shows the preceding application used SQLite. Thus the earlier SQLite state is historical context, not the selected `original` baseline.

## H. Risks / limitations affecting later analysis

### 1. README and lockfile differ slightly

README describes Rails `7.0.4`, while `Gemfile.lock` resolves Rails `7.0.6`. The baseline should use the **actual locked dependency versions** for reproducibility.

### 2. PostgreSQL configuration is environment-dependent

`config/database.yml` expects:

```text
DATABASE_USERNAME
DATABASE_PASSWORD
DATABASE_HOST
DATABASE_PORT
```

and Docker Compose also consumes these variables. A complete execution environment therefore requires appropriate database credentials/environment values.

### 3. Secrets/environment files are external to the reproducible source snapshot

The README documents Stripe and Integromat environment variables. Those external credentials/configuration values should not be copied into the case-study repository. The faculty instructions explicitly prohibit uploading passwords.

### 4. License evidence is inconsistent in strength

The README displays an MIT license badge/link, but GitHub repository metadata returned no license object. This should be documented as **README-claimed MIT**, rather than asserting that GitHub has formally detected the license.

### 5. RuboCop status needs verification before being used as evidence

The README presents RuboCop as part of the project, but the inspected `Gemfile` does not declare a RuboCop gem. Therefore we should not yet claim that a reproducible RuboCop command exists in the baseline environment.

### 6. No `app/services` layer

There is no application services directory in the inspected repository. Later analysis must therefore use the actual modules/models/controllers that exist rather than imposing a service-layer interpretation.

### 7. Payment behavior partly belongs to an external dependency

Payify supplies payment-related functionality and migrations. Later pattern evidence must explicitly distinguish:

```text
application code
vs.
Payify dependency/framework behavior
```

This is particularly important under your evidence rules.

### 8. Domain granularity is uneven

The application does not have separate classes for every conceptual term in the case-study brief. For example, cancellation is represented as booking state/behavior rather than a separate `Cancellation` entity, and no additional-services entity was found. Later analysis must reflect the repository's actual model rather than the assignment vocabulary.

### 9. Test coverage appears narrow

The inspected repository contains model specifications for booking and room behavior, but the baseline inventory did not establish comprehensive controller/system/integration coverage. This limits the testing evidence available for later behavioral preservation unless additional executable tests are added in Part 2.

### 10. Baseline execution remains unverified

I have **not** claimed that the application currently boots or that `rspec` passes. Those remain execution tasks to be performed in the controlled environment.

---

## Baseline record to carry forward

```text
repository:
  owner: andrewdsilva
  name: rails-room-booking
  url: https://github.com/andrewdsilva/rails-room-booking

source_version:
  id: original
  commit: 5e15551ee646871b4bed32c982fa17da319d3ee3
  branch_at_selection: main
  commit_date: 2023-07-16T04:45:38Z

environment:
  ruby: 2.7.5p203
  rails: 7.0.6
  bundler: 2.4.17
  database: PostgreSQL
  web_server: Puma 5.6.6
  test_framework: RSpec Rails 6.0.3

execution:
  application_command: rails s
  database_setup:
    - rails db:create
    - rails db:migrate
    - rails db:seed
  test_command: rspec
  execution_status: not_run
```

This baseline is now suitable as the anchor for subsequent Part 1 source inspection and later `Change1`, `Change2`, and `Change3` evolution tracking. The faculty template specifically requires the original source URL, exact baseline commit, environment, inspected scope, architecture, and actual run/test result in the application baseline section.