# Baseline pattern evidence

## Confirmed: Template Method

**Instance:** Shared CRUD Controller Workflow

**Template holder:** `CrudConcern`

**Concrete participants:** `BookingsController`, `RoomsController`, `SettingsController`

**Evidence:** `CrudConcern` contains the common CRUD operations and calls overridable controller hooks including `base_class`, `object_class`, `strong_params`, `model_params`, `use_slug?`, `set_object` and `redirect_to_show`. The concrete controllers implement these hooks differently.

**Verification:** source-level inspection at baseline commit `5e15551ee646871b4bed32c982fa17da319d3ee3`.

## Rejected / uncertain candidates

Pundit policies were not counted as Strategy because the inspected baseline did not establish a single context delegating interchangeable algorithms to a policy abstraction. Active Record callbacks were not counted as Observer because the source does not establish an explicit observer collaboration. Payify was not counted as Adapter or Facade because the dependency internals were not visible. Concerns were not counted as Decorator merely because they are Ruby modules.
