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
            zip(('component_id','component_type_id','type','connection_type_id','outside_shape','base_type','height_over_tube','bolt_pattern_long','bolt_pattern_wide','groove','base_diameter','shoulder_diameter','unique_feature','orientation','weight'),
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
        default='gs://boavista_teste/csvs/comp_boss.csv')

    parser.add_argument('--output',
                        dest='output',
                        required=False,
                        help='Output BQ table to write results to.',
                        default='teste-boa-vista:maquinas_industriais_data.comp_boss')

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

             schema='component_id:STRING,component_type_id:STRING,type:STRING,connection_type_id:STRING,outside_shape:STRING,base_type:STRING,height_over_tube:FLOAT,bolt_pattern_long:STRING,bolt_pattern_wide:STRING,groove:STRING,base_diameter:STRING,shoulder_diameter:STRING,unique_feature:STRING,orientation:STRING,weight:STRING',

             create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
             
             write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE)))
    p.run().wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()

