from typing import Any, Dict
import os
import boto3
from boto3.dynamodb.conditions import Attr
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.event_handler.api_gateway import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

# aws_lambda_powertools
logger = Logger()
tracer = Tracer()
cors_config = CORSConfig(allow_origin=os.environ['CORS_ORIGIN'], max_age=300)
app = APIGatewayRestResolver(cors=cors_config, strip_prefixes=[os.environ['BASE_PATH']])

# resource table
table = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> Dict[str, Any]:
    logger.debug(os.environ)
    return app.resolve(event, context)


@app.get('/')
@tracer.capture_method
def get():
    data = table.scan(
        FilterExpression=Attr('visible').eq(True)
    )
    logger.debug(data)
    
    for x in data['Items']:
        del x['visible']

    return {'message': data['Items']}
