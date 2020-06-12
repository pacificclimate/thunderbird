from .wps_generate_climos import GenerateClimos
from .wps_say_hello import SayHello
from .wps_update_metadata import UpdateMetadata

processes = [
    GenerateClimos(),
    UpdateMetadata(),
    SayHello(),
]
