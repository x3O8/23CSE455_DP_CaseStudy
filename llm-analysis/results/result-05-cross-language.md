1. Common reference design

The Part 3 implementation is a **compact cross-language demonstration derived from the verified baseline and Part 2 proposal**. It is not presented as a modification to the original Rails repository.

### Language-neutral design

```text
                              ┌──────────────────────┐
                              │        Booking       │
                              └──────────┬───────────┘
                                         │
                   ┌─────────────────────┼─────────────────────┐
                   │                     │                     │
                   ▼                     ▼                     ▼
                Room              BookingService*       RoomUpgrade
                                         │
                                         ▼
                                  AdditionalService
                                   /               \
                                  /                 \
                                 ▼                   ▼
                     BreakfastPackage       AirportTransfer


Booking cancellation
        │
        ▼
CancellationService
        │
        ▼
CancellationPolicy
   /          |           \
  ▼           ▼            ▼
Flexible   Partial      NoRefund
```

The original Rails Template Method intent is:

```text
CrudConcern
     │
     ▼
shared CRUD workflow
     │
     ├── resource-specific hooks
     ▼
BookingsController
RoomsController
SettingsController
```

The cross-language implementations preserve that **design intent**, but use language-appropriate mechanisms rather than mechanically reproducing Ruby's `ActiveSupport::Concern`.

The common pricing model is:

```text
booking total
= room stay total
+ selected additional-service totals
```

Room upgrade contributes the target-room price difference over the booking stay.

Cancellation is:

```text
CancellationService
        ↓
CancellationPolicy
        ↓
selected cancellation algorithm
```

The implementations use three concrete policies plus a fourth demonstration policy to prove that the cancellation workflow is open to another policy without modifying `CancellationService`.

---

2. Java implementation

### Source: `java/Main.java`

The Java version uses:

- interfaces for `AdditionalService` and `CancellationPolicy`
- an abstract class for the Template Method workflow
- normal Java inheritance for concrete controllers and policies
- `List<BookingService>` for optional services

```java
import java.util.ArrayList;
import java.util.List;

class Room {
    final String name;
    final double nightlyRate;
    boolean available;

    Room(String name, double nightlyRate, boolean available) {
        this.name = name;
        this.nightlyRate = nightlyRate;
        this.available = available;
    }
}

interface AdditionalService {
    String name();
    double priceFor(Booking booking);
}

class BreakfastPackage implements AdditionalService {
    private final String packageName;
    private final double pricePerGuestPerNight;

    BreakfastPackage(String packageName, double pricePerGuestPerNight) {
        this.packageName = packageName;
        this.pricePerGuestPerNight = pricePerGuestPerNight;
    }

    public String name() { return packageName; }

    public double priceFor(Booking booking) {
        return pricePerGuestPerNight * booking.guests * booking.nights();
    }
}

class AirportTransfer implements AdditionalService {
    private final String transferType;
    private final double price;

    AirportTransfer(String transferType, double price) {
        this.transferType = transferType;
        this.price = price;
    }

    public String name() { return transferType; }

    public double priceFor(Booking booking) { return price; }
}

class BookingService {
    final AdditionalService service;
    final int quantity;

    BookingService(AdditionalService service, int quantity) {
        this.service = service;
        this.quantity = quantity;
    }

    double totalFor(Booking booking) {
        return service.priceFor(booking) * quantity;
    }
}

class RoomUpgrade {
    private final Room targetRoom;

    RoomUpgrade(Room targetRoom) {
        this.targetRoom = targetRoom;
    }

    boolean availableFor(Booking booking) {
        return targetRoom.available;
    }

    double priceDifference(Booking booking) {
        return (targetRoom.nightlyRate - booking.room.nightlyRate) * booking.nights();
    }

    void apply(Booking booking) {
        if (!availableFor(booking)) {
            throw new IllegalStateException("Target room unavailable");
        }
        booking.room = targetRoom;
    }
}

class Booking {
    Room room;
    final int nights;
    final int guests;
    final List<BookingService> services = new ArrayList<>();
    double recordedRefund;
    boolean cancelled;

    Booking(Room room, int nights, int guests) {
        this.room = room;
        this.nights = nights;
        this.guests = guests;
    }

    int nights() {
        return nights;
    }

    void addService(AdditionalService service, int quantity) {
        services.add(new BookingService(service, quantity));
    }

    double total() {
        double total = room.nightlyRate * nights;
        for (BookingService service : services) {
            total += service.totalFor(this);
        }
        return total;
    }
}

interface CancellationPolicy {
    boolean canCancel(Booking booking, int daysBeforeStay);
    double refundAmount(Booking booking, int daysBeforeStay);
}

class FlexibleCancellationPolicy implements CancellationPolicy {
    public boolean canCancel(Booking booking, int daysBeforeStay) {
        return true;
    }

    public double refundAmount(Booking booking, int daysBeforeStay) {
        return booking.total();
    }
}

class PartialRefundCancellationPolicy implements CancellationPolicy {
    public boolean canCancel(Booking booking, int daysBeforeStay) {
        return true;
    }

    public double refundAmount(Booking booking, int daysBeforeStay) {
        return booking.total() * 0.5;
    }
}

class NoRefundCancellationPolicy implements CancellationPolicy {
    public boolean canCancel(Booking booking, int daysBeforeStay) {
        return true;
    }

    public double refundAmount(Booking booking, int daysBeforeStay) {
        return 0.0;
    }
}

class CancellationService {
    private final CancellationPolicy policy;

    CancellationService(CancellationPolicy policy) {
        this.policy = policy;
    }

    double cancel(Booking booking, int daysBeforeStay) {
        if (!policy.canCancel(booking, daysBeforeStay)) {
            throw new IllegalStateException("Cancellation not allowed");
        }

        double refund = policy.refundAmount(booking, daysBeforeStay);
        booking.recordedRefund = refund;
        booking.cancelled = true;
        return refund;
    }
}

abstract class CrudWorkflow {
    final String createResource() {
        beforeCreate();
        String result = buildResource();
        afterCreate(result);
        return result;
    }

    protected void beforeCreate() {}
    protected abstract String buildResource();
    protected void afterCreate(String resource) {}
}

class BookingController extends CrudWorkflow {
    protected String buildResource() {
        return "Booking resource: reservation form";
    }

    protected void afterCreate(String resource) {
        System.out.println(resource + " created");
    }
}

class RoomController extends CrudWorkflow {
    protected String buildResource() {
        return "Room resource: room form";
    }
}

class SettingsController extends CrudWorkflow {
    protected String buildResource() {
        return "Settings resource: settings form";
    }
}

public class Main {
    public static void main(String[] args) {
        Room standard = new Room("Standard", 100, true);
        Room deluxe = new Room("Deluxe", 150, true);

        Booking booking = new Booking(standard, 3, 2);
        System.out.printf("Basic booking total: %.2f%n", booking.total());

        booking.addService(new BreakfastPackage("Breakfast", 15), 1);
        System.out.printf("With breakfast: %.2f%n", booking.total());

        booking.addService(new AirportTransfer("Airport transfer", 40), 1);
        System.out.printf("With transfer: %.2f%n", booking.total());

        double beforeUpgrade = booking.total();
        RoomUpgrade upgrade = new RoomUpgrade(deluxe);

        System.out.printf(
            "Room upgrade difference: %.2f%n",
            upgrade.priceDifference(booking)
        );

        upgrade.apply(booking);

        System.out.printf("After room upgrade: %.2f%n", booking.total());
        System.out.printf(
            "Upgrade delta in total: %.2f%n",
            booking.total() - beforeUpgrade
        );

        Booking flexibleBooking = new Booking(standard, 3, 2);
        flexibleBooking.addService(
            new BreakfastPackage("Breakfast", 15), 1
        );
        flexibleBooking.addService(
            new AirportTransfer("Airport transfer", 40), 1
        );

        System.out.printf(
            "Flexible refund: %.2f%n",
            new CancellationService(
                new FlexibleCancellationPolicy()
            ).cancel(flexibleBooking, 10)
        );

        System.out.printf(
            "Partial refund: %.2f%n",
            new CancellationService(
                new PartialRefundCancellationPolicy()
            ).cancel(flexibleBooking, 2)
        );

        System.out.printf(
            "No refund: %.2f%n",
            new CancellationService(
                new NoRefundCancellationPolicy()
            ).cancel(flexibleBooking, 0)
        );

        class WeatherClosurePolicy implements CancellationPolicy {
            public boolean canCancel(Booking b, int daysBeforeStay) {
                return true;
            }

            public double refundAmount(Booking b, int daysBeforeStay) {
                return b.total() * 0.75;
            }
        }

        System.out.printf(
            "New 75%% policy refund: %.2f%n",
            new CancellationService(
                new WeatherClosurePolicy()
            ).cancel(new Booking(standard, 2, 1), 1)
        );

        System.out.println(
            new BookingController().createResource()
        );
        System.out.println(
            new RoomController().createResource()
        );
        System.out.println(
            new SettingsController().createResource()
        );
    }
}
```

### Java pattern roles

**Strategy**

```text
CancellationService
        │
        ▼
CancellationPolicy
   ├── FlexibleCancellationPolicy
   ├── PartialRefundCancellationPolicy
   └── NoRefundCancellationPolicy
```

The actual delegation occurs in `CancellationService.cancel()` through:

```java
policy.canCancel(...)
policy.refundAmount(...)
```

**Template Method**

`CrudWorkflow.createResource()` fixes the algorithm:

```text
beforeCreate
→ buildResource
→ afterCreate
```

while subclasses implement/override the extension points.

---

3. Python implementation

### Source: `python/main.py`

The Python implementation intentionally avoids Java-style interface boilerplate. It uses `abc.ABC` where an explicit contract is useful and normal Python polymorphism for the concrete strategies.

```python
from abc import ABC, abstractmethod


class Room:
    def __init__(self, name, nightly_rate, available=True):
        self.name = name
        self.nightly_rate = nightly_rate
        self.available = available


class AdditionalService(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def price_for(self, booking):
        pass


class BreakfastPackage(AdditionalService):
    def __init__(self, package_name, price_per_guest_per_night):
        self.package_name = package_name
        self.price_per_guest_per_night = price_per_guest_per_night

    def name(self):
        return self.package_name

    def price_for(self, booking):
        return (
            self.price_per_guest_per_night
            * booking.guests
            * booking.nights
        )


class AirportTransfer(AdditionalService):
    def __init__(self, transfer_type, price):
        self.transfer_type = transfer_type
        self.price = price

    def name(self):
        return self.transfer_type

    def price_for(self, booking):
        return self.price


class BookingService:
    def __init__(self, service, quantity=1):
        self.service = service
        self.quantity = quantity

    def total_for(self, booking):
        return self.service.price_for(booking) * self.quantity


class RoomUpgrade:
    def __init__(self, target_room):
        self.target_room = target_room

    def price_difference(self, booking):
        return (
            self.target_room.nightly_rate
            - booking.room.nightly_rate
        ) * booking.nights

    def apply(self, booking):
        if not self.target_room.available:
            raise ValueError("Target room unavailable")
        booking.room = self.target_room


class Booking:
    def __init__(self, room, nights, guests):
        self.room = room
        self.nights = nights
        self.guests = guests
        self.services = []
        self.cancelled = False
        self.recorded_refund = 0.0

    def add_service(self, service, quantity=1):
        self.services.append(
            BookingService(service, quantity)
        )

    def total(self):
        return (
            self.room.nightly_rate * self.nights
            + sum(
                item.total_for(self)
                for item in self.services
            )
        )


class CancellationPolicy(ABC):
    @abstractmethod
    def can_cancel(self, booking, days_before_stay):
        pass

    @abstractmethod
    def refund_amount(self, booking, days_before_stay):
        pass


class FlexibleCancellationPolicy(CancellationPolicy):
    def can_cancel(self, booking, days_before_stay):
        return True

    def refund_amount(self, booking, days_before_stay):
        return booking.total()


class PartialRefundCancellationPolicy(CancellationPolicy):
    def can_cancel(self, booking, days_before_stay):
        return True

    def refund_amount(self, booking, days_before_stay):
        return booking.total() * 0.5


class NoRefundCancellationPolicy(CancellationPolicy):
    def can_cancel(self, booking, days_before_stay):
        return True

    def refund_amount(self, booking, days_before_stay):
        return 0.0


class CancellationService:
    def __init__(self, policy):
        self.policy = policy

    def cancel(self, booking, days_before_stay):
        if not self.policy.can_cancel(
            booking,
            days_before_stay
        ):
            raise ValueError("Cancellation not allowed")

        refund = self.policy.refund_amount(
            booking,
            days_before_stay
        )
        booking.recorded_refund = refund
        booking.cancelled = True
        return refund


class CrudWorkflow(ABC):
    def create_resource(self):
        self.before_create()
        resource = self.build_resource()
        self.after_create(resource)
        return resource

    def before_create(self):
        pass

    @abstractmethod
    def build_resource(self):
        pass

    def after_create(self, resource):
        pass


class BookingController(CrudWorkflow):
    def build_resource(self):
        return "Booking resource: reservation form"

    def after_create(self, resource):
        print(resource + " created")


class RoomController(CrudWorkflow):
    def build_resource(self):
        return "Room resource: room form"


class SettingsController(CrudWorkflow):
    def build_resource(self):
        return "Settings resource: settings form"


class WeatherClosurePolicy(CancellationPolicy):
    def can_cancel(self, booking, days_before_stay):
        return True

    def refund_amount(self, booking, days_before_stay):
        return booking.total() * 0.75


def main():
    standard = Room("Standard", 100)
    deluxe = Room("Deluxe", 150)

    booking = Booking(standard, 3, 2)
    print(f"Basic booking total: {booking.total():.2f}")

    booking.add_service(
        BreakfastPackage("Breakfast", 15)
    )
    print(f"With breakfast: {booking.total():.2f}")

    booking.add_service(
        AirportTransfer("Airport transfer", 40)
    )
    print(f"With transfer: {booking.total():.2f}")

    before_upgrade = booking.total()
    upgrade = RoomUpgrade(deluxe)

    print(
        f"Room upgrade difference: "
        f"{upgrade.price_difference(booking):.2f}"
    )

    upgrade.apply(booking)

    print(f"After room upgrade: {booking.total():.2f}")
    print(
        f"Upgrade delta in total: "
        f"{booking.total() - before_upgrade:.2f}"
    )

    flexible_booking = Booking(standard, 3, 2)
    flexible_booking.add_service(
        BreakfastPackage("Breakfast", 15)
    )
    flexible_booking.add_service(
        AirportTransfer("Airport transfer", 40)
    )

    print(
        f"Flexible refund: "
        f"{CancellationService(FlexibleCancellationPolicy()).cancel(flexible_booking, 10):.2f}"
    )

    print(
        f"Partial refund: "
        f"{CancellationService(PartialRefundCancellationPolicy()).cancel(flexible_booking, 2):.2f}"
    )

    print(
        f"No refund: "
        f"{CancellationService(NoRefundCancellationPolicy()).cancel(flexible_booking, 0):.2f}"
    )

    print(
        f"New 75% policy refund: "
        f"{CancellationService(WeatherClosurePolicy()).cancel(Booking(standard, 2, 1), 1):.2f}"
    )

    print(BookingController().create_resource())
    print(RoomController().create_resource())
    print(SettingsController().create_resource())


if __name__ == "__main__":
    main()
```

### Python-specific design difference

Python does not need the Java-style declaration of a formal interface for every polymorphic relationship. `ABC` is used where an explicit contract helps communicate the Strategy and service abstractions.

---

4. JavaScript implementation

### Source: `javascript/main.js`

The JavaScript implementation uses ES6 classes. JavaScript's structural/dynamic nature means the “interfaces” are represented by base classes whose methods establish the expected protocol.

```javascript
class Room {
    constructor(name, nightlyRate, available = true) {
        this.name = name;
        this.nightlyRate = nightlyRate;
        this.available = available;
    }
}

class AdditionalService {
    getName() {
        throw new Error("getName must be implemented");
    }

    priceFor() {
        throw new Error("priceFor must be implemented");
    }
}

class BreakfastPackage extends AdditionalService {
    constructor(packageName, pricePerGuestPerNight) {
        super();
        this.packageName = packageName;
        this.pricePerGuestPerNight = pricePerGuestPerNight;
    }

    getName() {
        return this.packageName;
    }

    priceFor(booking) {
        return (
            this.pricePerGuestPerNight
            * booking.guests
            * booking.nights
        );
    }
}

class AirportTransfer extends AdditionalService {
    constructor(transferType, price) {
        super();
        this.transferType = transferType;
        this.price = price;
    }

    getName() {
        return this.transferType;
    }

    priceFor() {
        return this.price;
    }
}

class BookingService {
    constructor(service, quantity = 1) {
        this.service = service;
        this.quantity = quantity;
    }

    totalFor(booking) {
        return this.service.priceFor(booking) * this.quantity;
    }
}

class Booking {
    constructor(room, nights, guests) {
        this.room = room;
        this.nights = nights;
        this.guests = guests;
        this.services = [];
        this.cancelled = false;
        this.recordedRefund = 0;
    }

    addService(service, quantity = 1) {
        this.services.push(
            new BookingService(service, quantity)
        );
    }

    total() {
        return (
            this.room.nightlyRate * this.nights
            + this.services.reduce(
                (sum, item) => sum + item.totalFor(this),
                0
            )
        );
    }
}

class RoomUpgrade {
    constructor(targetRoom) {
        this.targetRoom = targetRoom;
    }

    priceDifference(booking) {
        return (
            this.targetRoom.nightlyRate
            - booking.room.nightlyRate
        ) * booking.nights;
    }

    apply(booking) {
        if (!this.targetRoom.available) {
            throw new Error("Target room unavailable");
        }
        booking.room = this.targetRoom;
    }
}

class CancellationPolicy {
    canCancel() {
        throw new Error("canCancel must be implemented");
    }

    refundAmount() {
        throw new Error("refundAmount must be implemented");
    }
}

class FlexibleCancellationPolicy extends CancellationPolicy {
    canCancel() {
        return true;
    }

    refundAmount(booking) {
        return booking.total();
    }
}

class PartialRefundCancellationPolicy extends CancellationPolicy {
    canCancel() {
        return true;
    }

    refundAmount(booking) {
        return booking.total() * 0.5;
    }
}

class NoRefundCancellationPolicy extends CancellationPolicy {
    canCancel() {
        return true;
    }

    refundAmount() {
        return 0;
    }
}

class CancellationService {
    constructor(policy) {
        this.policy = policy;
    }

    cancel(booking, daysBeforeStay) {
        if (!this.policy.canCancel(
            booking,
            daysBeforeStay
        )) {
            throw new Error("Cancellation not allowed");
        }

        const refund = this.policy.refundAmount(
            booking,
            daysBeforeStay
        );

        booking.recordedRefund = refund;
        booking.cancelled = true;

        return refund;
    }
}

class CrudWorkflow {
    createResource() {
        this.beforeCreate();
        const resource = this.buildResource();
        this.afterCreate(resource);
        return resource;
    }

    beforeCreate() {}

    buildResource() {
        throw new Error("buildResource must be implemented");
    }

    afterCreate() {}
}

class BookingController extends CrudWorkflow {
    buildResource() {
        return "Booking resource: reservation form";
    }

    afterCreate(resource) {
        console.log(resource + " created");
    }
}

class RoomController extends CrudWorkflow {
    buildResource() {
        return "Room resource: room form";
    }
}

class SettingsController extends CrudWorkflow {
    buildResource() {
        return "Settings resource: settings form";
    }
}

class WeatherClosurePolicy extends CancellationPolicy {
    canCancel() {
        return true;
    }

    refundAmount(booking) {
        return booking.total() * 0.75;
    }
}

function main() {
    const standard = new Room("Standard", 100);
    const deluxe = new Room("Deluxe", 150);

    const booking = new Booking(standard, 3, 2);
    console.log(
        `Basic booking total: ${booking.total().toFixed(2)}`
    );

    booking.addService(
        new BreakfastPackage("Breakfast", 15)
    );
    console.log(
        `With breakfast: ${booking.total().toFixed(2)}`
    );

    booking.addService(
        new AirportTransfer("Airport transfer", 40)
    );
    console.log(
        `With transfer: ${booking.total().toFixed(2)}`
    );

    const beforeUpgrade = booking.total();
    const upgrade = new RoomUpgrade(deluxe);

    console.log(
        `Room upgrade difference: ${upgrade.priceDifference(booking).toFixed(2)}`
    );

    upgrade.apply(booking);

    console.log(
        `After room upgrade: ${booking.total().toFixed(2)}`
    );

    console.log(
        `Upgrade delta in total: ${(booking.total() - beforeUpgrade).toFixed(2)}`
    );

    const flexibleBooking = new Booking(standard, 3, 2);

    flexibleBooking.addService(
        new BreakfastPackage("Breakfast", 15)
    );

    flexibleBooking.addService(
        new AirportTransfer("Airport transfer", 40)
    );

    console.log(
        `Flexible refund: ${new CancellationService(
            new FlexibleCancellationPolicy()
        ).cancel(flexibleBooking, 10).toFixed(2)}`
    );

    console.log(
        `Partial refund: ${new CancellationService(
            new PartialRefundCancellationPolicy()
        ).cancel(flexibleBooking, 2).toFixed(2)}`
    );

    console.log(
        `No refund: ${new CancellationService(
            new NoRefundCancellationPolicy()
        ).cancel(flexibleBooking, 0).toFixed(2)}`
    );

    console.log(