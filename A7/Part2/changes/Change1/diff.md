# Change1: additional services

The machine-applicable diff is `diff.patch`, from `Part2/checkpoints/original/` to `Part2/checkpoints/Change1/`. This is a reconstructed review stage, not a historical commit. Bundle/platform and eager-loading support are assigned to this first runnable evolved stage. The copied provenance note is removed from evolved checkpoints; baseline provenance remains retained. Test counts below describe the feature specification; consult fresh stage receipts for executed results.

+ app/models/additional_service.rb
+ app/models/breakfast_package.rb
+ app/models/airport_transfer.rb
+ app/models/booking_service.rb
+ app/services/additional_service_pricing.rb
+ db/migrate/20261004170000_create_booking_services.rb
+ Booking has_many :booking_services, dependent: :destroy
+ Booking#add_service captures service type, unit price and quantity.
+ Booking#compute_price_ht adds optional services to the room subtotal.
+ BookingService save/destroy callbacks recalculate booking totals under a lock.
+ HasPriceConcern refreshes totals on save; pending payments retain their identity and get the new amount, while paid amounts remain unchanged.
+ spec/services/additional_service_pricing_spec.rb: seven database-backed examples.

Refactoring effect: optional-service pricing is introduced as a separate domain/service responsibility. The retained baseline controllers did not contain optional-service pricing branches; this is responsibility separation for new functionality, not removal of existing controller logic.
