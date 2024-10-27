from src.adapters.repository import JsonUIDMappingRepository
from src.adapters.rfid_interface import TagRegister
from src.rfid.mfrc import MFRCModule

output_file = "tmp/out.json"
registry = JsonUIDMappingRepository(output_file)
rfid_module = MFRCModule()
tag_registry = TagRegister(registry, rfid_module)
while True:
    tag_registry.register()
