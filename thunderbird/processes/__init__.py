from .wps_generate_climos import GenerateClimos
from .wps_generate_prsn import GeneratePrsn
from .wps_say_hello import SayHello
from .wps_decompose_flow_vectors import DecomposeFlowVectors
from .wps_update_metadata import UpdateMetadata

processes = [
    GenerateClimos(),
    GeneratePrsn(),
    UpdateMetadata(),
    SayHello(),
    DecomposeFlowVectors(),
]
