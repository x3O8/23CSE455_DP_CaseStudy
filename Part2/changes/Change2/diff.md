Change 2 diff summary

+ app/services/room_upgrade.rb
+ db/migrate/20261004171000_add_room_upgrade_fields_to_bookings.rb

The algorithm locks the target room and booking, checks active reservations, computes the pre-VAT room-price delta and saves recalculated totals. Booking belongs_to :upgraded_from_room; repeated upgrades preserve the first original room. Validation failure restores persisted state. Optional services remain attached. Eight database-backed examples cover successful/rejected upgrades, adjacent dates, canceled reservations, services, repeated upgrades, rollback and canceled bookings.
