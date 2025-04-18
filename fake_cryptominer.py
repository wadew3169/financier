#!/usr/bin/env python3
"""
Simulated Cryptocurrency Miner with Slack Webhook Integration
------------------------------------------------------------
This script simulates cryptocurrency mining behavior for security testing
and sends reports to a Slack webhook for monitoring.

Features:
- Simulated mining behavior without actual mining
- Regular beacons to a Slack webhook
- CPU usage patterns resembling mining software
- File operations similar to mining software
- In-memory strings similar to mining software

Environment Variables:
- SLACK_WEBHOOK_URL: Your Slack webhook URL
- BEACON_INTERVAL: Time between beacons in seconds (default: 30)
- ALGO: Mining algorithm to simulate (for log purposes)
- WALLET: Wallet address for simulation (for log purposes)
- WORKER: Worker name for the simulation
- THREADS: Number of CPU threads to simulate mining on
- USE_GPU: Simulate GPU mining behavior (true/false)
- INTENSITY: Mining intensity (1-10)
"""

import os
import sys
import time
import random
import socket
import argparse
import threading
import multiprocessing
import hashlib
import logging
import json
import uuid
import platform
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('crypto_miner')

# Common cryptocurrency mining strings that might trigger detection
CRYPTO_STRINGS = [
    "stratum protocol", "ethash", "sha256", "scrypt", "randomx",
    "getwork", "getblocktemplate", "difficulty target",
    "nonce", "block header", "merkle root", "dag generation",
    "hashrate", "xmrig", "ethminer", "cgminer", "t-rex miner"
]

class FakeMiner:
    def __init__(self, args):
        self.args = args
        self.running = False
        self.shares_found = 0
        self.shares_accepted = 0
        self.shares_rejected = 0
        self.start_time = 0
        self.hashrate = 0
        self.worker_threads = []
        
        # Generate a unique ID for this miner instance
        self.miner_id = str(uuid.uuid4())
        
        # Create mining directory structure
        self._setup_directories()
        
        # Generate AWS-style identifiers for beaconing
        self.instance_id = f"i-{uuid.uuid4().hex[:8]}"
        self.account_id = f"{random.randint(100000000000, 999999999999)}"
        
    def _setup_directories(self):
        """Create directory structure similar to mining software"""
        try:
            os.makedirs(os.path.expanduser("~/.mining/logs"), exist_ok=True)
            os.makedirs(os.path.expanduser("~/.mining/configs"), exist_ok=True)
            os.makedirs(os.path.expanduser("~/.mining/bins"), exist_ok=True)
            
            # Create fake configuration files
            self._create_config_files()
            
            logger.info("Created mining directory structure")
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
    
    def _create_config_files(self):
        """Create fake configuration files"""
        config = {
            "pools": [
                {
                    "url": "stratum+tcp://us1.ethermine.org:4444",
                    "user": self.args.wallet,
                    "pass": "x",
                    "worker": self.args.worker,
                    "algorithm": self.args.algo
                }
            ],
            "cpu": {
                "enabled": True,
                "threads": self.args.threads,
                "priority": 5
            },
            "opencl": {
                "enabled": self.args.use_gpu,
                "platform": "AMD",
                "loader": None,
                "adl": True
            },
            "cuda": {
                "enabled": self.args.use_gpu,
                "loader": None,
                "nvml": True
            },
            "donate-level": 1,
            "log-file": "~/.mining/logs/miner.log",
            "retries": 5,
            "retry-pause": 5,
            "watchdog": True
        }
        
        # Write JSON config
        config_path = os.path.expanduser("~/.mining/configs/config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        # Write fake binary file to trigger AV/EDR
        with open(os.path.expanduser("~/.mining/bins/xmrig"), 'w') as f:
            f.write("#!/bin/bash\n# XMRig Miner v6.16.2\n# Copyright (c) 2021-2023\n# OpenCL/CUDA Miner")
        os.chmod(os.path.expanduser("~/.mining/bins/xmrig"), 0o755)
        
        # Create AWS-style HTML file that could trigger detection
        account_id = random.randint(100000000, 999999999)
        random_id = ''.join(random.choices('0123456789abcdef', k=8))
        random_id2 = ''.join(random.choices('0123456789abcdef', k=12))
        aws_filename = f"{account_id}{random_id}-Instance-Profile-Enforcement-{random_id}-9d6a-4e5d-b{random_id2}.html"
        
        with open(os.path.expanduser(f"~/.mining/configs/{aws_filename}"), 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>AWS Instance Profile Enforcement</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>
        // AWS-style credential-like variables
        var accessKey = "AKIA{random_id}{random_id2}";
        var secretKey = "{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=40))}";
        
        function checkInstanceProfile() {{
            // Simulate AWS credential retrieval
            console.log("Checking instance profile...");
            setTimeout(function() {{
                document.getElementById("status").innerHTML = "Instance profile verified";
                startMining();
            }}, 2000);
        }}
        
        function startMining() {{
            console.log("Starting mining process...");
            // Simulated crypto mining code would be here
        }}
    </script>
</head>
<body onload="checkInstanceProfile()">
    <h1>AWS Instance Profile Verification</h1>
    <div id="status">Checking instance profile...</div>
    <div id="mining-status">Waiting for verification...</div>
</body>
</html>""")
        
    def start(self):
        """Start the simulated mining operation"""
        self.running = True
        self.start_time = time.time()
        
        logger.info(f"Starting {self.args.algo} miner with Slack reporting")
        logger.info(f"Slack webhook URL: {self.args.slack_webhook_url}")
        logger.info(f"Beacon interval: {self.args.beacon_interval} seconds")
        logger.info(f"Worker ID: {self.args.worker}")
        logger.info(f"Using {self.args.threads} threads")
        
        # Check CUDA/OpenCL paths to simulate GPU mining setup
        if self.args.use_gpu:
            logger.info("Checking GPU devices...")
            time.sleep(1)
            logger.info("Found 2 compatible GPU devices")
            logger.info("Initializing DAG on GPU...")
            time.sleep(3)
            logger.info("DAG generation complete")
        
        # Start the mining simulation threads
        self._start_cpu_simulation()
        self._start_slack_reporting()
        self._start_progress_reporting()
        
        # Keep the main thread alive
        try:
            while self.running:
                time.sleep(1)
                # Randomly load crypto strings into memory
                _ = random.choice(CRYPTO_STRINGS) * 1000
        except KeyboardInterrupt:
            self.stop()

    def _start_cpu_simulation(self):
        """Simulate CPU mining with high utilization"""
        logger.info(f"Starting {self.args.threads} mining threads")
        
        for i in range(self.args.threads):
            t = threading.Thread(target=self._cpu_worker, args=(i,))
            t.daemon = True
            t.start()
            self.worker_threads.append(t)
            logger.info(f"Thread {i} started")
    
    def _cpu_worker(self, thread_id):
        """Worker thread that simulates CPU mining"""
        logger.info(f"Worker {thread_id} initialized")
        
        while self.running:
            # Simulate mining by calculating hashes (but not as intensively as real mining)
            start = time.time()
            
            # Generate random data and calculate hashes to simulate work
            # Use a lighter workload than actual mining
            data = os.urandom(64)
            for _ in range(1000):  # Reduced iterations to prevent high CPU load
                if not self.running:
                    break
                h = hashlib.sha256(data).digest()
                data = h
                
                # Randomly simulate finding a share
                if random.random() < 0.01:  # 1% chance per 1000 hashes
                    self._found_share()
            
            # Sleep to reduce CPU usage compared to real mining
            time.sleep(0.1)
            
            # Update simulated hashrate (much lower than real mining)
            elapsed = time.time() - start
            if elapsed > 0:
                # Update with reasonable simulated hashrate
                thread_hashrate = 1000 / elapsed / 1000  # MH/s
                with threading.Lock():
                    self.hashrate = thread_hashrate * self.args.threads
    
    def _start_slack_reporting(self):
        """Start sending reports to Slack webhook"""
        t = threading.Thread(target=self._slack_reporter)
        t.daemon = True
        t.start()
        logger.info(f"Started Slack reporting to {self.args.slack_webhook_url}")
    
    def _slack_reporter(self):
        """Worker thread that sends reports to Slack webhook"""
        report_count = 0
        
        # Send initial report
        self._send_slack_report("Miner started", "good")
        
        while self.running:
            try:
                time.sleep(self.args.beacon_interval)
                
                if not self.running:
                    break
                    
                report_count += 1
                
                # Send regular status update
                if report_count % 5 == 0:
                    # Every 5th report, include more details
                    self._send_detailed_slack_report()
                else:
                    # Regular status update
                    self._send_slack_report("Mining operation in progress", "good")
                
            except Exception as e:
                logger.error(f"Error sending Slack report: {e}")
    
    def _send_slack_report(self, message, color="good"):
        """Send a simple report to Slack webhook"""
        try:
            runtime = time.time() - self.start_time
            hours = int(runtime / 3600)
            minutes = int((runtime % 3600) / 60)
            seconds = int(runtime % 60)
            
            # Prepare Slack message payload
            payload = {
                "attachments": [
                    {
                        "fallback": f"Mining Report: {message}",
                        "color": color,  # good, warning, danger, or hex color
                        "title": "Simulated Cryptominer Report",
                        "text": message,
                        "fields": [
                            {
                                "title": "Worker",
                                "value": self.args.worker,
                                "short": True
                            },
                            {
                                "title": "Algorithm",
                                "value": self.args.algo,
                                "short": True
                            },
                            {
                                "title": "Hashrate",
                                "value": f"{self.hashrate:.2f} MH/s",
                                "short": True
                            },
                            {
                                "title": "Runtime",
                                "value": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                                "short": True
                            }
                        ],
                        "footer": f"Instance: {self.instance_id} | ID: {self.miner_id[:8]}",
                        "ts": int(time.time())
                    }
                ]
            }
            
            # Send the payload to Slack
            response = requests.post(
                self.args.slack_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to send Slack report: {response.status_code} - {response.text}")
            else:
                logger.info(f"Slack report sent successfully")
                
        except Exception as e:
            logger.error(f"Error preparing Slack report: {e}")
    
    def _send_detailed_slack_report(self):
        """Send a detailed report to Slack webhook"""
        try:
            runtime = time.time() - self.start_time
            hours = int(runtime / 3600)
            minutes = int((runtime % 3600) / 60)
            seconds = int(runtime % 60)
            
            # Collect system information
            system_info = {
                "hostname": socket.gethostname(),
                "ip": self._get_ip_address(),
                "os": platform.system(),
                "os_version": platform.version(),
                "platform": platform.platform(),
                "cpu_count": multiprocessing.cpu_count(),
                "architecture": platform.machine()
            }
            
            # Format system info for Slack
            system_info_text = "\n".join([
                f"*{key}*: {value}" 
                for key, value in system_info.items()
            ])
            
            # Prepare Slack message payload
            payload = {
                "attachments": [
                    {
                        "fallback": "Detailed Mining Report",
                        "color": "good",
                        "title": "Detailed Cryptominer Report",
                        "text": "Detailed status report of the simulated cryptominer",
                        "fields": [
                            {
                                "title": "Worker",
                                "value": self.args.worker,
                                "short": True
                            },
                            {
                                "title": "Algorithm",
                                "value": self.args.algo,
                                "short": True
                            },
                            {
                                "title": "Hashrate",
                                "value": f"{self.hashrate:.2f} MH/s",
                                "short": True
                            },
                            {
                                "title": "Runtime",
                                "value": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                                "short": True
                            },
                            {
                                "title": "Shares",
                                "value": f"Found: {self.shares_found}, Accepted: {self.shares_accepted}, Rejected: {self.shares_rejected}",
                                "short": False
                            },
                            {
                                "title": "System Information",
                                "value": system_info_text,
                                "short": False
                            }
                        ],
                        "footer": f"Instance: {self.instance_id} | Account: {self.account_id} | ID: {self.miner_id[:8]}",
                        "ts": int(time.time())
                    }
                ]
            }
            
            # Optional: Add fake "sensitive data" to sometimes trigger DLP alerts
            if random.random() < 0.2:  # 20% chance
                fake_aws_access_key = f"AKIA{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))}"
                fake_aws_secret_key = f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=', k=40))}"
                
                payload["attachments"][0]["fields"].append({
                    "title": "AWS Credentials (Simulated)",
                    "value": f"Access Key: {fake_aws_access_key}\nSecret Key: {fake_aws_secret_key}",
                    "short": False
                })
            
            # Send the payload to Slack
            response = requests.post(
                self.args.slack_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to send detailed Slack report: {response.status_code} - {response.text}")
            else:
                logger.info(f"Detailed Slack report sent successfully")
                
        except Exception as e:
            logger.error(f"Error preparing detailed Slack report: {e}")
    
    def _get_ip_address(self):
        """Get the machine's IP address"""
        try:
            # This doesn't actually make a connection
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _start_progress_reporting(self):
        """Start thread to report mining progress"""
        t = threading.Thread(target=self._progress_reporter)
        t.daemon = True
        t.start()
    
    def _progress_reporter(self):
        """Report simulated mining progress periodically"""
        while self.running:
            # Sleep for a random interval to simulate mining progress
            time.sleep(random.uniform(5, 15))
            
            if self.running:
                runtime = time.time() - self.start_time
                hours = int(runtime / 3600)
                minutes = int((runtime % 3600) / 60)
                seconds = int(runtime % 60)
                
                # Log progress with simulated hashrate
                hashrate_unit = "MH/s"
                if self.args.algo in ["randomx", "cryptonight"]:
                    hashrate_unit = "KH/s"
                
                logger.info(
                    f"Mining for {hours:02d}:{minutes:02d}:{seconds:02d} | " +
                    f"Hashrate: {self.hashrate:.2f} {hashrate_unit} | " +
                    f"Shares: {self.shares_accepted}/{self.shares_found} " +
                    f"(rejected: {self.shares_rejected})"
                )
    
    def _found_share(self):
        """Simulate finding and submitting a share"""
        self.shares_found += 1
        
        # Simulate share acceptance (95% accepted, 5% rejected)
        if random.random() < 0.95:
            self.shares_accepted += 1
            logger.info(f"Share accepted ({self.shares_accepted}/{self.shares_found})")
        else:
            self.shares_rejected += 1
            logger.info(f"Share rejected ({self.shares_rejected}/{self.shares_found}) - Low difficulty")
    
    def stop(self):
        """Stop the simulated mining operation"""
        logger.info("Stopping miner...")
        self.running = False
        
        # Send final report to Slack
        self._send_slack_report("Miner stopped", "danger")
        
        # Wait for threads to finish
        for t in self.worker_threads:
            t.join(1.0)
        
        runtime = time.time() - self.start_time
        hours = int(runtime / 3600)
        minutes = int((runtime % 3600) / 60)
        seconds = int(runtime % 60)
        
        logger.info(f"Mining session ended after {hours:02d}:{minutes:02d}:{seconds:02d}")
        logger.info(f"Shares: {self.shares_accepted}/{self.shares_found} " +
                   f"(rejected: {self.shares_rejected})")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Simulated Cryptocurrency Miner with Slack Reporting")
    
    parser.add_argument("--slack-webhook-url", type=str, 
                        default=os.environ.get("SLACK_WEBHOOK_URL", ""),
                        help="Slack webhook URL for sending reports")
    
    parser.add_argument("--beacon-interval", type=int, 
                        default=int(os.environ.get("BEACON_INTERVAL", "30")),
                        help="Interval between Slack reports in seconds")
    
    parser.add_argument("--algo", type=str, 
                        default=os.environ.get("ALGO", "ethash"),
                        choices=["ethash", "sha256", "scrypt", "randomx", "cryptonight"],
                        help="Mining algorithm to simulate")
    
    parser.add_argument("--wallet", type=str,
                        default=os.environ.get("WALLET", "0x0000000000000000000000000000000000000000"),
                        help="Wallet address for mining simulation")
    
    parser.add_argument("--worker", type=str, 
                        default=os.environ.get("WORKER", f"worker-{socket.gethostname()}"),
                        help="Worker name for the mining simulation")
    
    parser.add_argument("--threads", type=int, 
                        default=int(os.environ.get("THREADS", str(max(1, multiprocessing.cpu_count() - 1)))),
                        help="Number of CPU threads to simulate mining on")
    
    parser.add_argument("--use-gpu", action="store_true",
                        default=os.environ.get("USE_GPU", "false").lower() == "true",
                        help="Simulate GPU mining behavior")
    
    parser.add_argument("--intensity", type=int, 
                        default=int(os.environ.get("INTENSITY", "8")),
                        choices=range(1, 11),
                        help="Mining intensity (1-10)")
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # Ensure Slack webhook URL is set
    if not args.slack_webhook_url:
        logger.error("Slack webhook URL is required. Please set the SLACK_WEBHOOK_URL environment variable or use --slack-webhook-url.")
        sys.exit(1)
    
    miner = FakeMiner(args)
    
    try:
        miner.start()
    except KeyboardInterrupt:
        miner.stop()
