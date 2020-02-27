from pywps import Process, LiteralOutput, LiteralInput
from pywps.app.Common import Metadata


class GenerateClimos(Process):
    def __init__(self):
        inputs = []
        outputs = [LiteralOutput('answer', 'Answer to Ultimate Question', data_type='string')]

        super(GenerateClimos, self).__init__(
            self._handler,
            identifier='generate_climos',
            version='0.5.0',
            title='Generate Climatological Means',
            abstract='Generate files containing climatological means from input files of daily, monthly, or yearly data that adhere to the PCIC metadata standard (and consequently to CMIP5 and CF standards).',
            metadata=[Metadata('Ultimate Question'), Metadata('What is the meaning of life')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    @staticmethod
    def _handler(request, response):
        response.outputs['answer'].data = '41'
        return response
