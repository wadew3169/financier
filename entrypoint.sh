#!/bin/bash
# Entrypoint script for simulated cryptominer Docker container with Cloudflare integration
# This script serves as the entrypoint for our simulated miner container

# Print banner
echo "====================================================="
echo "     SIMULATED CRYPTOMINER FOR SECURITY TESTING      "
echo "              *** NOT ACTUAL MINING ***              "
echo "====================================================="
echo "This container simulates cryptocurrency mining behavior"
echo "for security testing and detection tuning purposes."
echo "No actual cryptocurrency mining is performed."
echo "====================================================="
echo ""

# Parse environment variables
CLOUDFLARE_WEBHOOK_URL=${CLOUDFLARE_WEBHOOK_URL}
BEACON_INTERVAL=${BEACON_INTERVAL:-"30"}
ALGO=${ALGO:-"ethash"}
WALLET=${WALLET:-"0x0000000000000000000000000000000000000000"}
WORKER=${WORKER:-"dockerized-miner"}
THREADS=${THREADS:-"2"}
USE_GPU=${USE_GPU:-"false"}
INTENSITY=${INTENSITY:-"8"}

# Display configuration
echo "Starting simulated miner with configuration:"
if [ -n "$CLOUDFLARE_WEBHOOK_URL" ]; then
    echo "  Cloudflare webhook:   Configured"
    echo "  Beacon Interval: $BEACON_INTERVAL seconds"
else
    echo "  Cloudflare webhook:   Not configured (reports will be logged but not sent)"
fi
echo "  Algorithm:       $ALGO"
echo "  Wallet:          $WALLET"
echo "  Worker:          $WORKER"
echo "  Threads:         $THREADS"
echo "  Use GPU:         $USE_GPU"
echo "  Intensity:       $INTENSITY"
echo ""

# Generate AWS-style HTML file name (for detection testing)
ACCOUNT_ID=$(( RANDOM % 1000000000 ))
RANDOM_ID=$(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 8 | head -n 1)
RANDOM_ID2=$(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 12 | head -n 1)
AWS_STYLE_FILENAME="${ACCOUNT_ID}${RANDOM_ID}-Instance-Profile-Enforcement-${RANDOM_ID}-9d6a-4e5d-b${RANDOM_ID2}.html"

# Create AWS-style HTML file that could trigger detection
cat > "/home/miner/.mining/configs/${AWS_STYLE_FILENAME}" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>AWS Instance Profile Enforcement</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>
        // AWS-style credential-like variables
        var accessKey = "AKIA${RANDOM_ID}${RANDOM_ID2}";
        var secretKey = "$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)";
        
        function checkInstanceProfile() {
            // Simulate AWS credential retrieval
            console.log("Checking instance profile...");
            setTimeout(function() {
                document.getElementById("status").innerHTML = "Instance profile verified";
                startMining();
            }, 2000);
        }
        
        function startMining() {
            console.log("Starting mining process...");
            // Simulated crypto mining code would be here
        }
    </script>
</head>
<body onload="checkInstanceProfile()">
    <h1>AWS Instance Profile Verification</h1>
    <div id="status">Checking instance profile...</div>
    <div id="mining-status">Waiting for verification...</div>
</body>
</html>
EOF

echo "Created AWS-style file: /home/miner/.mining/configs/${AWS_STYLE_FILENAME}"

# Check if Cloudflare webhook URL is provided
if [ -z "$CLOUDFLARE_WEBHOOK_URL" ]; then
    echo "Warning: No Cloudflare webhook URL provided. Reports will be logged but not sent."
    echo "To enable Cloudflare reporting, run with:"
    echo "  -e CLOUDFLARE_WEBHOOK_URL=https://YOUR-CLOUDFLARE.WEBHOOK.workers.dev"
fi

# Convert USE_GPU to command line option
if [ "$USE_GPU" = "true" ]; then
    GPU_OPTION="--use-gpu"
else
    GPU_OPTION=""
fi

# Generate a fake process ID file
echo $$ > /home/miner/.mining/logs/miner.pid

# Start the simulated miner with Cloudflare reporting
exec python3 /home/miner/fake_cryptominer.py \
    --cloudflare-webhook-url "$CLOUDFLARE_WEBHOOK_URL" \
    --beacon-interval "$BEACON_INTERVAL" \
    --algo "$ALGO" \
    --wallet "$WALLET" \
    --worker "$WORKER" \
    --threads "$THREADS" \
    --intensity "$INTENSITY" \
    $GPU_OPTION
