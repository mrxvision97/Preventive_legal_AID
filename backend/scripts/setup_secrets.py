"""
Script to store secrets in AWS Secrets Manager
Run this once to set up cloud storage for API keys
"""
import boto3
import json
import sys
from botocore.exceptions import ClientError

def create_secret():
    """Create secret in AWS Secrets Manager"""
    secret_name = "vu-legal-aid-secrets"
    region_name = "us-east-1"  # Change to your region
    
    # Get AWS credentials from environment or input
    aws_access_key = input("Enter AWS Access Key ID: ").strip()
    aws_secret_key = input("Enter AWS Secret Access Key: ").strip()
    
    # Get secrets to store
    print("\nEnter API keys (press Enter to skip):")
    secrets = {}
    
    openai_key = input("OpenAI API Key: ").strip()
    if openai_key:
        secrets["OPENAI_API_KEY"] = openai_key
    
    redis_password = input("Redis Password: ").strip()
    if redis_password:
        secrets["REDIS_PASSWORD"] = redis_password
    
    langcache_key = input("LangCache API Key: ").strip()
    if langcache_key:
        secrets["LANGCACHE_API_KEY"] = langcache_key
    
    pinecone_key = input("Pinecone API Key: ").strip()
    if pinecone_key:
        secrets["PINECONE_API_KEY"] = pinecone_key
    
    # Create Secrets Manager client
    session = boto3.session.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region_name
    )
    client = session.client(service_name='secretsmanager')
    
    try:
        # Try to get existing secret
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        print(f"Secret {secret_name} already exists. Updating...")
        
        # Update existing secret
        client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(secrets)
        )
        print(f"Secret {secret_name} updated successfully!")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Create new secret
            try:
                client.create_secret(
                    Name=secret_name,
                    Description="API keys for VU Legal AID application",
                    SecretString=json.dumps(secrets)
                )
                print(f"Secret {secret_name} created successfully!")
            except Exception as e:
                print(f"Error creating secret: {e}")
                sys.exit(1)
        else:
            print(f"Error: {e}")
            sys.exit(1)
    
    print("\nSecrets stored in AWS Secrets Manager!")
    print("The application will automatically load these on startup.")


if __name__ == "__main__":
    create_secret()

