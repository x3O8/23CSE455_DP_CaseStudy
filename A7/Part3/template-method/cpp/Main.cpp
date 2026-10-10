#include <iostream>
#include <string>
#include <vector>
using namespace std;
class ResourceTemplate { public: virtual ~ResourceTemplate()=default; virtual string resourceName() const=0; virtual string formName() const=0; string renderForm() const { return resourceName()+" form: "+formName(); } };
class BookingResource: public ResourceTemplate { public:string resourceName()const override{return "Booking";} string formName()const override{return "reservation";} };
class RoomResource: public ResourceTemplate { public:string resourceName()const override{return "Room";} string formName()const override{return "room";} };
class SettingsResource: public ResourceTemplate { public:string resourceName()const override{return "Settings";} string formName()const override{return "settings";} };
int main(){vector<ResourceTemplate*> v={new BookingResource,new RoomResource,new SettingsResource}; for(auto p:v){cout<<p->renderForm()<<"\n"; delete p;}}
