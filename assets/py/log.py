import os
import base64
import json
import re
import numpy as np
from datetime import datetime
from PySide6.QtCore import QObject, Slot, Signal, Property
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import sys
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_path, relative_path)

class BackendClass_log(QObject):
    # Add progress signal for frontend updates
    progressSignal = Signal(int, str)
    
    def __init__(self):
        super().__init__()
        self.base_folder = os.path.abspath('collected_logs/upload_log')
        # Create base folders if they don't exist
        os.makedirs(self.base_folder, exist_ok=True)
        self.setup_anomaly_patterns()
        

    
    @Slot(str, str, result=str)
    def save_log_file(self, filename, base64_data):
        try:
            # Define directory structure
            today = datetime.now().strftime('%Y-%m-%d')
            date_folder = os.path.join(self.base_folder, today)

            # Create folders if they don't exist
            os.makedirs(date_folder, exist_ok=True)

            # Full path to save file
            file_path = os.path.join(date_folder, filename)

            # Decode and write the file
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(base64_data))

            result = {
                "success": True,
                "message": f"File saved successfully",
                "path": file_path,
                "folder": today
            }
            
            print(f"✅ File saved: {file_path}")
            return json.dumps(result)

        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            print(f"❌ {error_msg}")
            return json.dumps({"success": False, "message": error_msg})

    @Slot(result=str)
    def list_folders(self):
        try:
            # Get folders in the log directory
            folders = []
            if os.path.exists(self.base_folder):
                for item in os.listdir(self.base_folder):
                    item_path = os.path.join(self.base_folder, item)
                    if os.path.isdir(item_path):
                        folders.append(item)
            
            # Sort folders by name (descending to show newest first)
            folders.sort(reverse=True)
            
            # Make sure we return a valid JSON array
            return json.dumps(folders)
        except Exception as e:
            print(f"❌ Error listing folders: {e}")
            return json.dumps([])  # Return empty array as fallback

    @Slot(str, result=str)
    def list_files_in_folder(self, folder_name):
        try:
            folder_path = os.path.join(self.base_folder, folder_name)
            files = []
            
            if os.path.exists(folder_path):
                # List only files (not directories)
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isfile(item_path):
                        files.append(item)
            
            # Sort files alphabetically
            files.sort()
            
            return json.dumps({
                "success": True,
                "folder": folder_name,
                "files": files,
                "count": len(files)
            })
        except Exception as e:
            error_msg = f"Error listing files: {str(e)}"
            print(f"❌ {error_msg}")
            return json.dumps({"success": False, "message": error_msg})

    @Slot(str, str, result=str)
    def read_log_file(self, folder_name, file_name):
        try:
            file_path = os.path.join(self.base_folder, folder_name, file_name)
            
            if not os.path.exists(file_path):
                return json.dumps({
                    "success": False,
                    "message": f"File not found: {file_path}"
                })
            
            # Get file creation time
            import datetime
            file_stats = os.stat(file_path)
            creation_time = file_stats.st_ctime
            creation_time_str = datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            return json.dumps({
                "success": True,
                "folder": folder_name,
                "file": file_name,
                "content": content,
                "created_at": creation_time_str
            })
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            print(f"❌ {error_msg}")
            return json.dumps({"success": False, "message": error_msg})

    @Slot(str, str, result=str)
    def search_in_logs(self, folder_name, search_term):
        """Search for a term in all log files in a folder"""
        try:
            folder_path = os.path.join(self.base_folder, folder_name)
            results = []
            
            if not os.path.exists(folder_path):
                return json.dumps({
                    "success": False,
                    "message": f"Folder not found: {folder_path}"
                })
            
            # Search in each file
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                            
                        # Find all occurrences
                        matches = []
                        lines = content.split('\n')
                        for line_number, line in enumerate(lines, 1):
                            if search_term.lower() in line.lower():
                                matches.append({
                                    "line_number": line_number,
                                    "content": line
                                })
                        
                        if matches:
                            results.append({
                                "file_name": file_name,
                                "matches": matches,
                                "match_count": len(matches)
                            })
                    except Exception as e:
                        print(f"Error searching in file {file_name}: {e}")
            
            return json.dumps({
                "success": True,
                "folder": folder_name,
                "search_term": search_term,
                "results": results,
                "total_files_with_matches": len(results)
            })
        except Exception as e:
            error_msg = f"Error searching logs: {str(e)}"
            print(f"❌ {error_msg}")
            return json.dumps({"success": False, "message": error_msg})
            
    def setup_anomaly_patterns(self):
        """Setup patterns for detecting anomalies in logs"""
        self.anomaly_patterns = {
            "Unusual TCP Flag Sequences": {
                "patterns": [
                    r'(?:SYN-?){3,}',  # SYN flooding
                    r'(?:FIN|RST).*(?:(?!SYN|ACK).)+$',  # FIN/RST without proper handshake
                    r'FLAGS:\s*$',  # NULL packets (no flags)
                    r'FLAGS:\s*SYN.*DST:\s*255\.255\.255\.255',  # SYN to broadcast
                    r'(?:SYN.*?ACK){3,}',  # Repeated SYN-ACK (potential handshake abuse)
                    r'(?:ACK){10,}'  # ACK storm
                ],
                "description": "Unusual sequence of TCP flags that may indicate scanning or abuse",
                "danger_level": "High"
            },
            "Broadcast Traffic Patterns": {
                "patterns": [
                    r'DST:\s*(?:\d+\.){3}255',  # Traffic to broadcast address
                    r'DST:\s*255\.255\.255\.255',  # Traffic to broadcast address
                    r'DST:\s*(?:224|239)\.(?:\d+\.){2}\d+',  # Multicast traffic
                ],
                "description": "High volume of traffic to broadcast addresses",
                "danger_level": "Medium"
            },
            "Multicast DNS Activity": {
                "patterns": [
                    r'DST:\s*224\.0\.0\.251:5353',  # mDNS traffic
                    r'_tcp\.local\.',  # mDNS service discovery
                    r'_udp\.local\.',   # mDNS service discovery
                    r'(?:MDNS|mDNS|multicast DNS).*discovery'  # Explicit mDNS discovery
                ],
                "description": "Unusual mDNS activity that may indicate network enumeration",
                "danger_level": "Low"
            },
            "Unusual DNS Queries": {
                "patterns": [
                    r'(?:QUERY|RESPONSE).*(?:\.local\.|\.local$)',  # Local domain queries
                    r'DNS\s+Query.*(?:_tcp|_udp)\.',  # Service discovery queries
                    r'(?:QUERY|DNS).*[0-9a-f]{16,}',  # Potential DNS tunneling/exfiltration
                    r'QUERY.*(?:\.){5,}',  # Excessive subdomains
                    r'DNS.*(?:\.){30,}',  # Extremely long domain (likely tunneling)
                    r'DNS.*(?:encoding|base64|hex)'  # Keywords suggesting encoding in DNS
                ],
                "description": "Unusual DNS queries that may indicate tunneling or C2",
                "danger_level": "High"
            },
            "External to Internal Communication": {
                "patterns": [
                    r'SRC:\s*(?!10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)(?:\d+\.){3}\d+.*DST:\s*(?:10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)(?:\d+\.){3}\d+',  # External to internal
                    r'SRC:\s*(?!fc00:|fd|fe80:|ff).*DST:\s*(?:fc00:|fd|fe80:|ff)'  # IPv6 variants
                ],
                "description": "External IP addresses communicating with internal networks",
                "danger_level": "Medium"
            },
            "Error & Failure Detection": {
                "patterns": [
                    r'error|failed|failure|exception|crash|segfault|panic|abort|core dump|unreachable|timeout|corrupt|invalid|not found|permission denied|disk full|out of memory|OOM killer|assertion failed|segmentation fault',
                ],
                "description": "System or application errors and failures",
                "danger_level": "Medium"
            },
            "Warning & Critical Events": {
                "patterns": [
                    r'warning|critical|alert|degraded|slow response|retrying|high latency|threshold exceeded|deprecated|unavailable|locked|overload|unresponsive',
                ],
                "description": "Warning or critical system events",
                "danger_level": "Medium"
            },
            "Authentication & Security": {
                "patterns": [
                    r'authentication failed|unauthorized|access denied|invalid credentials|brute force|login attempt|intrusion detected|malware|root access|privilege escalation|SSH failure|port scan|firewall block|DDoS|SQL injection|XSS detected|CVE-',
                    r'(?:failed|invalid)\s+(?:login|authentication).*(?:from|source)\s+\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # Failed login with source IP
                    r'failed\s+password\s+for\s+(?:root|admin|administrator)',  # Failed password for privileged accounts
                    r'multiple\s+authentication\s+failures',  # Multiple auth failures
                    r'access\s+denied\s+for\s+user',  # Access denied for user pattern
                ],
                "description": "Authentication failures or security events",
                "danger_level": "High"
            },
            "Network & Connectivity Issues": {
                "patterns": [
                    r'network unreachable|connection refused|host down|packet loss|latency|DNS failure|IP conflict|ARP spoofing|proxy error|SSL handshake failure|TLS error|certificate expired',
                ],
                "description": "Network or connectivity issues",
                "danger_level": "Medium"
            },
            "System & Resource Monitoring": {
                "patterns": [
                    r'CPU high|memory leak|disk I/O error|swap full|temp high|fan failure|power failure|battery low|process killed|service restart|unexpected shutdown|hardware failure',
                    r'CPU\s+usage[:\s]+(?:9\d|100)%',  # CPU usage over 90%
                    r'memory\s+usage[:\s]+(?:9\d|100)%',  # Memory usage over 90%
                    r'disk\s+usage[:\s]+(?:9\d|100)%',  # Disk usage over 90%
                ],
                "description": "System resource issues or monitoring alerts",
                "danger_level": "High"
            },
            "Logs Specific to Linux Systems": {
                "patterns": [
                    r'kernel panic|dmesg|syslog|journald|auditd|systemd failed|segfault|fsck error|mount failure|Xorg error|module failed|driver crash|SELinux denial|coredump',
                ],
                "description": "Specific log entries from Linux systems",
                "danger_level": "Medium"
            },
            "Logs Specific to Application & Database": {
                "patterns": [
                    r'query timeout|deadlock|transaction aborted|disk quota exceeded|index corruption|read-only mode|backup failed|config error',
                ],
                "description": "Application or database specific log entries",
                "danger_level": "Medium"
            },
            "Suspicious Command Execution": {
                "patterns": [
                    r'exec[ute]*\s+(?:\/bin\/(?:ba|z|c|k|tc)?sh|\||wget|curl|nc|ncat|netcat|bash -i|python -c|perl -e|ruby -e)',
                    r'(?:wget|curl|fetch)\s+(?:https?|ftp):\/\/.*\.(?:sh|pl|py|rb|php|exe|bin|elf)',
                    r'chmod\s+(?:\+|7)[^\/]*x',
                    r'sudo\s+(?:su|bash|sh|\-i|\-s)',
                ],
                "description": "Potentially suspicious command execution",
                "danger_level": "Critical"
            },
            "Data Exfiltration Signs": {
                "patterns": [
                    r'outbound\s+transfer\s+(?:\d+MB|\d+GB)',
                    r'upload.*(?:to|destination).*(?:external|remote|unknown)',
                    r'unusual\s+(?:traffic|data)\s+(?:pattern|volume)',
                    r'large\s+(?:outbound|egress)',
                ],
                "description": "Potential data exfiltration activity",
                "danger_level": "Critical"
            },
            "IoT Specific Anomalies": {
                "patterns": [
                    r'firmware\s+(?:changed|modified|updated|tampered)',
                    r'device\s+(?:reconfigured|reset|initialized)',
                    r'unexpected\s+(?:reboot|restart|shutdown)',
                    r'admin\s+password\s+changed',
                ],
                "description": "Anomalies specific to IoT devices",
                "danger_level": "High"
            },
            "Cloud Infrastructure Anomalies": {
                "patterns": [
                    r'(?:API|access)\s+key\s+(?:created|modified|deleted)',
                    r'(?:S3|Blob|storage)\s+bucket\s+(?:public|exposed|open)',
                    r'(?:IAM|user|permission)\s+(?:modified|escalated|elevated)',
                    r'unusual\s+(?:region|location|geography)',
                ],
                "description": "Anomalies in cloud infrastructure",
                "danger_level": "High"
            }
        }
        
    
    @Slot(str, str, result=str)
    def detect_anomalies(self, folder_path, file_names):
        """
        Detect anomalies in specified log files
        """
        try:
            print(f"🔍 Starting anomaly detection with folder_path: {folder_path}")
            print(f"📁 File names JSON: {file_names[:100]}...")  # Show first 100 chars
            
            # Initial progress update
            self.progressSignal.emit(0, "Starting anomaly detection...")
            
            base_folder = os.path.abspath('collected_logs/upload_log')
            folder_path = os.path.join(base_folder, folder_path)
            print(f"📂 Full folder path resolved: {folder_path}")

            files = json.loads(file_names)
            total_files = len(files)
            print(f"🧾 Total files to analyze: {total_files}")
            
            # Update progress - preparation complete
            self.progressSignal.emit(5, f"Preparing to analyze {total_files} files...")
            
            results = []
            anomaly_stats = {
                "total_files": total_files,
                "total_anomalies": 0,
                "danger_levels": {"High": 0, "Medium": 0, "Low": 0}
            }
            
            for idx, filename in enumerate(files):
                file_path = os.path.join(folder_path, filename)
                print(f"\n📄 Processing file {idx + 1}/{total_files}: {filename}")

                # Signal progress - use a formula that leaves 5% at start and ends at 95%
                # to allow for preparation and finalization steps
                progress = 5 + int(((idx) / total_files) * 90)
                self.progressSignal.emit(progress, f"Processing file {idx + 1} of {total_files}")
                
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    print(f"⚠️ File not found or invalid: {file_path}")
                    continue

                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    lines = content.split('\n')
                    print(f"📝 Total lines in file: {len(lines)}")
                    
                    # Optionally, update progress for large files
                    if len(lines) > 10000:
                        self.progressSignal.emit(progress, f"Processing large file: {filename} ({len(lines)} lines)")

                    for line_number, line in enumerate(lines, 1):
                        for anomaly_name, anomaly_data in self.anomaly_patterns.items():
                            patterns = anomaly_data["patterns"]
                            danger_level = anomaly_data["danger_level"]
                            
                            for pattern in patterns:
                                match = re.search(pattern, line, re.IGNORECASE)
                                if match:
                                    anomaly_stats["total_anomalies"] += 1
                                    anomaly_stats["danger_levels"][danger_level] += 1
                                    
                                    highlighted_log = line.replace(match.group(0), f"<span class='highlight'>{match.group(0)}</span>")
                                    
                                    anomaly_result = {
                                        "anomaly_name": anomaly_name,
                                        "danger_level": danger_level,
                                        "file_name": filename,
                                        "line_number": line_number,
                                        "log_content": highlighted_log,
                                        "raw_content": line
                                    }
                                    results.append(anomaly_result)

                                    print(f"🚨 Anomaly detected: [{danger_level}] {anomaly_name} at line {line_number}")
                                    # Break after first match
                                    break

            # Sort results - update progress to show sorting step
            self.progressSignal.emit(95, "Sorting and finalizing results...")
            print("\n🔃 Sorting results by danger level...")
            danger_level_order = {"High": 0, "Medium": 1, "Low": 2}
            results.sort(key=lambda x: danger_level_order.get(x["danger_level"], 3))

            # Final progress update - complete
            self.progressSignal.emit(100, "Analysis complete")
            print("✅ Anomaly detection completed.")

            response = {
                "success": True,
                "stats": anomaly_stats,
                "results": results
            }

            # Final output
            # print("\n📊 Final Analysis Response:")
            # print(json.dumps(response, indent=4))
            
            return json.dumps(response)

        except Exception as e:
            error_msg = f"❌ Error in anomaly detection: {str(e)}"
            print(error_msg)
            # Report error in progress update
            self.progressSignal.emit(100, f"Error: {str(e)}")
            return json.dumps({"success": False, "message": error_msg})

    def train_initial_model(self):
        """Train an initial ML model with sample data"""
        print("Starting initial model training...")
        # Sample data for training - comprehensive set covering various log types
        X_logs = [
            # Normal system logs
            "System initialized successfully",
            "User logged in",
            "Connection established to server",
            "Scheduled backup completed",
            "Service started successfully",
            "User user123 logged out successfully",
            "Server uptime: 365 days, 4 hours, 23 minutes",
            "Memory usage: 45%, CPU usage: 12%",
            "Disk space available: 345GB",
            "Routine maintenance completed successfully",
            "System updated to version 2.4.5",
            "Configuration changes saved successfully",
            "User preferences updated",
            "Cache cleared automatically",
            "Session timeout after 30 minutes of inactivity",
            
            # Medium risk logs - errors and warnings
            "Error: connection refused",
            "Warning: disk space below 15%",
            "Timeout occurred during backup",
            "Warning: high memory usage detected (87%)",
            "Disk throughput degraded on /dev/sda2",
            "CPU temperature approaching threshold (78°C)",
            "Slow query detected in database (6.2s execution time)",
            "Network latency increased to 250ms",
            "Warning: 5 files skipped during backup",
            "Service restarted automatically after crash",
            "Failed to establish connection with peer node",
            "DNS lookup failed for domain.example.com",
            "SSL certificate will expire in 5 days",
            "Warning: deprecated function called in module authentication.php",
            "Unusual traffic pattern detected on eth0",
            
            # High risk logs
            "Authentication failed: invalid credentials",
            "Failed login attempt for admin account (5th consecutive failure)",
            "Disk full while writing file",
            "Error: SYN flood detected from 192.168.1.5",
            "Critical process unexpectedly terminated",
            "Antivirus detected potential malware: Trojan.GenericKD.45781",
            "Firewall blocked outbound connection to known malicious IP",
            "Error: Database corruption detected in users table",
            "Multiple failed sudo attempts by user guest",
            "Root account accessed from unusual IP address",
            "Error: Invalid SSL certificate presented by remote server",
            "Authentication bypassed for admin portal",
            "Warning: Brute force attempt detected against SSH service",
            "User account locked after multiple failed attempts",
            "Unauthorized file access attempt in /etc/passwd",
            
            # Critical risk logs
            "Network unreachable due to ARP spoofing",
            "Critical alert from systemd",
            "Segmentation fault in application",
            "Possible data exfiltration detected to external IP",
            "Root privileges granted to unauthorized process",
            "Kernel panic - not syncing: Fatal exception",
            "Critical security breach detected in authentication module",
            "Ransomware encryption activity detected",
            "Multiple services crashed simultaneously",
            "Emergency shutdown initiated due to hardware failure",
            "Database encryption keys compromised",
            "Backdoor shell detected on system",
            "Remote code execution attempt through CVE-2023-1234",
            "DDoS attack in progress, network degraded",
            "Unauthorized access to financial records database",
            
            # Network logs
            "03/22 08:51:06 INFO   :...read_physical_netif: index #6, interface LOOPBACK has address 127.0.0.1, ifidx 0",
            "03/22 08:51:06 INFO   :...read_physical_netif: index #5, interface CTCD2 has address 9.67.117.98, ifidx 5",
            "03/22 08:52:50 TRACE  :........router_forward_getOI: out inf: 9.67.116.98",
            "03/22 08:52:50 TRACE  :.......event_establishSessionSend: found outgoing if=9.67.116.98 through forward engine",
            "03/22 08:52:50 TRACE  :......rsvp_event_mapSession: Session=9.67.116.99:1047:6 exists",
            "2025-01-27 13:04:09.097095 - TCP - SRC: 10.5.88.255:64770, DST: 103.243.115.26:80, FLAGS: A",
            "2025-01-27 13:04:09.155784 - DNS Query - SRC: N/A, QUERY: _spotify-social-listening._tcp.local.",
            "2025-01-27 13:04:09.172896 - UDP - SRC: 10.5.98.161:5353, DST: 224.0.0.251:5353",
            "May 24 12:13:06 server01 kernel: [  137.285832] device eth0 entered promiscuous mode",
            "Apr 15 23:17:01 webserver sshd[23742]: Failed password for root from 182.100.67.115 port 43815 ssh2",
            "Jan 5 10:15:15 appserver01 haproxy[12345]: 192.168.1.140:53932 [05/Jan/2025:10:15:15.123] frontend~ backend/server1 0/0/10/30/40 200 1500 - - ---- 1/1/0/0/0 0/0 {Mozilla/5.0} {session=abc123} \"GET /api/status HTTP/1.1\"",
            "Jun 7 06:45:12 mailserver postfix/smtpd[1234]: connect from unknown[192.168.1.87]",
            "Aug 12 15:22:48 fileserver kernel: [234971.123456] [UFW BLOCK] IN=eth0 OUT= MAC=00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd SRC=10.0.0.1 DST=10.0.0.2 LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=11647 DF PROTO=TCP SPT=57786 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0",
            
            # Web server logs
            "192.168.1.100 - user123 [25/Jan/2025:14:12:13 +0000] \"GET /index.html HTTP/1.1\" 200 4523 \"https://example.com/\" \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\"",
            "10.0.0.5 - - [25/Jan/2025:14:15:32 +0000] \"POST /api/login HTTP/1.1\" 401 289 \"https://example.com/login\" \"Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)\"",
            "10.0.0.5 - - [25/Jan/2025:14:15:35 +0000] \"POST /api/login HTTP/1.1\" 401 289 \"https://example.com/login\" \"Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)\"",
            "10.0.0.5 - - [25/Jan/2025:14:15:40 +0000] \"POST /api/login HTTP/1.1\" 401 289 \"https://example.com/login\" \"Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)\"",
            "192.168.1.54 - admin [25/Jan/2025:14:20:55 +0000] \"GET /admin/dashboard HTTP/1.1\" 200 15432 \"https://example.com/admin\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\"",
            "10.0.0.7 - - [25/Jan/2025:14:22:13 +0000] \"GET /images/header.jpg HTTP/1.1\" 304 0 \"https://example.com/products\" \"Mozilla/5.0 (Windows NT 10.0; Win64; x64)\"",
            "45.23.126.92 - - [25/Jan/2025:14:25:19 +0000] \"GET /wp-login.php HTTP/1.1\" 404 523 \"-\" \"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)\"",
            "45.23.126.92 - - [25/Jan/2025:14:25:20 +0000] \"GET /admin.php HTTP/1.1\" 404 523 \"-\" \"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)\"",
            "45.23.126.92 - - [25/Jan/2025:14:25:21 +0000] \"GET /config.php HTTP/1.1\" 404 523 \"-\" \"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)\"",
            "192.168.1.25 - - [25/Jan/2025:15:01:13 +0000] \"GET /product/12345 HTTP/1.1\" 200 8765 \"https://example.com/category/electronics\" \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\"",
            
            # Database logs
            "2025-01-25 14:30:15 [INFO] [DB2] Connection pool initialized with 20 connections",
            "2025-01-25 14:32:45 [WARN] [MySQL] Slow query: SELECT * FROM orders WHERE date > '2024-01-01' AND status = 'pending' (execution time: 2.5s)",
            "2025-01-25 14:35:12 [ERROR] [Postgres] Failed to connect to database: connection refused",
            "2025-01-25 14:40:22 [INFO] [MongoDB] Index created on collection 'users', fields: {email: 1, username: 1}",
            "2025-01-25 14:45:55 [WARN] [MySQL] Lock wait timeout exceeded; try restarting transaction",
            "2025-01-25 14:50:12 [ERROR] [Oracle] ORA-00054: resource busy and acquire with NOWAIT specified or timeout expired",
            "2025-01-25 14:55:30 [CRITICAL] [MySQL] Table './ecommerce/orders' is marked as crashed and should be repaired",
            "2025-01-25 15:00:01 [INFO] [DB2] Backup completed successfully. 1.2GB compressed to archive",
            "2025-01-25 15:05:45 [WARN] [Postgres] Autovacuum: VACUUM ANALYZE public.users (to prevent wraparound)",
            "2025-01-25 15:10:22 [ERROR] [MySQL] Error 1062: Duplicate entry '12345' for key 'PRIMARY'",
            
            # Application logs
            "2025-01-26 09:15:32 [INFO] [AppServer] Application started on port 8080",
            "2025-01-26 09:20:15 [DEBUG] [AuthModule] User authentication request received for username: john.doe",
            "2025-01-26 09:20:16 [INFO] [AuthModule] User john.doe authenticated successfully",
            "2025-01-26 09:25:43 [WARN] [PaymentGateway] Payment processing delayed, external API response time: 3.5s",
            "2025-01-26 09:30:12 [ERROR] [OrderProcessor] Failed to process order #1234567: inventory check failed",
            "2025-01-26 09:35:28 [INFO] [EmailService] 50 notification emails queued for delivery",
            "2025-01-26 09:40:55 [DEBUG] [CacheManager] Cache hit ratio: 78.5% for product catalog",
            "2025-01-26 09:45:12 [WARN] [APIHandler] Rate limit approaching for client 'mobile-app-v3': 950/1000 requests",
            "2025-01-26 09:50:39 [ERROR] [FileManager] Could not write to log directory: permission denied",
            "2025-01-26 09:55:14 [CRITICAL] [AppServer] Unhandled exception in thread 'main': NullPointerException at com.example.service.UserManager.processRequest(UserManager.java:245)",

            # System logs (Windows and Linux)
            "2025-01-26 10:05:22 [INFO] [Windows] User SYSTEM logged on from LOCAL",
            "2025-01-26 10:10:37 [WARN] [Windows] Failed to apply security policy: Access denied",
            "2025-01-26 10:15:44 [ERROR] [Windows] Service 'Print Spooler' failed to start. Error 1053: The service did not respond in a timely fashion",
            "Jan 26 10:20:15 ubuntu-server systemd[1]: Started Daily apt activities.",
            "Jan 26 10:25:32 ubuntu-server kernel: [42689.234567] Out of memory: Killed process 12345 (java) total-vm:8169348kB, anon-rss:7836912kB",
            "Jan 26 10:30:48 ubuntu-server sshd[5678]: Accepted publickey for admin from 10.0.0.15 port 52413 ssh2: RSA SHA256:abc123def456",
            "Jan 26 10:35:59 ubuntu-server sudo: user1 : TTY=pts/2 ; PWD=/home/user1 ; USER=root ; COMMAND=/usr/bin/apt update",
            "330 - Mon Jan 27 13:01:48 2025 - ESENT - ('Video.UI', '17616,D,2,0', '{897060D4-9ADA-4F8B-ABF5-E503B42E8604}: ', 'C:\\Users\\91940\\AppData\\Local\\Packages\\Microsoft.ZuneVideo_8wekyb3d8bbwe\\LocalState\\Database\\828a233f8d8c3f4e\\tmp.edb', '0x410022D8 (8920 | JET_efvAllowHigherPersistedFormat)', '8920 (0x22d8)', '9620 (0x2594)') - User  IP: No IP Address",
            
            # Security logs
            "Jan 26 12:05:18 securityapp [INFO] Login successful for user admin from IP 10.0.0.15",
            "Jan 26 12:10:27 securityapp [WARN] Multiple failed login attempts detected for user root from IP 103.158.42.73",
            "Jan 26 12:15:36 securityapp [ALERT] Possible brute force attack detected: 50 failed login attempts in 2 minutes from IP 103.158.42.73",
            "Jan 26 12:20:44 securityapp [CRITICAL] Intrusion detection: SQL injection attempt in login form",
            "Jan 26 12:25:53 securityapp [ERROR] File integrity check failed for /etc/passwd - checksum mismatch",
            "Jan 26 12:30:12 securityapp [WARN] Unusual outbound connection from server to IP 185.209.135.64:8545",
            "Jan 26 12:35:25 securityapp [CRITICAL] Virus scan detected malware: Win32.Ransomware.WannaCrypt in file /downloads/invoice.pdf.exe",
            "Jan 26 12:40:38 securityapp [ALERT] Privilege escalation detected: user guest executed command with root privileges",
            "Jan 26 12:45:47 securityapp [WARN] SSL certificate validation failed for connection to payment.example.com",
            "Jan 26 12:50:59 securityapp [INFO] Firewall updated with new ruleset. 5 rules added, 2 rules modified"
        ]
        
        # Generate risk labels for the sample data
        # 0: Normal, 1: Low, 2: Medium, 3: High, 4: Critical
        y_risk = [
            # Normal system logs (20)
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            
            # Medium risk logs (15)
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            
            # High risk logs (15)
            3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            
            # Critical risk logs (15)
            4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
            
            # Network logs (13)
            0, 0, 0, 0, 0, 1, 1, 1, 0, 3, 0, 0, 2,
            
            # Web server logs (10)
            0, 2, 3, 4, 0, 0, 1, 2, 3, 0,
            
            # Database logs (10)
            0, 2, 3, 0, 2, 3, 4, 0, 1, 2,
            
            # Application logs (10)
            0, 0, 0, 1, 3, 0, 0, 1, 3, 4,
            
            # System logs (8)
            0, 2, 3, 0, 4, 0, 0, 0,
            
            # Security logs (10)
            0, 2, 3, 4, 3, 2, 4, 4, 2, 0
        ]
        
        print(f"Training data loaded: {len(X_logs)} log samples")
        
        # Convert numeric risk levels to categorical labels
        risk_mapping = {0: "Normal", 1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
        y_labels = [risk_mapping[y] for y in y_risk]
        
        print(f"Risk levels distribution: {pd.Series(y_labels).value_counts().to_dict()}")
        
        # Create a DataFrame to make it easier to work with the data
        self.training_data = pd.DataFrame({
            'log': X_logs,
            'risk_level': y_labels
        })
        
        print("Creating vectorizer...")
        # Create features using CountVectorizer (bag of words)
        self.vectorizer = CountVectorizer(
            max_features=1000,       # Limit features to prevent overfitting
            min_df=2,                # Ignore terms that appear in less than 2 docs
            max_df=0.95,             # Ignore terms that appear in more than 95% of docs
            ngram_range=(1, 2)       # Use both unigrams and bigrams
        )
        
        print("Creating classifier...")
        # Train the Random Forest classifier
        self.classifier = RandomForestClassifier(
            n_estimators=100,         # Number of trees
            max_depth=20,             # Maximum depth of trees
            min_samples_split=2,      # Minimum samples required to split
            min_samples_leaf=1,       # Minimum samples required at leaf node
            class_weight='balanced',  # Balance class weights
            random_state=42           # For reproducibility
        )
        
        print("Creating pipeline...")
        # Create a pipeline that vectorizes the text and then classifies it
        self.model = Pipeline([
            ('vectorizer', self.vectorizer),
            ('classifier', self.classifier)
        ])
        
        print("Fitting model...")
        # Fit the model on the training data
        self.model.fit(self.training_data['log'], self.training_data['risk_level'])
        
        print("Model training complete!")
        
        # Optional: Save the model for future use
        try:
            model_dir = os.path.abspath('./models')
            print(f"Saving model to directory: {model_dir}")
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, 'log_analysis_model.joblib')
            joblib.dump(self.model, model_path)
            print(f"Model saved successfully to {model_path}")
        except Exception as e:
            print(f"⚠️ Could not save model: {e}")

    @Slot(str, str, result=str)
    def perform_deep_analysis(self, folder_path, file_names):
        """
        Perform deep analysis using Random Forest on log files
        
        Args:
            folder_path: Path to folder containing log files
            file_names: JSON string containing array of file names to analyze
        """
        try:
            # Initial progress update
            self.progressSignal.emit(0, "Starting deep analysis...")
            
            print(f"🔍 Starting deep analysis with folder_path: {folder_path}")
            print(f"📁 File names JSON: {file_names[:100]}...") # Print first 100 chars to avoid excessive output
            
            base_folder = os.path.abspath('collected_logs/upload_log')
            folder_path = os.path.join(base_folder, folder_path)
            print(f"📂 Full folder path: {folder_path}")
            
            files = json.loads(file_names)
            print(f"📋 Total files to analyze: {len(files)}")
            
            # Progress update
            self.progressSignal.emit(5, f"Validating {len(files)} files...")
            
            # Validate paths for security
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                print(f"❌ Invalid folder path: {folder_path}")
                self.progressSignal.emit(100, "Error: Invalid folder path")
                return json.dumps({"success": False, "message": "Invalid folder path"})
            
            # Load the trained model if it exists, otherwise create a new one
            self.progressSignal.emit(10, "Loading analysis model...")
            
            model_path = os.path.abspath('./models/log_analysis_model.joblib')
            print(f"🔍 Looking for model at: {model_path}")
            if os.path.exists(model_path):
                try:
                    print("📊 Loading existing model from disk...")
                    self.model = joblib.load(model_path)
                    print("✅ Loaded existing model from disk")
                except Exception as e:
                    print(f"⚠️ Could not load model, training new one: {e}")
                    self.progressSignal.emit(15, "Training new model...")
                    self.train_initial_model()
            else:
                print("🔄 Model file not found, training new model")
                self.progressSignal.emit(15, "Training new model...")
                self.train_initial_model()
            
            # Progress update
            self.progressSignal.emit(20, "Model ready, starting file analysis...")
            
            total_files = len(files)
            analysis_results = []
            
            # Process files with progress updates
            for idx, filename in enumerate(files):
                file_path = os.path.join(folder_path, filename)
                # Signal progress - allocate 20% to 90% of progress for file processing
                progress = 20 + int((idx / total_files) * 70)
                progress_msg = f"Analyzing file {idx+1} of {total_files}: {filename}"
                print(f"📊 Progress: {progress}% - {progress_msg}")
                self.progressSignal.emit(progress, progress_msg)
                
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    print(f"⚠️ File does not exist or is not a file: {file_path}")
                    continue
                
                print(f"📄 Reading file: {file_path}")
                # Read the file content
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    print(f"📋 File {filename} has {len(lines)} lines")
                    
                    # For very large files, provide additional progress updates
                    if len(lines) > 10000:
                        self.progressSignal.emit(progress, f"Processing large file {filename} ({len(lines)} lines)")
                    
                    file_results = {
                        "file_name": filename,
                        "total_lines": len(lines),
                        "risk_prediction": {
                            "Critical": 0,
                            "High": 0,
                            "Medium": 0,
                            "Low": 0,
                            "Normal": 0
                        },
                        "line_analysis": []
                    }
                    
                    # Process non-empty lines
                    valid_lines = [line for line in lines if line.strip()]
                    print(f"📋 Valid non-empty lines: {len(valid_lines)}")
                    
                    # Batch prediction for efficiency
                    if valid_lines:
                        print(f"🧠 Making predictions for {len(valid_lines)} lines in {filename}...")
                        # Use the trained model to predict risk levels
                        predicted_risks = self.model.predict(valid_lines)
                        
                        # Get prediction probabilities to assess confidence
                        prediction_probs = self.model.predict_proba(valid_lines)
                        
                        print(f"🔍 Vectorizing lines for feature importance analysis...")
                        # Get feature importance for each line
                        # We need to vectorize the text first to get the features
                        vectorized_lines = self.model.named_steps['vectorizer'].transform(valid_lines)
                        feature_names = self.model.named_steps['vectorizer'].get_feature_names_out()
                        
                        # Loop through lines and predictions
                        print(f"📝 Processing prediction results and extracting key features...")
                        for line_idx, (line_number, line, risk_level, probs) in enumerate(
                                zip(range(1, len(valid_lines) + 1), valid_lines, predicted_risks, prediction_probs)):
                            
                            # Update risk count in file results
                            file_results["risk_prediction"][risk_level] += 1
                            
                            # Skip Normal logs unless they have unusual patterns
                            if risk_level == "Normal" and max(probs) > 0.9:
                                continue
                            
                            # Get feature importance for this specific line
                            if risk_level != "Normal":
                                # Get the sparse vector for this line
                                line_vector = vectorized_lines[line_idx]
                                
                                # Get the non-zero feature indices and their values
                                feature_indices = line_vector.indices
                                feature_values = line_vector.data
                                
                                # Get the most important features (words) for this prediction
                                important_features = []
                                for idx, value in zip(feature_indices, feature_values):
                                    if idx < len(feature_names):
                                        feature = feature_names[idx]
                                        # Find and highlight this feature in the line
                                        if " " in feature:  # Bigram
                                            parts = feature.split()
                                            # Check if both parts are in the line
                                            if all(part.lower() in line.lower() for part in parts):
                                                important_features.append(feature)
                                        elif feature.lower() in line.lower():
                                            important_features.append(feature)
                                
                                # Sort by importance (approximated by frequency in training data)
                                important_features = sorted(important_features)[:5]  # Limit to top 5
                                risk_type = self.classify_risk_type(line, important_features)

                                # Create highlighted log content
                                highlighted_log = line
                                for feature in important_features:
                                    # Case-insensitive replacement with HTML highlighting
                                    pattern = re.compile(re.escape(feature), re.IGNORECASE)
                                    highlighted_log = pattern.sub(
                                        lambda m: f"<span class='highlight'>{m.group(0)}</span>", 
                                        highlighted_log
                                    )
                                
                                # Add line analysis
                                line_result = {
                                    "line_number": line_number,
                                    "risk_level": risk_level,
                                    "risk_type": risk_type,  # Add this line
                                    "confidence": float(max(probs)),  # Convert numpy float to Python float
                                    "log_content": highlighted_log,
                                    "raw_content": line,
                                    "indicators": important_features
                                }
                                file_results["line_analysis"].append(line_result)
                    
                    # Calculate overall risk level for file
                    risk_hierarchy = ["Critical", "High", "Medium", "Low", "Normal"]
                    for risk in risk_hierarchy:
                        if file_results["risk_prediction"][risk] > 0:
                            file_results["overall_risk"] = risk
                            break
                    else:
                        file_results["overall_risk"] = "Normal"
                    
                    print(f"📊 File {filename} analysis complete. Overall risk: {file_results.get('overall_risk', 'Unknown')}")
                    print(f"📊 Risk breakdown: {file_results['risk_prediction']}")
                    
                    analysis_results.append(file_results)
            
            # Sort analysis results by overall risk level
            self.progressSignal.emit(90, "Finalizing analysis...")
            
            risk_level_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Normal": 4}
            
            print("🔄 Sorting analysis results by risk level...")
            # Sort the file-level results
            analysis_results.sort(key=lambda x: risk_level_order.get(x["overall_risk"], 5))
            
            # Sort line analysis within each file by risk level and confidence
            for file_result in analysis_results:
                file_result["line_analysis"].sort(
                    key=lambda x: (risk_level_order.get(x["risk_level"], 5), -x.get("confidence", 0))
                )
            
            # Calculate aggregate statistics
            self.progressSignal.emit(95, "Calculating statistics...")
            print("📊 Calculating aggregate statistics...")
            total_risk_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Normal": 0}
            for file_result in analysis_results:
                for level, count in file_result["risk_prediction"].items():
                    total_risk_counts[level] += count
            
            print(f"📊 Total risk counts across all files: {total_risk_counts}")
            
            # Determine overall analysis risk level
            overall_analysis_risk = "Normal"  # Default value
            for risk in risk_hierarchy:
                if total_risk_counts[risk] > 0:
                    overall_analysis_risk = risk
                    break
            
            print(f"🚨 Overall analysis risk level: {overall_analysis_risk}")
            
            # Final progress signal
            self.progressSignal.emit(100, "Deep analysis complete")
            print("✅ Deep analysis complete!")
            
            # Final results
            response = {
                "success": True,
                "stats": {
                    "total_files": total_files,
                    "risk_counts": total_risk_counts,
                    "overall_risk": overall_analysis_risk
                },
                "file_results": analysis_results
            }
            return json.dumps(response)
            
        except Exception as e:
            error_msg = f"❌ Error in deep analysis: {str(e)}"
            print(error_msg)
            # Report error in progress update
            self.progressSignal.emit(100, f"Error: {str(e)}")
            return json.dumps({"success": False, "message": error_msg})   
    
    def classify_risk_type(self, content, indicators=None):
        """
        Classify the type of risk based on content and indicators
        
        Args:
            content: The log line content
            indicators: List of indicator words from NLP analysis
        
        Returns:
            String representing the risk type
        """
        risk_type_patterns = {
            "Authentication & Security": r'authentication failed|unauthorized|access denied|invalid credentials|brute force|login attempt|intrusion detected|malware|root access|privilege escalation|SSH failure|port scan|firewall block|DDoS|SQL injection|XSS detected|CVE-',
            "Network & Connectivity": r'network unreachable|connection refused|host down|packet loss|latency|DNS failure|IP conflict|ARP spoofing|proxy error|SSL handshake failure|TLS error|certificate expired',
            "System Resources": r'CPU high|memory leak|disk I/O error|swap full|temp high|fan failure|power failure|battery low|process killed|service restart|unexpected shutdown|hardware failure',
            "Unusual TCP Activity": r'(?:SYN-?){3,}|(?:FIN|RST).*(?:(?!SYN|ACK).)+$|FLAGS:\s*$|FLAGS:\s*SYN.*DST:\s*255\.255\.255\.255',
            "Broadcast & Multicast": r'DST:\s*(?:\d+\.){3}255|DST:\s*255\.255\.255\.255|DST:\s*224\.0\.0\.251:5353|_tcp\.local\.|_udp\.local\.',
            "DNS Anomalies": r'(?:QUERY|RESPONSE).*(?:\.local\.|\.local$)|DNS\s+Query.*(?:_tcp|_udp)\.|(?:QUERY|DNS).*[0-9a-f]{16,}|QUERY.*(?:\.){5,}',
            "External Traffic": r'SRC:\s*(?!10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)(?:\d+\.){3}\d+.*DST:\s*(?:10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)(?:\d+\.){3}\d+',
            "System Errors": r'error|failed|failure|exception|crash|segfault|panic|abort|core dump|unreachable|timeout|corrupt|invalid|not found|permission denied|disk full|out of memory|OOM killer|assertion failed|segmentation fault',
            "Warning Events": r'warning|critical|alert|degraded|slow response|retrying|high latency|threshold exceeded|deprecated|unavailable|locked|overload|unresponsive',
            "Linux System": r'kernel panic|dmesg|syslog|journald|auditd|systemd failed|segfault|fsck error|mount failure|Xorg error|module failed|driver crash|SELinux denial|coredump',
            "Database Issues": r'query timeout|deadlock|transaction aborted|disk quota exceeded|index corruption|read-only mode|backup failed|config error'
        }
        
        # Check content against patterns
        if content:
            for risk_type, pattern in risk_type_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    return risk_type
        
        # Check indicators for matches if no match found in content
        if indicators and len(indicators) > 0:
            indicators_text = " ".join(indicators).lower()
            for risk_type, pattern in risk_type_patterns.items():
                # Extract key terms from pattern
                key_terms = pattern.split('|')
                for term in key_terms:
                    # Clean up the term
                    clean_term = re.sub(r'[\(\)\[\]\{\}\.\*\+\?\|\^\$\\]', '', term).strip()
                    if clean_term and len(clean_term) > 3 and clean_term.lower() in indicators_text:
                        return risk_type
        
        # Default if no specific type is identified
        return "Unclassified"
    
    @Slot(str, str, str, result=str)
    def export_analysis_to_csv(self, analysis_type, folder_path, data):
        """
        Export analysis results to CSV file
        
        Args:
            analysis_type: Either 'anomaly' or 'deep_analysis'
            folder_path: Original folder path for reference
            data: JSON string of analysis data to export
        """
        try:
            # Create downloads directory if it doesn't exist
            downloads_dir = os.path.expanduser("~/Downloads")
            if not os.path.exists(downloads_dir):
                downloads_dir = os.path.abspath("./downloads")
                os.makedirs(downloads_dir, exist_ok=True)
            
            # Parse the analysis data
            analysis_data = json.loads(data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if analysis_type == "anomaly":
                # Prepare CSV file for anomaly detection results
                filename = f"anomaly_analysis_{timestamp}.csv"
                filepath = os.path.join(downloads_dir, filename)
                
                # Create DataFrame for anomalies
                rows = []
                for item in analysis_data.get("results", []):
                    rows.append({
                        "Anomaly Type": item.get("anomaly_name", "Unknown"),
                        "Danger Level": item.get("danger_level", "Unknown"),
                        "File Name": item.get("file_name", "Unknown"),
                        "Line Number": item.get("line_number", 0),
                        "Log Content": item.get("raw_content", "")
                    })
                
                if rows:
                    df = pd.DataFrame(rows)
                    df.to_csv(filepath, index=False)
                else:
                    return json.dumps({
                        "success": False,
                        "message": "No anomaly data to export"
                    })
            
            elif analysis_type == "deep_analysis":
                # Prepare CSV file for deep analysis results
                filename = f"deep_analysis_{timestamp}.csv"
                filepath = os.path.join(downloads_dir, filename)
                
                # Create DataFrame for deep analysis
                rows = []
                for file_result in analysis_data.get("file_results", []):
                    file_name = file_result.get("file_name", "Unknown")
                    overall_risk = file_result.get("overall_risk", "Unknown")
                    
                    for line_analysis in file_result.get("line_analysis", []):
                        rows.append({
                            "File Name": file_name,
                            "Overall File Risk": overall_risk,
                            "Line Number": line_analysis.get("line_number", 0),
                            "Risk Level": line_analysis.get("risk_level", "Unknown"),
                            "Indicators": ", ".join(line_analysis.get("indicators", [])),
                            "Log Content": line_analysis.get("raw_content", "")
                        })
                
                if rows:
                    df = pd.DataFrame(rows)
                    df.to_csv(filepath, index=False)
                else:
                    return json.dumps({
                        "success": False,
                        "message": "No analysis data to export"
                    })
            else:
                return json.dumps({
                    "success": False,
                    "message": f"Unknown analysis type: {analysis_type}"
                })
            
            return json.dumps({
                "success": True,
                "message": f"Data exported successfully to {filename}",
                "path": filepath,
                "filename": filename
            })
            
        except Exception as e:
            error_msg = f"Error exporting data: {str(e)}"
            print(f"❌ {error_msg}")
    
    
