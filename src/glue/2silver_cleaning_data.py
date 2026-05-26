import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality
from awsglue.dynamicframe import DynamicFrame
from awsglue import DynamicFrame
from pyspark.sql import functions as SqlFuncs

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Default ruleset used by all target nodes with data quality enabled
DEFAULT_DATA_QUALITY_RULESET = """
    Rules = [
        ColumnCount > 0
    ]
"""

# Script generated for node Amazon S3
AmazonS3_node1774575466278 = glueContext.create_dynamic_frame.from_options(format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False}, connection_type="s3", format="csv", connection_options={"paths": ["s3://DELETED_FOR_SECURITY_REASONS"], "recurse": True}, transformation_ctx="AmazonS3_node1774575466278")

# Script generated for node Change Schema
ChangeSchema_node1776933859657 = ApplyMapping.apply(frame=AmazonS3_node1774575466278, mappings=[("fecha", "string", "fecha", "string"), ("precio", "string", "precio", "double"), ("promedio_20d", "string", "promedio_20d", "double"), ("rsi", "string", "rsi", "double"), ("bollinger_alta", "string", "bollinger_alta", "double"), ("bollinger_baja", "string", "bollinger_baja", "double"), ("macd_linea", "string", "macd_linea", "double"), ("macd_senal", "string", "macd_senal", "double")], transformation_ctx="ChangeSchema_node1776933859657")

# Script generated for node Drop Duplicates
DropDuplicates_node1774575645360 =  DynamicFrame.fromDF(ChangeSchema_node1776933859657.toDF().dropDuplicates(["fecha"]), glueContext, "DropDuplicates_node1774575645360")

# Script generated for node SQL Query
SqlQuery38 = '''
select * from myDataSource where length(macd_senal) != 0
'''
SQLQuery_node1775593689692 = sparkSqlQuery(glueContext, query = SqlQuery38, mapping = {"myDataSource":DropDuplicates_node1774575645360}, transformation_ctx = "SQLQuery_node1775593689692")

# Script generated for node Amazon S3
EvaluateDataQuality().process_rows(frame=SQLQuery_node1775593689692, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1775611477237", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
if (SQLQuery_node1775593689692.count() >= 1):
   SQLQuery_node1775593689692 = SQLQuery_node1775593689692.coalesce(1)
AmazonS3_node1775611501916 = glueContext.getSink(path="s3://DELETED_FOR_SECURITY_REASONS", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=[], enableUpdateCatalog=True, transformation_ctx="AmazonS3_node1775611501916")
AmazonS3_node1775611501916.setCatalogInfo(catalogDatabase="glue-2silver",catalogTableName="silver_table")
AmazonS3_node1775611501916.setFormat("glueparquet", compression="snappy")
AmazonS3_node1775611501916.writeFrame(SQLQuery_node1775593689692)
job.commit()