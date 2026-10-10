Change 3 diff summary

+ app/services/cancellation_policy.rb
+ app/services/flexible_cancellation_policy.rb
+ app/services/partial_refund_cancellation_policy.rb
+ app/services/no_refund_cancellation_policy.rb
+ app/services/cancellation_service.rb
+ config/initializers/cancellation_policy.rb and CANCELLATION_POLICY in .env.dist
+ db/migrate/20261010190000_add_cancellation_refund_amount_to_bookings.rb
+ BookingsController#cancel authenticates, authorizes and calls CancellationService with the server-selected policy.
+ Booking.active and Room#booked_dates exclude canceled reservations.
+ CancellationService locks the booking and persists canceled_at and cancellation_refund_amount, rejecting repeats.
+ PartialRefundCancellationPolicy validates the rate and rounds refunds to two decimal places.
+ Nine service examples and six Rails request examples pass.

Pattern effect: newly_introduced Strategy collaboration. The policy abstraction isolates refund rules from the cancellation workflow.
