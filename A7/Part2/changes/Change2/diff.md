# Change2: room upgrade and active-reservation availability

The machine-applicable diff is `diff.patch`, from `Part2/checkpoints/Change1/` to `Part2/checkpoints/Change2/`. This is a reconstructed review stage. It introduces `Booking.active` together with its uses in Booking availability validation and Room#booked_dates. Canceled reservations already exist in the baseline schema. Change2 needs no Change3 policy classes or refund migration. This resolves the previously documented later-stage dependency. Consult fresh stage receipts for execution results.

+ app/services/room_upgrade.rb
+ db/migrate/20261004171000_add_room_upgrade_fields_to_bookings.rb

The algorithm locks the target room and booking, checks active reservations, computes the pre-VAT room-price delta and saves recalculated totals. Booking belongs_to :upgraded_from_room; repeated upgrades preserve the first original room. Validation failure restores persisted state. Optional services remain attached. Eight database-backed examples cover successful/rejected upgrades, adjacent dates, canceled reservations, services, repeated upgrades, rollback and canceled bookings.
