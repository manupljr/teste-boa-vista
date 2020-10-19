from __future__ import absolute_import
import argparse
import logging
import re
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/manupljr/teste-boa-vista/teste-boa-vista-995ecbbf1ac2.json"

class DataIngestion:


    def parse_method(self, string_input):
        values = re.split(",",
                          re.sub('\r\n', '', re.sub(u'"', '', string_input)))
        row = dict(
            zip(('tube_assembly_id','component_id_1','quantity_1','component_id_2','quantity_2','component_id_3','quantity_3','component_id_4','quantity_4','component_id_5','quantity_5','component_id_6','quantity_6','component_id_7','quantity_7','component_id_8','quantity_8'),
                values))
        return row


def run(argv=None):
    """The main function which creates the pipeline and runs it."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to read. This can be a local file or '
        'a file in a Google Storage Bucket.',
        default='gs://boavista_teste/csvs/bill_of_materials.csv')

    parser.add_argument('--output',
                        dest='output',
                        required=False,
                        help='Output BQ table to write results to.',
                        default='teste-boa-vista:maquinas_industriais_data.bill_of_materials')

    known_args, pipeline_args = parser.parse_known_args(argv)


    data_ingestion = DataIngestion()


    p = beam.Pipeline(options=PipelineOptions(pipeline_args))

    (
     p | 'Read File from GCS' >> beam.io.ReadFromText(known_args.input,
                                                  skip_header_lines=1)
    
     | 'String To BigQuery Row' >>
     beam.Map(lambda s: data_ingestion.parse_method(s))
     | 'Write to BigQuery' >> beam.io.Write(
         beam.io.BigQuerySink(
             known_args.output,

             schema='tube_assembly_id:STRING,component_id_1:STRING,quantity_1:STRING,component_id_2:STRING,quantity_2:STRING,component_id_3:STRING,quantity_3:STRING,component_id_4:STRING,quantity_4:STRING,component_id_5:STRING,quantity_5:STRING,component_id_6:STRING,quantity_6:STRING,component_id_7:STRING,quantity_7:STRING,component_id_8:STRING,quantity_8:STRING',

             create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,

             write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE)))
    p.run().wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()

