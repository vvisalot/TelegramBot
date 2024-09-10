import boto3

# Inicializa el cliente para Bedrock
client = boto3.client('bedrock', region_name='us-east-1')

# Listar los modelos disponibles en Bedrock
response = client.list_foundation_models()

# Imprime la respuesta completa
print(response)