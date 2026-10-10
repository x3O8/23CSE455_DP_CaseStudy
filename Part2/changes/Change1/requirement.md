Requirement
Add optional breakfast and airport transfer services without adding service-specific branches to Booking.

Acceptance criteria
1. Breakfast and airport transfer are represented by the AdditionalService abstraction.
2. BookingService persists service selection, quantity and captured unit price.
3. Additional service totals can be calculated independently of Booking controller code.
4. The migration creates the booking_services table with a booking foreign key.
5. Booking totals and pending payment amounts refresh when selections change; paid payment amounts remain unchanged.

Before
Baseline commit 5e15551: Booking has room/user/date/price responsibilities and no booking_services association.

After
This submission snapshot: Part2/code adds AdditionalService, BreakfastPackage, AirportTransfer, BookingService and pricing service.
