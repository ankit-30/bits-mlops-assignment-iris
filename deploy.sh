#!/bin/bash

# Deployment script for Iris MLOps Pipeline
set -e

echo "🚀 Starting deployment of Iris MLOps Pipeline..."

# Configuration
APP_NAME="iris-mlops"
DOCKER_IMAGE="iris-mlops:latest"
CONTAINER_NAME="iris-mlops-container"
PORT=8000

# Function to check if container is running
check_container() {
    docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" --quiet
}

# Function to stop and remove existing container
cleanup_container() {
    if [ "$(check_container)" ]; then
        echo "📦 Stopping existing container..."
        docker stop $CONTAINER_NAME
    fi
    
    if [ "$(docker ps -a --filter "name=$CONTAINER_NAME" --quiet)" ]; then
        echo "🗑️  Removing existing container..."
        docker rm $CONTAINER_NAME
    fi
}

# Function to build Docker image
build_image() {
    echo "🔨 Building Docker image..."
    docker build -t $DOCKER_IMAGE .
}

# Function to run the container
run_container() {
    echo "🏃 Running new container..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8000 \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/models:/app/models \
        -v $(pwd)/data:/app/data \
        $DOCKER_IMAGE
}

# Function to wait for service to be ready
wait_for_service() {
    echo "⏳ Waiting for service to be ready..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
            echo "✅ Service is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    echo "❌ Service failed to start within timeout"
    return 1
}

# Function to run health check
health_check() {
    echo "🏥 Running health check..."
    response=$(curl -s http://localhost:$PORT/health)
    echo "Health check response: $response"
    
    if echo "$response" | grep -q '"status":"healthy"'; then
        echo "✅ Health check passed!"
        return 0
    else
        echo "❌ Health check failed!"
        return 1
    fi
}

# Function to display service info
show_service_info() {
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "📊 Service Information:"
    echo "   • API URL: http://localhost:$PORT"
    echo "   • API Docs: http://localhost:$PORT/docs"
    echo "   • Health Check: http://localhost:$PORT/health"
    echo "   • Metrics: http://localhost:$PORT/metrics"
    echo "   • Container Name: $CONTAINER_NAME"
    echo ""
    echo "📋 Useful Commands:"
    echo "   • View logs: docker logs $CONTAINER_NAME"
    echo "   • Stop service: docker stop $CONTAINER_NAME"
    echo "   • Restart service: docker restart $CONTAINER_NAME"
    echo ""
}

# Main deployment workflow
main() {
    echo "Starting deployment workflow..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Cleanup existing container
    cleanup_container
    
    # Build new image
    build_image
    
    # Run new container
    run_container
    
    # Wait for service to be ready
    if wait_for_service; then
        # Run health check
        if health_check; then
            show_service_info
        else
            echo "❌ Deployment failed health check"
            exit 1
        fi
    else
        echo "❌ Deployment failed - service not ready"
        exit 1
    fi
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        echo "🛑 Stopping service..."
        docker stop $CONTAINER_NAME || echo "Container not running"
        ;;
    "restart")
        echo "🔄 Restarting service..."
        docker restart $CONTAINER_NAME
        wait_for_service && health_check
        ;;
    "logs")
        echo "📋 Showing logs..."
        docker logs -f $CONTAINER_NAME
        ;;
    "status")
        echo "📊 Service status:"
        if [ "$(check_container)" ]; then
            echo "✅ Service is running"
            health_check
        else
            echo "❌ Service is not running"
        fi
        ;;
    "help")
        echo "Usage: $0 [deploy|stop|restart|logs|status|help]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the service (default)"
        echo "  stop     - Stop the service"
        echo "  restart  - Restart the service"
        echo "  logs     - Show service logs"
        echo "  status   - Check service status"
        echo "  help     - Show this help message"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
