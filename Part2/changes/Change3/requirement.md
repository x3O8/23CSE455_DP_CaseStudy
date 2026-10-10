Requirement
Support multiple cancellation/refund rules without embedding policy-specific branching in Booking.

Acceptance criteria
1. CancellationService accepts a CancellationPolicy abstraction.
2. Flexible policy returns 100% of the booking amount.
3. Partial policy returns its configured fraction.
4. No-refund policy returns zero.
5. CancellationService delegates the calculation polymorphically and then cancels the booking.
6. The Rails cancellation action authenticates and authorizes the user and selects the policy from server configuration.
7. Cancellation persists the calculated refund and timestamp atomically; repeat cancellation cannot replace the original record.
8. Canceled reservations release availability. No external Stripe transfer is claimed.
