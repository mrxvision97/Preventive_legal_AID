#!/bin/bash
# Cloud Deployment Script for VU Legal AID Backend
# Supports: AWS EC2, Azure App Service, GCP Cloud Run

set -e

echo "=========================================="
echo "VU Legal AID - Cloud Deployment Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check for required tools
check_dependencies() {
    echo "Checking dependencies..."
    
    if ! command -v git &> /dev/null; then
        echo -e "${RED}Error: git is not installed${NC}"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Dependencies OK${NC}"
}

# Deploy to AWS EC2
deploy_aws_ec2() {
    echo ""
    echo "=== AWS EC2 Deployment ==="
    echo ""
    
    read -p "EC2 instance IP or hostname: " EC2_HOST
    read -p "SSH key path: " SSH_KEY
    read -p "EC2 username (default: ubuntu): " EC2_USER
    EC2_USER=${EC2_USER:-ubuntu}
    
    echo "Deploying to AWS EC2..."
    
    # Copy files to EC2
    echo "Copying files..."
    scp -i "$SSH_KEY" -r ../backend "$EC2_USER@$EC2_HOST:~/"
    
    # Run setup on EC2
    echo "Running setup on EC2..."
    ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << 'ENDSSH'
cd ~/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create systemd service
sudo tee /etc/systemd/system/vu-legal-aid.service > /dev/null <<EOF
[Unit]
Description=VU Legal AID Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/backend
Environment="PATH=$HOME/backend/venv/bin"
ExecStart=$HOME/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable vu-legal-aid
sudo systemctl start vu-legal-aid

echo "Backend deployed and started!"
ENDSSH
    
    echo -e "${GREEN}Deployment complete!${NC}"
    echo "Backend URL: http://$EC2_HOST:8000"
}

# Deploy to Azure App Service
deploy_azure() {
    echo ""
    echo "=== Azure App Service Deployment ==="
    echo ""
    
    if ! command -v az &> /dev/null; then
        echo -e "${YELLOW}Azure CLI not found. Installing...${NC}"
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    fi
    
    read -p "Azure resource group name: " RESOURCE_GROUP
    read -p "App Service name: " APP_NAME
    read -p "Azure region (default: eastus): " REGION
    REGION=${REGION:-eastus}
    
    echo "Creating Azure resources..."
    
    # Create resource group
    az group create --name "$RESOURCE_GROUP" --location "$REGION"
    
    # Create App Service plan
    az appservice plan create \
        --name "${APP_NAME}-plan" \
        --resource-group "$RESOURCE_GROUP" \
        --sku B1 \
        --is-linux
    
    # Create web app
    az webapp create \
        --resource-group "$RESOURCE_GROUP" \
        --plan "${APP_NAME}-plan" \
        --name "$APP_NAME" \
        --runtime "PYTHON:3.11"
    
    echo "Configure environment variables in Azure Portal or use:"
    echo "az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings KEY=VALUE"
    
    echo -e "${GREEN}Azure deployment initiated!${NC}"
    echo "App URL: https://$APP_NAME.azurewebsites.net"
}

# Deploy to GCP Cloud Run
deploy_gcp() {
    echo ""
    echo "=== GCP Cloud Run Deployment ==="
    echo ""
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}Error: gcloud CLI is not installed${NC}"
        echo "Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    read -p "GCP project ID: " PROJECT_ID
    read -p "Cloud Run service name: " SERVICE_NAME
    read -p "GCP region (default: us-central1): " REGION
    REGION=${REGION:-us-central1}
    
    echo "Setting GCP project..."
    gcloud config set project "$PROJECT_ID"
    
    # Create Dockerfile if not exists
    if [ ! -f Dockerfile ]; then
        echo "Creating Dockerfile..."
        cat > Dockerfile <<EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080"]
EOF
    fi
    
    # Build and deploy
    echo "Building container..."
    gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
    
    echo "Deploying to Cloud Run..."
    gcloud run deploy "$SERVICE_NAME" \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --port 8080
    
    echo -e "${GREEN}GCP deployment complete!${NC}"
    echo "Service URL: Check Cloud Run console"
}

# Main menu
main() {
    check_dependencies
    
    echo ""
    echo "Select deployment target:"
    echo "1) AWS EC2"
    echo "2) Azure App Service"
    echo "3) GCP Cloud Run"
    echo "4) Exit"
    echo ""
    read -p "Choice [1-4]: " choice
    
    case $choice in
        1)
            deploy_aws_ec2
            ;;
        2)
            deploy_azure
            ;;
        3)
            deploy_gcp
            ;;
        4)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
}

main

