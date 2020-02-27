from .wps_say_hello import SayHello
from .wps_generate_climos import GenerateClimos

processes = [
    SayHello(),
    GenerateClimos(),
]
