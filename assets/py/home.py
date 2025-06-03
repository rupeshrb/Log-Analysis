import os
import time
import json
import sqlite3
from datetime import datetime, timedelta
import threading
import shutil
import math
from datetime import datetime, timedelta
from pathlib import Path
import ipaddress
from PySide6.QtCore import QObject, Slot, Signal
import winsound 
import sys

# Define a function to get the correct path for resources in both dev and PyInstaller environments
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_path, relative_path)

class BackendClass_hom(QObject):
    # Signals to update frontend
    updateNetworkLog = Signal(str)
    updateAlerts = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.capturing = False
        self.capture_thread = None
        self.db_lock = threading.Lock()
        
        # Cache for aggregated data to reduce database load
        self.data_cache = {
            'network_data': {'data': None, 'timestamp': None},
            'traffic_summary': {'data': None, 'timestamp': None},
            'alerts': {'data': None, 'timestamp': None},
            'log_count': {'data': 0, 'timestamp': None}
        }
        self.sound_enabled = True
        self.sound_frequencies = {
            'high': 1000,    # High severity alerts
            'medium': 750,   # Medium severity alerts
            'low': 500       # Low severity alerts
        }
        self.sound_durations = {
            'high': 1000,    # 1 second for high severity
            'medium': 500,   # 0.5 seconds for medium
            'low': 250       # 0.25 seconds for low
        }
        
        # Cache TTL in seconds
        self.cache_ttl = 3  # Refresh cache every 3 seconds
        
        # Setup directories
        self.setup_directories()
        
        # Setup database
        self.setup_database()
        
        # Start log cleanup timer
        self.setup_database_maintenance()
        
        # Initialize trackers for suspicious activity detection (code omitted for brevity)
        self.init_security_trackers()
    
    def init_security_trackers(self):
        """Initialize security trackers"""
        self.tcp_flag_sequences = {}
        self.broadcast_traffic = {}
        self.last_processed_position = 0
        # Port scan detection
        self.port_scan_tracker = {}
        
        # DNS tunneling detection
        self.dns_query_tracker = {}
        
        # SYN flood detection
        self.syn_flood_tracker = {}
        
        # Data exfiltration detection
        self.data_transfer_tracker = {}
        
        # C2 communication detection
        self.c2_pattern_tracker = {}
        
        # Unusual time activity tracking
        self.active_hours = {}
        self.after_hours_alerted = set()
        
        # Login attempt monitoring
        self.login_attempt_tracker = {}
        
        # Example placeholder for known malicious IPs - replace with actual implementation
        self.malicious_ip_database = {
            # Format: "ip": {"threat_type": "description", "source": "source_name"}
            "192.0.2.1": {"threat_type": "Botnet C2", "source": "Threat Intel Feed"},
            "198.51.100.1": {"threat_type": "Ransomware", "source": "Threat Intel Feed"}
        }
        
        # Example list of Tor exit nodes - replace with actual implementation
        self.tor_exit_nodes = ["198.51.100.5", "203.0.113.7"]
        
        # Example high-risk countries - replace with actual implementation
        self.high_risk_countries = [
            "CN", "KP", "PK", "AF", "BD", "IR", "RU", "BY", "SY", "VE"
        ]
    
    def setup_directories(self):
        """Setup required directories for log storage"""
        base_path = Path("collected_logs/upload_log")
        base_path.mkdir(parents=True, exist_ok=True)
        
        # Create Network Log directory
        self.log_dir = base_path / "Network_Log"
        self.log_dir.mkdir(exist_ok=True)
        
        # Current log file path - mostly for compatibility, not primary storage
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file_path = self.log_dir / f"network_log_{today}.log"
        
        # Create log file if it doesn't exist
        if not self.log_file_path.exists():
            with open(self.log_file_path, 'w') as f:
                f.write(f"# Network Log File - Created on {today}\n")
                
                f.write("# [Timestamp] [Protocol] [Source] -> [Destination] [Flags] [Payloads] [Details]\n")
    
    def setup_database(self):
        """Setup SQLite database for network logs and alerts"""
        db_path = Path("log_analysis.db")
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        
        with self.db_lock:
            cursor = self.conn.cursor()
            
            # Create network logs table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                protocol TEXT,
                src_ip TEXT,
                dst_ip TEXT,
                src_port INTEGER,
                dst_port INTEGER,
                flags TEXT,
                payload_size INTEGER,
                details TEXT
            )
            ''')
            
            # Create alerts table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                alert_type TEXT,
                description TEXT,
                severity TEXT,
                source_ip TEXT,
                details TEXT
            )
            ''')
            
            # Create maintenance log table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action TEXT,
                details TEXT
            )
            ''')
            
            # Create aggregated data cache table for performance
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_aggregates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aggregate_type TEXT UNIQUE,
                data TEXT,
                updated_at TEXT
            )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON network_logs (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_protocol ON network_logs (protocol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_src_ip ON network_logs (src_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_dst_port ON network_logs (dst_port)')
            
            self.conn.commit()
    
    def setup_database_maintenance(self):
        """Setup automated database maintenance"""
        maintenance_thread = threading.Thread(target=self.database_maintenance_task, daemon=True)
        maintenance_thread.start()
    
    def database_maintenance_task(self):
        """Periodically clean up database tables"""
        while True:
            time.sleep(86400)  # Run once a day
            self.perform_database_maintenance()
    
    def perform_database_maintenance(self):
        """Remove log entries older than 10 days and optimize database"""
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                
                # Get current count before deletion
                cursor.execute("SELECT COUNT(*) FROM network_logs")
                before_count = cursor.fetchone()[0]
                
                # Delete network logs older than 10 days
                ten_days_ago = (datetime.now() - timedelta(days=10)).isoformat()
                cursor.execute("DELETE FROM network_logs WHERE timestamp < ?", (ten_days_ago,))
                
                # Delete alerts older than 30 days
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                cursor.execute("DELETE FROM alerts WHERE timestamp < ?", (thirty_days_ago,))
                
                # Delete old aggregate data
                cursor.execute("DELETE FROM data_aggregates WHERE updated_at < ?", (ten_days_ago,))
                
                # Get current count after deletion
                cursor.execute("SELECT COUNT(*) FROM network_logs")
                after_count = cursor.fetchone()[0]
                
                # Log the maintenance action
                details = {
                    "records_before": before_count,
                    "records_after": after_count,
                    "records_deleted": before_count - after_count
                }
                
                cursor.execute(
                    "INSERT INTO maintenance_log (timestamp, action, details) VALUES (?, ?, ?)",
                    (datetime.now().isoformat(), "Database Cleanup", json.dumps(details))
                )
                
                # Optimize database
                cursor.execute("VACUUM")
                
                self.conn.commit()
                
                # Clear the cache after maintenance
                self.clear_cache()
                
        except Exception as e:
            print(f"Error during database maintenance: {e}")
    
    def clear_cache(self):
        """Clear all cached data"""
        for key in self.data_cache:
            self.data_cache[key]['data'] = None
            self.data_cache[key]['timestamp'] = None
    
    @Slot(result=bool)
    def start_capture(self):
        """Start network packet capture"""
        if self.capturing:
            return True
            
        self.capturing = True
        self.capture_thread = threading.Thread(target=self.packet_capture, daemon=True)
        self.capture_thread.start()
        
        # Start the log analysis thread
        self.analysis_thread = threading.Thread(target=self.continuous_log_analysis, daemon=True)
        self.analysis_thread.start()
        
        return True
    
    @Slot(result=bool)
    def stop_capture(self):
        """Stop network packet capture"""
        self.capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1)
        return True
    
    def packet_capture(self):
        """Capture network packets using scapy"""
        try:
            from scapy.all import sniff, IP, TCP, UDP, ICMP, DNS, Raw
            sniff(prn=self.process_packet, store=False, stop_filter=lambda _: not self.capturing)
        except Exception as e:
            print(f"Error in packet capture: {e}")
            self.capturing = False
    
    def process_packet(self, packet):
        """Process captured packet and store in database"""
        try:
            from scapy.all import IP, TCP, UDP, ICMP, DNS, Raw
            timestamp = datetime.now().isoformat()
            
            # Initialize default values
            protocol = "UNKNOWN"
            src_ip = "N/A"
            dst_ip = "N/A"
            src_port = None
            dst_port = None
            flags = "N/A"
            payload_size = None
            details = {}
            
            # Process TCP traffic
            if TCP in packet and IP in packet:
                protocol = "TCP"
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
                flags = str(packet[TCP].flags)
                
                if Raw in packet:
                    payload_size = len(packet[Raw].load)
            
            # Process UDP traffic
            elif UDP in packet and IP in packet:
                protocol = "UDP"
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
                
                if Raw in packet:
                    payload_size = len(packet[Raw].load)
            
            # Process ICMP traffic
            elif ICMP in packet and IP in packet:
                protocol = "ICMP"
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                details["icmp_type"] = packet[ICMP].type
                details["icmp_code"] = packet[ICMP].code
            
            # Process DNS traffic
            elif DNS in packet:
                protocol = "DNS"
                if IP in packet:
                    src_ip = packet[IP].src
                    dst_ip = packet[IP].dst
                
                if packet.haslayer(UDP):
                    src_port = packet[UDP].sport
                    dst_port = packet[UDP].dport
                elif packet.haslayer(TCP):
                    src_port = packet[TCP].sport
                    dst_port = packet[TCP].dport
                
                # Extract DNS query or response
                if packet[DNS].qr == 0:  # Query
                    details["query_type"] = "QUERY"
                    if packet[DNS].qd:
                        details["query"] = packet[DNS].qd.qname.decode('utf-8', errors='ignore')
                elif packet[DNS].qr == 1:  # Response
                    details["query_type"] = "RESPONSE"
                    if packet[DNS].an:
                        try:
                            details["response"] = str(packet[DNS].an.rdata)
                        except:
                            details["response"] = "Unable to decode response"
            
            # Append to log file for reference
            log_line = f"[{timestamp}] [{protocol}] [{src_ip}:{src_port}] -> [{dst_ip}:{dst_port}] [{flags}] [{payload_size}] [{details}]\n"
            try:
                with open(self.log_file_path, 'a') as f:
                    f.write(log_line)
            except Exception as e:
                print(f"Error writing to log file: {e}")
            
            # Insert into database with lock to prevent race conditions
            with self.db_lock:
                try:
                    cursor = self.conn.cursor()
                    cursor.execute(
                        """INSERT INTO network_logs 
                           (timestamp, protocol, src_ip, dst_ip, src_port, dst_port, flags, payload_size, details) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (timestamp, protocol, src_ip, dst_ip, src_port, dst_port, flags, payload_size, json.dumps(details))
                    )
                    self.conn.commit()
                    
                    # Invalidate relevant caches
                    self.data_cache['log_count']['data'] += 1
                    self.data_cache['log_count']['timestamp'] = datetime.now()
                    self.data_cache['network_data']['data'] = None
                    self.data_cache['traffic_summary']['data'] = None
                    
                except Exception as e:
                    print(f"Error inserting into database: {e}")
            
            # Create log entry object for frontend
            log_entry = {
                "timestamp": timestamp,
                "protocol": protocol,
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "flags": flags,
                "details": details
            }
            
            # Signal the frontend with new data (but only send minimal info)
            # This just updates a counter, not the full data
            self.updateNetworkLog.emit(json.dumps({"count": self.data_cache['log_count']['data']}))
            
        except Exception as e:
            print(f"Error processing packet: {e}")
    
    def continuous_log_analysis(self):
        """Continuously analyze logs for suspicious patterns"""
        last_analyzed_id = 0
        
        while self.capturing:
            try:
                time.sleep(2)  # Check every 2 seconds to reduce load
                
                with self.db_lock:
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT MAX(id) FROM network_logs")
                    max_id = cursor.fetchone()[0] or 0
                    
                    if max_id > last_analyzed_id:
                        # Get new logs since last analysis
                        cursor.execute("""
                            SELECT id, timestamp, protocol, src_ip, dst_ip, src_port, dst_port, 
                                   flags, payload_size, details
                            FROM network_logs 
                            WHERE id > ? 
                            ORDER BY id
                            LIMIT 500
                        """, (last_analyzed_id,))
                        
                        new_logs = cursor.fetchall()
                        
                        # Process logs in batches to avoid memory issues
                        for log_row in new_logs:
                            log = {
                                "id": log_row[0],
                                "timestamp": log_row[1],
                                "protocol": log_row[2],
                                "src_ip": log_row[3],
                                "dst_ip": log_row[4],
                                "src_port": log_row[5],
                                "dst_port": log_row[6],
                                "flags": log_row[7],
                                "payload_size": log_row[8],
                                "details": json.loads(log_row[9]) if log_row[9] else {}
                            }
                            
                            self.analyze_log(log)
                        
                        # Update last analyzed ID
                        if new_logs:
                            last_analyzed_id = new_logs[-1][0]
            
            except Exception as e:
                print(f"Error in log analysis: {e}")
                
    # Alternative solution: If you want to keep the original method name but fix the issue
    def analyze_log(self, log):
        """Analyze a single log entry for suspicious patterns"""
        try:
            # Don't iterate - this is already a single log
            # Basic protocol-specific checks
            if log.get("protocol") == "TCP" and log.get("flags") and log["flags"] != "N/A":
                self.check_tcp_flag_sequence(log)
                
                # TCP-specific detection methods
                if log.get("flags") == "S":  # SYN packets
                    self.check_syn_flood(log)
                
                # Port scan detection (for all TCP traffic)
                self.detect_port_scan(log)
                
            # Check for suspicious destinations (applies to all protocols)
            self.check_suspicious_destinations(log)
            
            # Check for known malicious IPs (applies to all protocols)
            self.check_known_malicious_ip(log)
            
            # Check for time anomalies (applies to all protocols)
            self.check_time_anomaly(log)
            
            # Check for broadcast traffic patterns
            if log.get("protocol") in ["UDP", "TCP"] and log.get("dst_ip", "").endswith(".255"):
                self.check_broadcast_traffic(log)
                
            # Protocol-specific checks
            if log.get("protocol") == "DNS":
                self.check_dns_tunneling(log)
                
            if log.get("protocol") == "ARP":
                self.check_arp_spoofing(log)
                
            # Data exfiltration and C2 detection (if log has payload info)
            if log.get("payload_size") is not None:
                self.check_data_exfiltration(log)
                
            elif log.get("details") and "payload_size" in log["details"]:
                self.check_data_exfiltration(log)
                
            # C2 communication pattern detection (for all traffic)
            self.detect_c2_communication(log)
        except Exception as e:
            print(f"Error processing log {log.get('id', 'unknown')}: {e}")
    
    def check_tcp_flag_sequence(self, log):
        """Check for unusual TCP flag sequences"""
        src_ip = log["src_ip"]
        dst_ip = log["dst_ip"]
        flags = log["flags"]
        connection = f"{src_ip}:{log['src_port']}-{dst_ip}:{log['dst_port']}"
        
        if connection not in self.tcp_flag_sequences:
            self.tcp_flag_sequences[connection] = []
        
        self.tcp_flag_sequences[connection].append(flags)
        
        # Keep only the last 5 flags for each connection
        if len(self.tcp_flag_sequences[connection]) > 5:
            self.tcp_flag_sequences[connection].pop(0)
        
        # Check for suspicious patterns like NULL, FIN, XMAS scans
        sequence = "".join(self.tcp_flag_sequences[connection])
        
        # Example: Check for NULL scan (no flags set)
        if "." in flags:  # Scapy represents NULL flags as '.'
            self.create_alert(
                "Unusual TCP Flags",
                f"Possible NULL scan detected from {src_ip}",
                "High",
                src_ip,
                {"flags": flags, "destination": dst_ip}
            )
        
        # Check for FIN scan (only FIN flag)
        if flags == "F" and len(self.tcp_flag_sequences[connection]) >= 3:
            fin_count = sequence.count("F")
            if fin_count >= 3:
                self.create_alert(
                    "Unusual TCP Flags",
                    f"Possible FIN scan detected from {src_ip}",
                    "High",
                    src_ip,
                    {"flags": sequence, "destination": dst_ip}
                )

    def detect_port_scan(self, log):
        """Detect potential port scanning activity"""
        src_ip = log["src_ip"]
        dst_ip = log["dst_ip"]
        dst_port = log["dst_port"]
        
        # Use a time window for detection
        time_window = 60  # seconds
        current_time = datetime.now()
        
        # Initialize if not exists
        if src_ip not in self.port_scan_tracker:
            self.port_scan_tracker[src_ip] = {
                "targets": {},
                "last_reset": current_time
            }
        
        # Check if we need to reset the counter (outside time window)
        if (current_time - self.port_scan_tracker[src_ip]["last_reset"]).total_seconds() > time_window:
            self.port_scan_tracker[src_ip]["targets"] = {}
            self.port_scan_tracker[src_ip]["last_reset"] = current_time
        
        # Track this connection
        if dst_ip not in self.port_scan_tracker[src_ip]["targets"]:
            self.port_scan_tracker[src_ip]["targets"][dst_ip] = set()
        
        self.port_scan_tracker[src_ip]["targets"][dst_ip].add(dst_port)
        
        # Alert if scanning many ports on same IP
        if len(self.port_scan_tracker[src_ip]["targets"][dst_ip]) >= 15:
            ports_scanned = list(self.port_scan_tracker[src_ip]["targets"][dst_ip])
            self.create_alert(
                "Port Scan Detected",
                f"Host {src_ip} scanned {len(ports_scanned)} ports on {dst_ip}",
                "High",
                src_ip,
                {"target_ip": dst_ip, "ports_scanned": ports_scanned[:20]}
            )
            # Reset counter after alert
            self.port_scan_tracker[src_ip]["targets"][dst_ip] = set()
        
        # Alert if scanning multiple IPs
        if len(self.port_scan_tracker[src_ip]["targets"]) >= 10:
            targets = list(self.port_scan_tracker[src_ip]["targets"].keys())
            self.create_alert(
                "Network Scan Detected",
                f"Host {src_ip} scanned {len(targets)} different hosts",
                "High",
                src_ip,
                {"targets": targets[:10]}
            )
            # Reset counter after alert
            self.port_scan_tracker[src_ip] = {
                "targets": {},
                "last_reset": current_time
            }
    import ipaddress

    def get_country_code(self, ip):
        try:
            # Check if the IP is a valid IP address
            if ip == "N/A" or not ip:  # Handle cases where IP is "N/A" or an empty string
                return "XX"  # Return a default country code (Unknown)

            # Validate the IP format using ipaddress module
            ipaddress.ip_address(ip)  # Will raise ValueError if invalid

            # Sample mappings (as before)
            sample_mappings = {
                "103.5.8.": "IN",  # India range
                "103.15.6.": "PK",  # Pakistan range
                "103.9.2.": "BD",  # Bangladesh range
                "103.37.": "CN",  # China range
                "175.45.": "KP",  # North Korea range
                "91.108.": "RU",  # Russia range
                "46.32.": "IR",  # Iran range
                "93.115.": "AF",  # Afghanistan range
            }

            # Check if IP starts with any of our sample prefixes
            for prefix, country in sample_mappings.items():
                if ip.startswith(prefix):
                    return country

            # If no prefix match, use first octet to determine region
            first_octet = int(ip.split('.')[0])
            if 1 <= first_octet <= 127:
                return "US"  # Class A (mostly North America)
            elif 128 <= first_octet <= 191:
                return "EU"  # Class B (mostly Europe)
            elif 192 <= first_octet <= 223:
                return "AP"  # Class C (mostly Asia-Pacific)
            else:
                return "XX"  # Unknown/Special addresses
        except ValueError:
            print(f"Invalid IP address: {ip}")
            return "XX"  # Return unknown code for invalid IP
        except Exception as e:
            print(f"Error in GeoIP lookup: {e}")
            return "XX"  # Return unknown code for any other errors

        
        
    def check_dns_tunneling(self, log):
        """Check for signs of DNS tunneling (data exfiltration via DNS)"""
        if "details" not in log or "query" not in log["details"]:
            return
        
        query = log["details"]["query"]
        src_ip = log["src_ip"]
        
        # Initialize tracker if needed
        if src_ip not in self.dns_query_tracker:
            self.dns_query_tracker[src_ip] = {
                "queries": [],
                "total_bytes": 0,
                "last_check": datetime.now()
            }
        
        # Check time window (reset if needed)
        current_time = datetime.now()
        if (current_time - self.dns_query_tracker[src_ip]["last_check"]).total_seconds() > 60:
            self.dns_query_tracker[src_ip] = {
                "queries": [],
                "total_bytes": 0,
                "last_check": current_time
            }
        
        # Track query and bytes
        self.dns_query_tracker[src_ip]["queries"].append(query)
        self.dns_query_tracker[src_ip]["total_bytes"] += len(query)
        
        # Suspect DNS tunneling if:
        # 1. Many DNS queries in short time
        # 2. Long average query length
        # 3. High entropy in queries (many random-looking subdomains)
        
        queries = self.dns_query_tracker[src_ip]["queries"]
        
        if len(queries) > 20:
            avg_length = self.dns_query_tracker[src_ip]["total_bytes"] / len(queries)
            
            # Check for unusually long average query length
            if avg_length > 50:
                # Calculate entropy of queries to detect randomness
                entropy = self.calculate_entropy(queries)
                
                if entropy > 4.0:  # High entropy threshold
                    self.create_alert(
                        "Possible DNS Tunneling",
                        f"Host {src_ip} making unusual DNS queries (possible data exfiltration)",
                        "High",
                        src_ip,
                        {
                            "query_count": len(queries),
                            "avg_length": avg_length,
                            "entropy": entropy,
                            "sample_queries": queries[-5:]  # Last 5 queries as sample
                        }
                    )
                    # Reset after alert
                    self.dns_query_tracker[src_ip] = {
                        "queries": [],
                        "total_bytes": 0,
                        "last_check": current_time
                    }

    def calculate_entropy(self, strings):
        """Calculate Shannon entropy to detect randomness in strings"""
        # Join all strings
        combined = ''.join(strings)
        
        # Count frequency of each character
        char_count = {}
        for char in combined:
            if char not in char_count:
                char_count[char] = 0
            char_count[char] += 1
        
        # Calculate entropy
        entropy = 0
        for count in char_count.values():
            probability = count / len(combined)
            entropy -= probability * math.log2(probability)
        
        return entropy

    def check_syn_flood(self, log):
        """Check for SYN flood attacks"""
        src_ip = log["src_ip"]
        dst_ip = log["dst_ip"]
        dst_port = log["dst_port"]
        target = f"{dst_ip}:{dst_port}"
        
        # Initialize or update time window
        current_time = datetime.now()
        time_window = 5  # 5 seconds window
        
        if src_ip not in self.syn_flood_tracker:
            self.syn_flood_tracker[src_ip] = {}
        
        if target not in self.syn_flood_tracker[src_ip]:
            self.syn_flood_tracker[src_ip][target] = {
                "count": 0,
                "last_check": current_time
            }
        
        # Reset if outside time window
        if (current_time - self.syn_flood_tracker[src_ip][target]["last_check"]).total_seconds() > time_window:
            self.syn_flood_tracker[src_ip][target] = {
                "count": 1,
                "last_check": current_time
            }
        else:
            self.syn_flood_tracker[src_ip][target]["count"] += 1
        
        # Check for SYN flood (many SYN packets to same target in short time)
        if self.syn_flood_tracker[src_ip][target]["count"] > 30:
            self.create_alert(
                "Possible SYN Flood Attack",
                f"Host {src_ip} sent {self.syn_flood_tracker[src_ip][target]['count']} SYN packets to {target} in {time_window} seconds",
                "Critical",
                src_ip,
                {"target": target, "syn_count": self.syn_flood_tracker[src_ip][target]["count"]}
            )
            # Reset counter after alert
            self.syn_flood_tracker[src_ip][target]["count"] = 0

    def check_suspicious_destinations(self, log):
        """Check for connections to suspicious destinations"""
        dst_ip = log["dst_ip"]
        src_ip = log["src_ip"]
        dst_port = log["dst_port"]
        
        # Check for connections to Tor exit nodes
        if dst_ip in self.tor_exit_nodes:
            self.create_alert(
                "Tor Network Connection",
                f"Host {src_ip} connected to known Tor exit node {dst_ip}",
                "Medium",
                src_ip,
                {"destination": dst_ip, "port": dst_port}
            )
        
        # Check for connections to high-risk countries
        country_code = self.get_country_code(dst_ip)
        if country_code in self.high_risk_countries:
            self.create_alert(
                "Connection to High-Risk Location",
                f"Host {src_ip} connected to {dst_ip} in {country_code}",
                "Medium",
                src_ip,
                {"destination": dst_ip, "country": country_code, "port": dst_port}
            )
        
        # Check for non-standard ports for common protocols
        if dst_port in [8080, 8000, 8888, 8081, 8443] and log["protocol"] == "TCP":
            self.create_alert(
                "Connection to Non-Standard Web Port",
                f"Host {src_ip} connected to {dst_ip} on non-standard web port {dst_port}",
                "Low",
                src_ip,
                {"destination": dst_ip, "port": dst_port}
            )

    def check_broadcast_traffic(self, log):
        """Check for unusual broadcast traffic patterns"""
        src_ip = log["src_ip"]
        protocol = log["protocol"]
        
        if src_ip not in self.broadcast_traffic:
            self.broadcast_traffic[src_ip] = {"count": 0, "last_seen": datetime.now()}
        
        # Update counts
        self.broadcast_traffic[src_ip]["count"] += 1
        self.broadcast_traffic[src_ip]["last_seen"] = datetime.now()
        
        # Alert if too many broadcast packets in short time
        if self.broadcast_traffic[src_ip]["count"] > 10:
            time_diff = datetime.now() - self.broadcast_traffic[src_ip]["last_seen"]
            
            if time_diff.total_seconds() < 60:  # Within a minute
                self.create_alert(
                    "Broadcast Traffic",
                    f"High broadcast traffic from {src_ip} ({self.broadcast_traffic[src_ip]['count']} packets)",
                    "Medium",
                    src_ip,
                    {"protocol": protocol, "count": self.broadcast_traffic[src_ip]["count"]}
                )
                # Reset counter after alert
                self.broadcast_traffic[src_ip]["count"] = 0

    def check_data_exfiltration(self, log):
        """Check for unusual data transfer volumes indicating possible data exfiltration"""
        try:
            src_ip = log.get("src_ip")
            dst_ip = log.get("dst_ip")
            timestamp_str = log.get("timestamp")
            
            # First check if all required fields are present
            if not src_ip or not dst_ip or not timestamp_str:
                return  # Skip this log if crucial fields are missing
            
            # Get payload size, handling both possible locations and formats
            payload_size = None
            
            # Try main payload_size field first
            if log.get("payload_size") is not None:
                try:
                    payload_size = int(log["payload_size"])
                except (ValueError, TypeError):
                    # If it's not convertible to int, ignore it
                    pass
            
            # If not found or not valid, check in details
            if payload_size is None and isinstance(log.get("details"), dict):
                try:
                    if "payload_size" in log["details"]:
                        payload_size = int(log["details"]["payload_size"])
                except (ValueError, TypeError):
                    # If it's not convertible to int, ignore it
                    pass
            
            # If we still don't have a valid payload size, we can't proceed
            if payload_size is None:
                return
                
            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except (ValueError, TypeError):
                return  # Skip if timestamp can't be parsed
                
            # Initialize host data tracker if needed
            if src_ip not in self.data_transfer_tracker:
                self.data_transfer_tracker[src_ip] = {
                    "outbound_bytes": 0,
                    "start_time": timestamp,
                    "destinations": set()
                }
                
            # Update tracker
            self.data_transfer_tracker[src_ip]["outbound_bytes"] += payload_size
            self.data_transfer_tracker[src_ip]["destinations"].add(dst_ip)
                
            # Calculate time elapsed
            time_elapsed = (timestamp - self.data_transfer_tracker[src_ip]["start_time"]).total_seconds()
                
            # Only check if at least 5 minutes have passed
            if time_elapsed > 300:
                # Calculate outbound transfer rate (bytes per second)
                transfer_rate = self.data_transfer_tracker[src_ip]["outbound_bytes"] / time_elapsed
                    
                # Alert if transfer rate exceeds threshold (e.g., 1MB/s)
                if transfer_rate > 1000000:  # 1MB/second
                    self.create_alert(
                        "Large Data Transfer",
                        f"Host {src_ip} transferred {self.data_transfer_tracker[src_ip]['outbound_bytes']/1000000:.2f} MB in {time_elapsed/60:.1f} minutes",
                        "High",
                        src_ip,
                        {
                            "bytes_transferred": self.data_transfer_tracker[src_ip]["outbound_bytes"],
                            "transfer_rate_bps": transfer_rate,
                            "destinations": list(self.data_transfer_tracker[src_ip]["destinations"])
                        }
                    )
                    # Reset tracker after alert
                    self.data_transfer_tracker[src_ip] = {
                        "outbound_bytes": 0,
                        "start_time": timestamp,
                        "destinations": set()
                    }
        except Exception as e:
            print(f"Error in check_data_exfiltration for log {log.get('id', 'unknown')}: {e}")
            # Don't crash the whole analysis process for one problematic log
              
    def check_known_malicious_ip(self, log):
        """Check if IP is in known malicious IP database"""
        src_ip = log["src_ip"]
        dst_ip = log["dst_ip"]
        
        # Check outbound connections to malicious IPs
        if dst_ip in self.malicious_ip_database:
            threat_info = self.malicious_ip_database[dst_ip]
            self.create_alert(
                f"Connection to Known Malicious IP",
                f"Host {src_ip} connected to known malicious IP {dst_ip} ({threat_info['threat_type']})",
                "Critical",
                src_ip,
                {
                    "destination": dst_ip,
                    "threat_type": threat_info["threat_type"],
                    "threat_source": threat_info["source"]
                }
            )
        
        # Check for incoming connections from malicious IPs
        if src_ip in self.malicious_ip_database:
            threat_info = self.malicious_ip_database[src_ip]
            self.create_alert(
                f"Connection from Known Malicious IP",
                f"Malicious IP {src_ip} ({threat_info['threat_type']}) connected to {dst_ip}",
                "Critical",
                src_ip,
                {
                    "destination": dst_ip,
                    "threat_type": threat_info["threat_type"],
                    "threat_source": threat_info["source"]
                }
            )

    def check_arp_spoofing(self, log):
        """Check for signs of ARP spoofing attacks"""
        if log["protocol"] != "ARP" or "details" not in log:
            return
        
        if "sender_mac" not in log["details"] or "sender_ip" not in log["details"]:
            return
        
        mac = log["details"]["sender_mac"]
        ip = log["details"]["sender_ip"]
        
        # Initialize ARP table if not exists
        if "arp_table" not in self.__dict__:
            self.arp_table = {}
        
        # Check if we've seen this IP before with a different MAC
        if ip in self.arp_table and self.arp_table[ip] != mac:
            self.create_alert(
                "Possible ARP Spoofing",
                f"IP address {ip} changed MAC from {self.arp_table[ip]} to {mac}",
                "High",
                ip,
                {"old_mac": self.arp_table[ip], "new_mac": mac}
            )
        
        # Update ARP table
        self.arp_table[ip] = mac

    def detect_c2_communication(self, log):
        """Detect potential Command & Control communication patterns"""
        src_ip = log["src_ip"]
        dst_ip = log["dst_ip"]
        dst_port = log["dst_port"]
        protocol = log["protocol"]
        timestamp = datetime.fromisoformat(log["timestamp"])
        
        # Initialize tracker for this source IP
        if src_ip not in self.c2_pattern_tracker:
            self.c2_pattern_tracker[src_ip] = {
                "connections": [],
                "last_checked": timestamp
            }
        
        # Add this connection
        self.c2_pattern_tracker[src_ip]["connections"].append({
            "dst_ip": dst_ip,
            "dst_port": dst_port,
            "protocol": protocol,
            "timestamp": timestamp
        })
        
        # Keep only last 24 hours of connections
        one_day_ago = timestamp - timedelta(days=1)
        self.c2_pattern_tracker[src_ip]["connections"] = [
            conn for conn in self.c2_pattern_tracker[src_ip]["connections"]
            if conn["timestamp"] > one_day_ago
        ]
        
        # Only analyze if we have enough data and haven't checked recently
        if (len(self.c2_pattern_tracker[src_ip]["connections"]) >= 5 and
                (timestamp - self.c2_pattern_tracker[src_ip]["last_checked"]).total_seconds() > 3600):
            
            self.c2_pattern_tracker[src_ip]["last_checked"] = timestamp
            
            # Analyze timing patterns
            intervals = []
            connections = sorted(self.c2_pattern_tracker[src_ip]["connections"], 
                                key=lambda x: x["timestamp"])
            
            for i in range(1, len(connections)):
                interval = (connections[i]["timestamp"] - 
                            connections[i-1]["timestamp"]).total_seconds()
                intervals.append(interval)
            
            # Check for regular beaconing (common in C2)
            if len(intervals) >= 4:
                # Calculate standard deviation of intervals
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
                std_dev = variance ** 0.5
                
                # Regular beaconing has low standard deviation relative to average
                if std_dev < avg_interval * 0.2 and avg_interval > 60:  # At least 1 minute average
                    self.create_alert(
                        "Possible C2 Beaconing",
                        f"Host {src_ip} shows regular connection patterns (beaconing) to {dst_ip}",
                        "High",
                        src_ip,
                        {
                            "destination": dst_ip,
                            "avg_interval_seconds": avg_interval,
                            "std_dev": std_dev,
                            "connection_count": len(connections)
                        }
                    )

    def check_time_anomaly(self, log):
        """Check for network activity at unusual times"""
        timestamp = datetime.fromisoformat(log["timestamp"])
        src_ip = log["src_ip"]
        hour = timestamp.hour
        
        # Define business hours (e.g., 8 AM to 6 PM)
        business_hours_start = 8
        business_hours_end = 18
        
        # Skip checks for external IPs
        if not self.is_internal_ip(src_ip):
            return
        
        # Check if this internal host has been active during business hours
        if src_ip not in self.active_hours:
            self.active_hours[src_ip] = set()
        
        self.active_hours[src_ip].add(hour)
        
        # If host is active outside business hours and has been seen during business hours
        business_hours = set(range(business_hours_start, business_hours_end + 1))
        if (hour < business_hours_start or hour > business_hours_end) and \
        self.active_hours[src_ip].intersection(business_hours) and \
        src_ip not in self.after_hours_alerted:
            
            self.create_alert(
                "After-Hours Activity",
                f"Host {src_ip} active at {timestamp.strftime('%H:%M')} outside normal business hours",
                "Medium",
                src_ip,
                {"hour": hour, "timestamp": timestamp.isoformat()}
            )
            
            # Remember we've alerted for this host (to avoid too many alerts)
            self.after_hours_alerted.add(src_ip)
            
            # Reset after 24 hours (allows for alert the next day if needed)
            threading.Timer(86400, lambda ip=src_ip: self.after_hours_alerted.discard(ip)).start()

    def is_internal_ip(self, ip):
        """Check if IP is internal"""
        return (ip.startswith('10.') or 
                ip.startswith('192.168.') or 
                ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31)

    def monitor_login_attempts(self, log):
        """Monitor for suspicious credential login attempts"""
        src_ip = log["src_ip"]
        dst_ip = log["dst_ip"]
        dst_port = log["dst_port"]
        timestamp = datetime.fromisoformat(log["timestamp"])
        
        # Map ports to services
        port_service_map = {
            22: "SSH",
            23: "Telnet",
            3389: "RDP",
            445: "SMB",
            139: "NetBIOS",
            21: "FTP",
            25: "SMTP"
        }
        
        service = port_service_map.get(dst_port, f"Port {dst_port}")
        
        # Track login attempts
        key = f"{src_ip}_{dst_ip}_{dst_port}"
        if key not in self.login_attempt_tracker:
            self.login_attempt_tracker[key] = {
                "count": 0,
                "first_attempt": timestamp,
                "last_attempt": timestamp
            }
        else:
            self.login_attempt_tracker[key]["count"] += 1
            self.login_attempt_tracker[key]["last_attempt"] = timestamp
        
        # Check time elapsed
        time_elapsed = (timestamp - self.login_attempt_tracker[key]["first_attempt"]).total_seconds()
        
        # Alert on many login attempts in short time
        if self.login_attempt_tracker[key]["count"] >= 5 and time_elapsed < 60:
            self.create_alert(
                "Possible Brute Force Attempt",
                f"Host {src_ip} made {self.login_attempt_tracker[key]['count']} {service} connection attempts to {dst_ip} in {time_elapsed:.1f} seconds",
                "High",
                src_ip,
                {
                    "target": dst_ip,
                    "service": service,
                    "attempts": self.login_attempt_tracker[key]["count"],
                    "time_period": f"{time_elapsed:.1f} seconds"
                }
            )
            # Reset tracker after alert
            self.login_attempt_tracker[key]["count"] = 0
            self.login_attempt_tracker[key]["first_attempt"] = timestamp

    def play_alert_sound(self, severity):
        """Play a sound based on alert severity"""
        if not self.sound_enabled:
            return
            
        try:
            # Map severity to sound parameters
            severity_level = severity.lower() if isinstance(severity, str) else 'medium'
            if severity_level not in self.sound_frequencies:
                severity_level = 'medium'  # Default to medium if severity not recognized
                
            frequency = self.sound_frequencies[severity_level]
            duration = self.sound_durations[severity_level]
            
            # Play sound in a separate thread to avoid blocking
            sound_thread = threading.Thread(
                target=self._play_sound,
                args=(frequency, duration),
                daemon=True
            )
            sound_thread.start()
                
        except Exception as e:
            print(f"Error playing alert sound: {e}")
    
    def _play_sound(self, frequency, duration):
        """Actual sound playing function - platform dependent"""
        try:
            if os.name == 'nt':  # Windows
                winsound.Beep(frequency, duration)
            else:  # Linux/Mac
                # For Linux/Mac, you might need to use different libraries
                # This is a simple fallback using the system bell
                print('\a')  # Terminal bell
                
                # Alternative implementations using other libraries:
                # If using pygame (pip install pygame):
                # import pygame
                # pygame.mixer.init()
                # pygame.mixer.Sound('path/to/alert.wav').play()
                
                # If using pydub (pip install pydub):
                # from pydub import AudioSegment
                # from pydub.playback import play
                # sound = AudioSegment.silent(duration=duration).overlay(
                #     AudioSegment.sine(frequency, duration=duration)
                # )
                # play(sound)
        except Exception as e:
            print(f"Failed to play sound: {e}")

    def create_alert(self, alert_type, description, severity, source_ip, details):
        """Create and store an alert"""
        timestamp = datetime.now().isoformat()
        
        # Store in database
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO alerts (timestamp, alert_type, description, severity, source_ip, details) VALUES (?, ?, ?, ?, ?, ?)",
                (timestamp, alert_type, description, severity, source_ip, json.dumps(details))
            )
            self.conn.commit()
            
            # Invalidate alert cache
            self.data_cache['alerts']['data'] = None
        
        # Create alert object for frontend
        alert = {
            "timestamp": timestamp,
            "alert_type": alert_type,
            "description": description,
            "severity": severity,
            "source_ip": source_ip,
            "details": details
        }
        
        # Play sound based on severity
        self.play_alert_sound(severity)
        
        # Signal the frontend
        self.updateAlerts.emit(json.dumps(alert))

    # def create_test_alert(self):
    #     """
    #     Create a fake alert for testing purposes.
    #     This method generates random alert data and stores it in the database.
    #     Returns the created alert as a JSON string.
    #     """
    #     import random
    #     import json
    #     from datetime import datetime
        
    #     # Generate random alert data
    #     alert_types = ["intrusion_attempt", "port_scan", "malware_detection", "unusual_traffic", "authentication_failure"]
    #     severities = ["low", "medium", "high", "critical"]
        
    #     alert_type = random.choice(alert_types)
    #     severity = random.choice(severities)
        
    #     # Generate a random IP address
    #     source_ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        
    #     # Create description based on alert type
    #     descriptions = {
    #         "intrusion_attempt": f"Possible intrusion attempt from {source_ip}",
    #         "port_scan": f"Port scan detected from {source_ip}",
    #         "malware_detection": f"Potential malware activity from {source_ip}",
    #         "unusual_traffic": f"Unusual network traffic pattern from {source_ip}",
    #         "authentication_failure": f"Multiple authentication failures from {source_ip}"
    #     }
        
    #     description = descriptions[alert_type]
        
    #     # Generate random details based on alert type
    #     details = {
    #         "timestamp": datetime.now().isoformat(),
    #         "test_generated": True
    #     }
        
    #     if alert_type == "intrusion_attempt":
    #         details.update({
    #             "target_port": random.randint(1, 65535),
    #             "attempt_count": random.randint(1, 10),
    #             "protocol": random.choice(["TCP", "UDP"])
    #         })
    #     elif alert_type == "port_scan":
    #         details.update({
    #             "ports_scanned": [random.randint(1, 65535) for _ in range(random.randint(3, 10))],
    #             "scan_duration_ms": random.randint(100, 5000)
    #         })
    #     elif alert_type == "malware_detection":
    #         details.update({
    #             "signature": f"MALWARE-{random.randint(1000, 9999)}",
    #             "file_path": f"/tmp/suspicious-file-{random.randint(1000, 9999)}.bin"
    #         })
    #     elif alert_type == "unusual_traffic":
    #         details.update({
    #             "normal_traffic_bytes": random.randint(1000, 10000),
    #             "current_traffic_bytes": random.randint(10000, 100000),
    #             "threshold_exceeded": "Yes"
    #         })
    #     elif alert_type == "authentication_failure":
    #         details.update({
    #             "username": random.choice(["admin", "user", "guest", "root", "system"]),
    #             "attempt_count": random.randint(3, 10),
    #             "time_window_minutes": random.randint(1, 5)
    #         })
        
    #     # Create the alert using the existing method
    #     self.create_alert(alert_type, description, severity, source_ip, details)
        
    #     # Return the created alert data as a JSON string
    #     alert = {
    #         "timestamp": datetime.now().isoformat(),
    #         "alert_type": alert_type,
    #         "description": description,
    #         "severity": severity,
    #         "source_ip": source_ip,
    #         "details": details
    #     }
        
    #     return json.dumps(alert)

    # # Add the Slot decorator to make this method accessible from the frontend
    # @Slot(result=str)
    # def test_alert(self):
    #     """
    #     Create a test alert and return the result.
    #     This is a slot that can be called from the frontend via QWebChannel.
    #     """
    #     try:
    #         return self.create_test_alert()
    #     except Exception as e:
    #         print(f"Error creating test alert: {e}")
    #         return json.dumps({"error": str(e)})
        
    @Slot(bool)
    def toggle_alert_sound(self, enabled):
        """Enable or disable alert sounds"""
        self.sound_enabled = enabled
        return self.sound_enabled
    
    @Slot(result=bool)
    def get_sound_status(self):
        """Return whether alert sounds are enabled"""
        return self.sound_enabled
    
    def is_cache_valid(self, cache_key):
        """Check if cache entry is valid"""
        cache_entry = self.data_cache.get(cache_key)
        if not cache_entry or not cache_entry['timestamp']:
            return False
        age = (datetime.now() - cache_entry['timestamp']).total_seconds()
        return age <= self.cache_ttl
    
    @Slot(result=str)
    def get_network_data(self):
        """Get network data for visualization with sampling for large datasets"""
        # Check cache first
        if self.is_cache_valid('network_data'):
            return json.dumps(self.data_cache['network_data']['data'])
            
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                
                # Get data from the last hour
                one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
                
                # Get aggregated data directly from the database with sampling for large datasets
                cursor.execute("""
                    SELECT 
                        substr(timestamp, 1, 16) as minute_bucket,
                        COUNT(*) as packet_count
                    FROM network_logs
                    WHERE timestamp > ?
                    GROUP BY minute_bucket
                    ORDER BY minute_bucket
                """, (one_hour_ago,))
                
                time_series_data = cursor.fetchall()
                
                # Convert to list of dicts
                result = [{"timestamp": ts, "count": count} for ts, count in time_series_data]
                
                # Smart sampling for large datasets - don't send more than 60 points
                if len(result) > 60:
                    # Calculate sampling rate
                    sample_rate = max(1, len(result) // 60)
                    result = result[::sample_rate]
                
                # Update cache
                self.data_cache['network_data'] = {
                    'data': result,
                    'timestamp': datetime.now()
                }
                
                return json.dumps(result)
        
        except Exception as e:
            print(f"Error getting network data: {e}")
            return json.dumps([])
    
    @Slot(result=str)
    def get_alert_data(self):
        """Get alert data for visualization"""
        # Check cache first
        if self.is_cache_valid('alerts'):
            return json.dumps(self.data_cache['alerts']['data'])
            
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT timestamp, alert_type, description, severity, source_ip, details 
                    FROM alerts 
                    ORDER BY timestamp DESC 
                    LIMIT 100
                """)
                alerts = cursor.fetchall()
            
            alert_list = []
            for alert in alerts:
                raw_details = alert[5]
                try:
                    details = json.loads(raw_details) if raw_details else {}
                except json.JSONDecodeError:
                    details = {"raw": raw_details}

                alert_obj = {
                    "timestamp": alert[0],
                    "alert_type": alert[1],
                    "description": alert[2],
                    "severity": alert[3],
                    "source_ip": alert[4],
                    "details": details
                }
                alert_list.append(alert_obj)
            
            # Update cache
            self.data_cache['alerts'] = {
                'data': alert_list,
                'timestamp': datetime.now()
            }
                
            return json.dumps(alert_list)

        except Exception as e:
            print(f"Error getting alert data: {e}")
            return json.dumps([])
        
    @Slot(result=str)
    def get_traffic_summary(self):
        """Get traffic summary for visualization with optimizations for large datasets"""
        # Check cache first
        if self.is_cache_valid('traffic_summary'):
            return json.dumps(self.data_cache['traffic_summary']['data'])
            
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                
                # Get protocol distribution - limit the query to recent data
                cursor.execute("""
                    SELECT protocol, COUNT(*) as count
                    FROM network_logs
                    WHERE timestamp > datetime('now', '-1 hour')
                    GROUP BY protocol
                """)
                protocol_data = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Get top source IPs - limit to 10 most active
                cursor.execute("""
                    SELECT src_ip, COUNT(*) as count
                    FROM network_logs
                    WHERE timestamp > datetime('now', '-1 hour')
                    GROUP BY src_ip
                    ORDER BY count DESC
                    LIMIT 10
                """)
                src_ip_data = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Get top destination ports (services) - limit to 10 most active
                cursor.execute("""
                    SELECT dst_port, COUNT(*) as count
                    FROM network_logs
                    WHERE timestamp > datetime('now', '-1 hour')
                    AND dst_port IS NOT NULL
                    GROUP BY dst_port
                    ORDER BY count DESC
                    LIMIT 10
                """)
                dst_port_data = {str(row[0]): row[1] for row in cursor.fetchall()}
                
                # Create summary object
                summary = {
                    "protocol_distribution": protocol_data,
                    "top_sources": src_ip_data,
                    "top_services": dst_port_data
                }
                
                # Update cache
                self.data_cache['traffic_summary'] = {
                    'data': summary,
                    'timestamp': datetime.now()
                }
                
                return json.dumps(summary)
        
        except Exception as e:
            print(f"Error getting traffic summary: {e}")
            return json.dumps({})
    
    @Slot(result=int)
    def get_log_count(self):
        """Get total count of log entries"""
        # Check cache first for very frequent queries
        if self.is_cache_valid('log_count'):
            return self.data_cache['log_count']['data']
            
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM network_logs")
                count = cursor.fetchone()[0]
            
            # Update cache
            self.data_cache['log_count'] = {
                'data': count,
                'timestamp': datetime.now()
            }
            
            # Emit signal for log count change to notify frontend
            # This triggers the JS to update charts when log count changes
            self.updateNetworkLog.emit(json.dumps({"count": count}))
            
            return count
        
        except Exception as e:
            print(f"Error getting log count: {e}")
            return 0

    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()