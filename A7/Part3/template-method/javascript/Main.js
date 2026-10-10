class ResourceTemplate {
  resourceName(){ throw new Error("abstract"); }
  formName(){ throw new Error("abstract"); }
  renderForm(){ return `${this.resourceName()} form: ${this.formName()}`; }
}
class BookingResource extends ResourceTemplate { resourceName(){return "Booking";} formName(){return "reservation";} }
class RoomResource extends ResourceTemplate { resourceName(){return "Room";} formName(){return "room";} }
class SettingsResource extends ResourceTemplate { resourceName(){return "Settings";} formName(){return "settings";} }
for (const resource of [new BookingResource(),new RoomResource(),new SettingsResource()]) console.log(resource.renderForm());
