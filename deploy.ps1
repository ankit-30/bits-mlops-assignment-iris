# Deployment script for Iris MLOps Pipeline (PowerShell)
param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "stop", "restart", "logs", "status", "help")]
    [string]$Action = "deploy"
)

# Configuration
$APP_NAME = "iris-mlops"
$DOCKER_IMAGE = "iris-mlops:latest"
$CONTAINER_NAME = "iris-mlops-container"
$PORT = 8000

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-ContainerRunning {
    $result = docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" --quiet
    return $result -ne $null -and $result.Trim() -ne ""
}

function Remove-ExistingContainer {
    if (Test-ContainerRunning) {
        Write-ColorOutput "📦 Stopping existing container..." "Yellow"
        docker stop $CONTAINER_NAME
    }
    
    $existing = docker ps -a --filter "name=$CONTAINER_NAME" --quiet
    if ($existing -ne $null -and $existing.Trim() -ne "") {
        Write-ColorOutput "🗑️  Removing existing container..." "Yellow"
        docker rm $CONTAINER_NAME
    }
}

function Build-DockerImage {
    Write-ColorOutput "🔨 Building Docker image..." "Cyan"
    docker build -t $DOCKER_IMAGE .
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ Failed to build Docker image" "Red"
        exit 1
    }
}

function Start-Container {
    Write-ColorOutput "🏃 Running new container..." "Green"
    
    # Create volumes if they don't exist
    if (!(Test-Path ".\logs")) { New-Item -ItemType Directory -Path ".\logs" -Force | Out-Null }
    if (!(Test-Path ".\models")) { New-Item -ItemType Directory -Path ".\models" -Force | Out-Null }
    if (!(Test-Path ".\data")) { New-Item -ItemType Directory -Path ".\data" -Force | Out-Null }
    
    $currentDir = (Get-Location).Path
    docker run -d `
        --name $CONTAINER_NAME `
        -p "${PORT}:8000" `
        -v "${currentDir}\logs:/app/logs" `
        -v "${currentDir}\models:/app/models" `
        -v "${currentDir}\data:/app/data" `
        $DOCKER_IMAGE
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ Failed to start container" "Red"
        exit 1
    }
}

function Wait-ForService {
    Write-ColorOutput "⏳ Waiting for service to be ready..." "Yellow"
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$PORT/health" -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "✅ Service is ready!" "Green"
                return $true
            }
        }
        catch {
            # Service not ready yet
        }
        
        $attempt++
        Write-ColorOutput "   Attempt $attempt/$maxAttempts..." "Gray"
        Start-Sleep -Seconds 2
    }
    
    Write-ColorOutput "❌ Service failed to start within timeout" "Red"
    return $false
}

function Test-ServiceHealth {
    Write-ColorOutput "🏥 Running health check..." "Cyan"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$PORT/health" -ErrorAction Stop
        $content = $response.Content | ConvertFrom-Json
        
        Write-ColorOutput "Health check response: $($response.Content)" "Gray"
        
        if ($content.status -eq "healthy") {
            Write-ColorOutput "✅ Health check passed!" "Green"
            return $true
        } else {
            Write-ColorOutput "❌ Health check failed!" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "❌ Health check failed: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Show-ServiceInfo {
    Write-ColorOutput ""
    Write-ColorOutput "🎉 Deployment completed successfully!" "Green"
    Write-ColorOutput "📊 Service Information:" "Cyan"
    Write-ColorOutput "   • API URL: http://localhost:$PORT" "White"
    Write-ColorOutput "   • API Docs: http://localhost:$PORT/docs" "White"
    Write-ColorOutput "   • Health Check: http://localhost:$PORT/health" "White"
    Write-ColorOutput "   • Metrics: http://localhost:$PORT/metrics" "White"
    Write-ColorOutput "   • Container Name: $CONTAINER_NAME" "White"
    Write-ColorOutput ""
    Write-ColorOutput "📋 Useful Commands:" "Cyan"
    Write-ColorOutput "   • View logs: docker logs $CONTAINER_NAME" "White"
    Write-ColorOutput "   • Stop service: docker stop $CONTAINER_NAME" "White"
    Write-ColorOutput "   • Restart service: docker restart $CONTAINER_NAME" "White"
    Write-ColorOutput ""
}

function Invoke-Deployment {
    Write-ColorOutput "🚀 Starting deployment of Iris MLOps Pipeline..." "Green"
    
    # Check if Docker is running
    try {
        docker info 2>$null | Out-Null
    }
    catch {
        Write-ColorOutput "❌ Docker is not running. Please start Docker and try again." "Red"
        exit 1
    }
    
    # Cleanup existing container
    Remove-ExistingContainer
    
    # Build new image
    Build-DockerImage
    
    # Run new container
    Start-Container
    
    # Wait for service to be ready
    if (Wait-ForService) {
        # Run health check
        if (Test-ServiceHealth) {
            Show-ServiceInfo
        } else {
            Write-ColorOutput "❌ Deployment failed health check" "Red"
            exit 1
        }
    } else {
        Write-ColorOutput "❌ Deployment failed - service not ready" "Red"
        exit 1
    }
}

function Stop-Service {
    Write-ColorOutput "🛑 Stopping service..." "Yellow"
    try {
        docker stop $CONTAINER_NAME
        Write-ColorOutput "✅ Service stopped" "Green"
    }
    catch {
        Write-ColorOutput "❌ Container not running or failed to stop" "Red"
    }
}

function Restart-Service {
    Write-ColorOutput "🔄 Restarting service..." "Yellow"
    try {
        docker restart $CONTAINER_NAME
        if (Wait-ForService) {
            Test-ServiceHealth | Out-Null
        }
    }
    catch {
        Write-ColorOutput "❌ Failed to restart service" "Red"
    }
}

function Show-Logs {
    Write-ColorOutput "📋 Showing logs..." "Cyan"
    docker logs -f $CONTAINER_NAME
}

function Show-Status {
    Write-ColorOutput "📊 Service status:" "Cyan"
    if (Test-ContainerRunning) {
        Write-ColorOutput "✅ Service is running" "Green"
        Test-ServiceHealth | Out-Null
    } else {
        Write-ColorOutput "❌ Service is not running" "Red"
    }
}

function Show-Help {
    Write-ColorOutput "Usage: .\deploy.ps1 [deploy|stop|restart|logs|status|help]" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "Commands:" "White"
    Write-ColorOutput "  deploy   - Deploy the service (default)" "Gray"
    Write-ColorOutput "  stop     - Stop the service" "Gray"
    Write-ColorOutput "  restart  - Restart the service" "Gray"
    Write-ColorOutput "  logs     - Show service logs" "Gray"
    Write-ColorOutput "  status   - Check service status" "Gray"
    Write-ColorOutput "  help     - Show this help message" "Gray"
}

# Main execution
switch ($Action) {
    "deploy" { Invoke-Deployment }
    "stop" { Stop-Service }
    "restart" { Restart-Service }
    "logs" { Show-Logs }
    "status" { Show-Status }
    "help" { Show-Help }
    default { 
        Write-ColorOutput "Unknown command: $Action" "Red"
        Write-ColorOutput "Use '.\deploy.ps1 help' for usage information" "Yellow"
        exit 1
    }
}
