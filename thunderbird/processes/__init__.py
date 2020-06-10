from .wps_generate_climos import GenerateClimos
from .wps_say_hello import SayHello
from .wps_decompose_flow_vectors import DecomposeFlowVectors

processes = [
    GenerateClimos(),
    SayHello(),
    DecomposeFlowVectors(),
]
