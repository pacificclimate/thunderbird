from .wps_generate_climos import GenerateClimos
from .wps_generate_prsn import GeneratePrsn
from .wps_say_hello import SayHello

processes = [
    GenerateClimos(),
    GeneratePrsn(),
    SayHello(),
]
