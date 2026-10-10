Requirement
Allow a confirmed booking to move to an available target room, recalculate the room-price difference, validate date availability and persist the change.

Acceptance criteria
1. The target room is rejected when an overlapping booking exists.
2. The original room remains unchanged on rejection.
3. A free target room is assigned on success.
4. The price difference is based on nightly price and booking nights.
5. Booking totals are recalculated and saved.
6. Canceled reservations do not block availability; canceled bookings cannot be upgraded.
7. Services survive upgrades, invalid changes roll back, and repeated upgrades retain the first original room in upgraded_from_room.

Checkpoint boundary
Part2/checkpoints/Change2 is cumulative after Change1. Booking.active and canceled-reservation availability filtering are introduced here, since RoomUpgrade already depends on them. The baseline canceled_at column and cancel! method are sufficient; no Change3 refund-policy classes or migration are required. Here, confirmed means a persisted reservation; the implementation does not require a paid payment or record external upgrade payments.
