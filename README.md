# Manoel Pessoa Lima Junior
## Decisões de Arquitetura
### Produtos (Google Cloud Plataform)
- #### Storage
> Optei pelo Storage pela facilidade de criação dos buckets, tanto via console, quanto via API para armazenamento dos arquivos CSVs do teste.
- #### Dataflow
> Optei pelo Dataflow, pois via linha de comando montei um job, que executa um arquivo Python responsável pela leitura dos arquivos *.csv e importação para o BigQuery, criando uma tabela para cada arquivo.
- #### BigQuery
> Optei pelo BigQuery pela eficência das consultas e a possiblidade de integração com o Data Studio.
- #### Data Studio
> Optei pelo Data Studio, pela facilidade na organização das métricas recolhidas.

## Implementação
### Criar o projeto
- NEW PROJECT: Teste Boa Vista (teste-boa-vista)
![new project](https://manupljr.com.br/teste-eng-dados/img/new_project.png "New Project")
### Criar o bucket
- Acessar o produto Storage > Browser na GCP:
- CREATE BUCKET:
- Name your bucket: boavista_teste
- Choose where to store your data:
    - Location type: Region
    - Location: us-central1 (Iowa)
- Choose a default storage class for your data: Standard
- Choose how to control access to objects:
    - Access control: Fine-grained
- Advanced settings (optional): 
    - Encryption: Google-managed key
- CREATE
![create bucket](https://manupljr.com.br/teste-eng-dados/img/create_bucket.png "Create bucket")
### Criar diretórios no bucket
- Create Folder
    - Name: csvs
    - Name: teste_bv_staging
    - Name: teste_bv_temp
![create folder](https://manupljr.com.br/teste-eng-dados/img/create_folder.png "Create folder")
- Subir arquivos *.csv (bill_of_materials.csv, comp_boss.csv e price_quote.csv) para Buckets > boavista_teste > csvs
### Criar a Service Account
- Acessar o recurso IAM & Admin > Service Accounts:
- CREATE SERVICE ACCOUNT:
    - Service account name: teste-boa-vista
    - CREATE
- Service account permissions (optional):
    - App Engine flexible environment Service Agent
    - BigQuery Admin
    - Cloud Asset Service Agent
    - Composer Administrator
    - Environment and Storage Object Administrator
    - Compute Admin
    - Dataflow Admin
    - Dataflow Developer
    - Cloud Dataflow Service Agent
    - Dataflow Viewer
    - Dataflow Worker
    - Workflows Invoker
    - CONTINUE
- Grant users access to this service account (optional):
    - DONE
### Gerar a chave:
- Actions > Create key:
    - Key type: JSON (Salvar o arquivo gerado)
![service account](https://manupljr.com.br/teste-eng-dados/img/service_account.png "Service Account")
### Big Query:
- Criar o dataset "maquinas_industriais_data":
    - Dataset ID: maquinas_industriais_data
    - Data location: Default
    - Default table expiration: Never
    - Encryption: Google-managed key
    - Create Dataset
![big query](https://manupljr.com.br/teste-eng-dados/img/bigquery.png "Big Query")

### Cloud Shell:
```sh
$ mkdir teste-boa-vista
$ cd teste-boa-vista/
```
Subir o json da service account para esse diretório

Subir os arquivos abaixo para a pasta criada do teste:
Obs.: Ajustar a variável **os.environ['GOOGLE_APPLICATION_CREDENTIALS']**, com o caminho exato da service account criada anteriormente.
#### Arquivo: load-bills.py
```sh
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


```
#### Arquivo: load-comp-boss.py
```sh
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
```
#### Arquivo: load-price-quote.py
```sh
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
            zip(('tube_assembly_id','supplier','quote_date','annual_usage','min_order_quantity','bracket_pricing','quantity','cost'),
                values))
        return row


def run(argv=None):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to read. This can be a local file or '
        'a file in a Google Storage Bucket.',
        default='gs://boavista_teste/csvs/price_quote.csv')

    parser.add_argument('--output',
                        dest='output',
                        required=False,
                        help='Output BQ table to write results to.',
                        default='teste-boa-vista:maquinas_industriais_data.price_quote')

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

             schema='tube_assembly_id:STRING,supplier:STRING,quote_date:DATE,annual_usage:INTEGER,min_order_quantity:INTEGER,bracket_pricing:STRING,quantity:FLOAT,cost:FLOAT',

             create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
             
             write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE)))
    p.run().wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
```
Como sudo executar (Configurações do python virtualenv e do apache-beam):
```sh
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install 'apache-beam[gcp]'
```
Executando os jobs que farão o import dos dados do csv para as tabelas no BigQuery, utilizando o Dataflow. Para tanto, basta executar os comandos abaixo:
Arquivo bill_of_materials.csv:
```sh
$ python load-bills.py \
--project=teste-boa-vista \
--runner=DataflowRunner \
--staging_location=gs://boavista_teste/teste_bv_staging \
--temp_location=gs://boavista_teste/teste_bv_temp \
--input='gs://boavista_teste/csvs/bill_of_materials.csv' \
--region=us-central1 \
--save_main_session
```
Arquivo comp_boss.csv:
```sh
$ python load-comp-boss.py \
--project=teste-boa-vista \
--runner=DataflowRunner \
--staging_location=gs://boavista_teste/teste_bv_staging \
--temp_location=gs://boavista_teste/teste_bv_temp \
--input='gs://boavista_teste/csvs/comp_boss.csv' \
--region=us-central1 \
--save_main_session
```
Arquivo price_quote.csv:
```sh
$ python load-price-quote.py \
--project=teste-boa-vista \
--runner=DataflowRunner \
--staging_location=gs://boavista_teste/teste_bv_staging \
--temp_location=gs://boavista_teste/teste_bv_temp \
--input='gs://boavista_teste/csvs/price_quote.csv' \
--region=us-central1 \
--save_main_session
```
### Dataflow
![jobs dataflow](https://manupljr.com.br/teste-eng-dados/img/jobs_dataflow.png "Jobs Dataflow")

### Tabelas criadas e populadas no BigQuery
![tabelas bigquery](https://manupljr.com.br/teste-eng-dados/img/tabelas_bigquery.png "Tabelas criadas no BigQuery")

### Relatório Data Studio
Montei o relatórop com um totalizador de registros, a tabela com os dados, um gráfico pizza das ocorrências "Yes" e "No" do campo bracket_pricing e dois gráficos de barras, sendo um totalizando os custos e outro totalizando ocorrencias da dimensão tuble_assembly_id. Inclui um filtro por bracket_pricing e também por range de data que uriliza o campo quote_date. Por fim, editei para as cores verdes.
![relatorio](https://manupljr.com.br/teste-eng-dados/img/relatorio.png "Relatório Data Studio")

### Modelagem conceitual dos Dados
![modelagem](https://manupljr.com.br/teste-eng-dados/img/modelo_conceitual_dados.png "Modelagem conceitual dos Dados")