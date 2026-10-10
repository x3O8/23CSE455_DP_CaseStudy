# Change3: cancellation refund Strategy

The machine-applicable diff is `diff.patch`, from `Part2/checkpoints/Change2/` to `Part2/checkpoints/Change3/`. The final checkpoint matches `Part2/code/` excluding runtime files. Booking.active and canceled-reservation availability are inherited from Change2. Consult fresh stage receipts for executed results; prose is not a test receipt.

+ app/services/cancellation_policy.rb
+ app/services/flexible_cancellation_policy.rb
+ app/services/partial_refund_cancellation_policy.rb
+ app/services/no_refund_cancellation_policy.rb
+ app/services/cancellation_service.rb
+ config/initializers/cancellation_policy.rb and CANCELLATION_POLICY in .env.dist
+ db/migrate/20261010190000_add_cancellation_refund_amount_to_bookings.rb
+ BookingsController#cancel authenticates, authorizes and calls CancellationService with the server-selected policy.
+ Booking.active and Room#booked_dates inherit Change2's canceled-reservation filtering.
+ CancellationService locks the booking and persists canceled_at and cancellation_refund_amount, rejecting repeats.
+ PartialRefundCancellationPolicy validates the rate and rounds refunds to two decimal places.
+ Nine service examples and six Rails request examples are present; results are recorded in verification receipts.

Pattern effect: newly_introduced Strategy collaboration. The policy abstraction isolates refund rules from the cancellation workflow.
