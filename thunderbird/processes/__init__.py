from .wps_generate_climos import GenerateClimos
from .wps_generate_prsn import GeneratePrsn
from .wps_say_hello import SayHello
from .wps_update_metadata import UpdateMetadata
from .wps_split_merged_climos import SplitMergedClimos

processes = [
    GenerateClimos(),
    GeneratePrsn(),
    UpdateMetadata(),
    SplitMergedClimos(),
    SayHello(),
]
