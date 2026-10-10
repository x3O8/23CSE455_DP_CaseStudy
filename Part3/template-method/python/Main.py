from abc import ABC, abstractmethod

class ResourceTemplate(ABC):
    @abstractmethod
    def resource_name(self): pass
    @abstractmethod
    def form_name(self): pass
    def render_form(self): return f"{self.resource_name()} form: {self.form_name()}"

class BookingResource(ResourceTemplate):
    def resource_name(self): return "Booking"
    def form_name(self): return "reservation"

class RoomResource(ResourceTemplate):
    def resource_name(self): return "Room"
    def form_name(self): return "room"

class SettingsResource(ResourceTemplate):
    def resource_name(self): return "Settings"
    def form_name(self): return "settings"

for resource in [BookingResource(), RoomResource(), SettingsResource()]: print(resource.render_form())
