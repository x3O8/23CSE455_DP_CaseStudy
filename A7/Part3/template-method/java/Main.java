abstract class ResourceTemplate {
    protected abstract String resourceName();
    protected abstract String formName();
    public String renderForm() { return resourceName() + " form: " + formName(); }
}
class BookingResource extends ResourceTemplate { protected String resourceName(){return "Booking";} protected String formName(){return "reservation";} }
class RoomResource extends ResourceTemplate { protected String resourceName(){return "Room";} protected String formName(){return "room";} }
class SettingsResource extends ResourceTemplate { protected String resourceName(){return "Settings";} protected String formName(){return "settings";} }
public class Main { public static void main(String[] args){ System.out.println(new BookingResource().renderForm()); System.out.println(new RoomResource().renderForm()); System.out.println(new SettingsResource().renderForm()); }}
