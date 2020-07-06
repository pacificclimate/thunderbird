from .wps_generate_climos import GenerateClimos
from .wps_generate_prsn import GeneratePrsn
from .wps_decompose_flow_vectors import DecomposeFlowVectors
from .wps_update_metadata import UpdateMetadata
from .wps_split_merged_climos import SplitMergedClimos

processes = [
    GenerateClimos(),
    GeneratePrsn(),
    UpdateMetadata(),
    SplitMergedClimos(),
    DecomposeFlowVectors(),
]
