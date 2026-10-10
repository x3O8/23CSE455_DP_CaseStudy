Change 1 diff summary

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

Refactoring effect: optional-service pricing is moved away from controller branching into a small domain/service layer.
