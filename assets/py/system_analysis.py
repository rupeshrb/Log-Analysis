from PySide6.QtCore import QObject, Slot, Signal
import os
import sys
import platform
import subprocess
import logging
import time
import psutil
from datetime import datetime
import threading
import json

# Define a function to get the correct path for resources in both dev and PyInstaller environments
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_path, relative_path)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SystemLogCollector")

# Base directories
BASE_LOG_DIR = "collected_logs/upload_log"
WINDOWS_LOG_DIR = os.path.join(BASE_LOG_DIR, "windows")
LINUX_LOG_DIR = os.path.join(BASE_LOG_DIR, "linux")

class SystemLogCollector(QObject):
    progressSignal = Signal(int, str)  # percentage, message
    
    def __init__(self):
        super().__init__()
        self.collected_files = []
   
    
    @Slot(result=str)
    def fetch_system_logs(self):
        """Main method to fetch system logs based on the OS"""
        self.collected_files = []
        
        try:
            # Create necessary directories
            self.create_log_directories()
            self.progressSignal.emit(5, "Created log directories")
            
            # Detect operating system
            os_type = platform.system()
            logger.info(f"Detected operating system: {os_type}")
            
            if os_type == "Windows":
                success = self.fetch_windows_logs()
            elif os_type == "Linux":
                success = self.fetch_linux_logs()
            else:
                logger.warning(f"Unsupported operating system: {os_type}")
                return json.dumps({
                    "success": False,
                    "message": f"Unsupported operating system: {os_type}",
                    "files_collected": 0
                })
            
            # Return result
            if success:
                result = {
                    "success": True,
                    "message": f"Successfully collected {len(self.collected_files)} system log files",
                    "files_collected": len(self.collected_files),
                    "storage_path": os.path.abspath(WINDOWS_LOG_DIR if os_type == "Windows" else LINUX_LOG_DIR),
                    "files": self.collected_files
                }
                logger.info(f"Log collection completed: {len(self.collected_files)} files")
                return json.dumps(result)
            else:
                return json.dumps({
                    "success": False,
                    "message": "Failed to collect system logs",
                    "files_collected": 0
                })
                
        except Exception as e:
            logger.error(f"Error in log collection: {e}")
            return json.dumps({
                "success": False,
                "message": f"Error in log collection: {str(e)}",
                "files_collected": 0
            })
    
    def create_log_directories(self):
        """Create directories for storing logs based on OS"""
        os_type = platform.system()
        if os_type == "Windows":
            os.makedirs(WINDOWS_LOG_DIR, exist_ok=True)
            logger.info(f"Created Windows log directory: {WINDOWS_LOG_DIR}")
        elif os_type == "Linux":
            os.makedirs(LINUX_LOG_DIR, exist_ok=True)
            logger.info(f"Created Linux log directory: {LINUX_LOG_DIR}")
        else:
            logger.warning(f"Unsupported OS type: {os_type}")

    
    def generate_log_file_name(self, log_dir, base_name):
        """Generate a unique log file name with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(log_dir, f"{base_name}_{timestamp}.txt")
        return file_path
    
    def fetch_windows_logs(self):
        """Advanced Windows log collection"""
        try:
            # Windows event logs
            self.progressSignal.emit(10, "Starting Windows log collection")
            self.collect_windows_event_logs()
            self.progressSignal.emit(30, "Collected Windows event logs")
            
            # System information
            self.collect_windows_system_info()
            self.progressSignal.emit(50, "Collected Windows system information")
            
            # Network configuration
            self.collect_windows_network_info()
            self.progressSignal.emit(70, "Collected Windows network information")
            
            # Process information
            self.collect_windows_processes()
            self.progressSignal.emit(90, "Collected Windows process information")
            
            # Service information
            self.collect_windows_services()
            self.progressSignal.emit(95, "Collected Windows service information")
            
            logger.info("Windows log collection completed successfully")
            self.progressSignal.emit(100, "Windows log collection completed")
            return True
        
        except Exception as e:
            logger.error(f"Error in Windows log collection: {e}")
            return False
    
    def collect_windows_event_logs(self):
        """Collect Windows event logs in log-like format"""
        try:
            # Try to import win32evtlog
            try:
                import win32evtlog
                import win32con
                import win32evtlogutil
            except ImportError:
                logger.error("win32evtlog module not available")
                event_file = self.generate_log_file_name(WINDOWS_LOG_DIR, "event_log_error")
                with open(event_file, "w", encoding="utf-8") as f:
                    f.write("Error: win32evtlog module not available. Cannot collect Windows event logs.\n")
                    f.write("Please install pywin32 package to enable Windows event log collection.")
                self.collected_files.append(event_file)
                return

            # Windows event log types to collect
            log_types = [
                "System",
                "Application",
                "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall"
            ]

            for i, log_type in enumerate(log_types):
                try:
                    log_type_safe = log_type.replace("/", "_").replace("-", "_").replace(" ", "_")
                    log_file_path = self.generate_log_file_name(WINDOWS_LOG_DIR, f"event_{log_type_safe}")

                    with open(log_file_path, "w", encoding="utf-8") as log_file:
                        # Metadata header
                        log_file.write(f"# === Windows Event Log: {log_type} ===\n")
                        log_file.write(f"# Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        log_file.write("#" * 50 + "\n\n")

                        log_handle = win32evtlog.OpenEventLog(None, log_type)
                        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

                        # Read only the latest 100 events
                        count = 0
                        max_events = 100

                        events = win32evtlog.ReadEventLog(log_handle, flags, 0)
                        while events and count < max_events:
                            for event in events:
                                try:
                                    event_id = event.EventID & 0xFFFF
                                    event_time = event.TimeGenerated.Format()
                                    event_type = {
                                        win32con.EVENTLOG_ERROR_TYPE: "ERROR",
                                        win32con.EVENTLOG_WARNING_TYPE: "WARNING",
                                        win32con.EVENTLOG_INFORMATION_TYPE: "INFO",
                                        win32con.EVENTLOG_AUDIT_SUCCESS: "AUDIT_SUCCESS",
                                        win32con.EVENTLOG_AUDIT_FAILURE: "AUDIT_FAILURE"
                                    }.get(event.EventType, "UNKNOWN")

                                    # Build a clean log line
                                    log_entry = (f"[{event_time}] "
                                                f"[{event_type}] "
                                                f"[{event.SourceName}] "
                                                f"EventID={event_id}")

                                    if event.StringInserts:
                                        message = " ".join(data for data in event.StringInserts if data)
                                        log_entry += f" Message=\"{message}\""

                                    log_file.write(log_entry + "\n")
                                    count += 1

                                    if count >= max_events:
                                        break

                                except Exception as e:
                                    log_file.write(f"# Error processing event: {e}\n\n")

                            if count >= max_events:
                                break

                            try:
                                events = win32evtlog.ReadEventLog(log_handle, flags, 0)
                            except:
                                break

                        win32evtlog.CloseEventLog(log_handle)

                    self.collected_files.append(log_file_path)
                    self.progressSignal.emit(10 + 5 * i, f"Collected {log_type} event log")
                    logger.info(f"Collected Windows event log: {log_type}")

                except Exception as e:
                    logger.error(f"Error collecting Windows event log {log_type}: {e}")
                    error_file = self.generate_log_file_name(WINDOWS_LOG_DIR, f"error_eventlog_{log_type_safe}")
                    with open(error_file, "w", encoding="utf-8") as f:
                        f.write(f"Error collecting Windows event log {log_type}: {e}\n")
                    self.collected_files.append(error_file)

        except Exception as e:
            logger.error(f"Error in Windows event log collection: {e}")

    
    def collect_windows_system_info(self):
        """Collect Windows system information"""
        try:
            sysinfo_file = self.generate_log_file_name(WINDOWS_LOG_DIR, "system_info")
            
            with open(sysinfo_file, "w", encoding="utf-8") as f:
                f.write("=== Windows System Information ===\n")
                f.write(f"Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # System information
                f.write("--- System Information ---\n")
                result = subprocess.run(["systeminfo"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Disk information
                f.write("--- Disk Information ---\n")
                result = subprocess.run(["wmic", "logicaldisk", "get", "caption,description,providername,size,freespace"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Hardware information
                f.write("--- CPU Information ---\n")
                result = subprocess.run(["wmic", "cpu", "get", "name,manufacturer,maxclockspeed,numberofcores,numberoflogicalprocessors"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Memory information
                f.write("--- Memory Information ---\n")
                virtual_memory = psutil.virtual_memory()
                f.write(f"Total: {virtual_memory.total / (1024**3):.2f} GB\n")
                f.write(f"Available: {virtual_memory.available / (1024**3):.2f} GB\n")
                f.write(f"Used: {virtual_memory.used / (1024**3):.2f} GB\n")
                f.write(f"Percentage: {virtual_memory.percent}%\n\n")
                
                # Startup programs
                f.write("--- Startup Programs ---\n")
                result = subprocess.run(["wmic", "startup", "get", "caption,command,location,user"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Installed software
                f.write("--- Installed Software (Sample) ---\n")
                result = subprocess.run(["wmic", "product", "get", "name,version,vendor", "/format:list"], capture_output=True, text=True)
                # Limit output size by taking the first 50 lines
                software_lines = result.stdout.split('\n')[:50]
                f.write('\n'.join(software_lines) + "\n...(truncated)...\n\n")
                
                # Windows firewall status
                f.write("--- Firewall Status ---\n")
                result = subprocess.run(["netsh", "advfirewall", "show", "allprofiles"], capture_output=True, text=True)
                f.write(result.stdout + "\n")
            
            self.collected_files.append(sysinfo_file)
            logger.info("Collected Windows system information")
        except Exception as e:
            logger.error(f"Error collecting Windows system info: {e}")
    
    def collect_windows_network_info(self):
        """Collect Windows network configuration"""
        try:
            network_file = self.generate_log_file_name(WINDOWS_LOG_DIR, "network_config")
            with open(network_file, "w", encoding="utf-8") as f:
                # Run ipconfig /all
                f.write("=== Network Configuration ===\n\n")
                result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True)
                f.write(result.stdout)
                
                # Run netstat
                f.write("\n\n=== Network Connections ===\n\n")
                result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
                f.write(result.stdout)
                
                # Run route print
                f.write("\n\n=== Routing Table ===\n\n")
                result = subprocess.run(["route", "print"], capture_output=True, text=True)
                f.write(result.stdout)
                
                # DNS information
                f.write("\n\n=== DNS Cache ===\n\n")
                result = subprocess.run(["ipconfig", "/displaydns"], capture_output=True, text=True)
                f.write(result.stdout)
                
                # Network adapters detailed info
                f.write("\n\n=== Network Adapters Details ===\n\n")
                result = subprocess.run(["wmic", "nic", "get", "name,index,manufacturer,macaddress,netconnectionid"], capture_output=True, text=True)
                f.write(result.stdout)
                
                # Active network connections
                f.write("\n\n=== Active Network Connections ===\n\n")
                try:
                    connections = psutil.net_connections(kind='all')
                    f.write(f"{'Local Address':<25} {'Remote Address':<25} {'Status':<15} {'PID':<10} {'Process Name':<20}\n")
                    f.write("-" * 100 + "\n")
                    
                    for conn in connections:
                        try:
                            if conn.laddr:
                                local_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
                            else:
                                local_addr = "-"
                                
                            if conn.raddr:
                                remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}"
                            else:
                                remote_addr = "-"
                                
                            status = conn.status if hasattr(conn, 'status') else "-"
                            pid = conn.pid if conn.pid else "-"
                            
                            try:
                                process_name = psutil.Process(pid).name() if pid != "-" else "-"
                            except:
                                process_name = "Unknown"
                                
                            f.write(f"{local_addr:<25} {remote_addr:<25} {status:<15} {pid:<10} {process_name:<20}\n")
                        except:
                            pass
                except Exception as net_err:
                    f.write(f"Error retrieving network connections: {net_err}\n")
            
            self.collected_files.append(network_file)
            logger.info("Collected Windows network information")
        except Exception as e:
            logger.error(f"Error collecting Windows network info: {e}")
    
    def collect_windows_processes(self):
        """Collect information about running processes"""
        try:
            processes_file = self.generate_log_file_name(WINDOWS_LOG_DIR, "processes")
            with open(processes_file, "w", encoding="utf-8") as f:
                f.write("=== Running Processes ===\n")
                f.write(f"Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"{'PID':<10} {'CPU %':<10} {'Memory %':<10} {'Name':<30} {'Username':<20} {'Created':<25} {'Connections'}\n")
                f.write("-" * 100 + "\n")
                
                for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']):
                    try:
                        process_info = proc.info
                        created_time = datetime.fromtimestamp(process_info['create_time']).strftime('%Y-%m-%d %H:%M:%S') if process_info.get('create_time') else 'N/A'
                        username = process_info.get('username') or 'N/A'
                        
                        # Fetch connections safely
                        try:
                            connections = len(proc.connections(kind='inet'))
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            connections = "N/A"
                        
                        f.write(f"{process_info['pid']:<10} "
                                f"{process_info['cpu_percent']:<10.1f} "
                                f"{process_info['memory_percent']:<10.1f} "
                                f"{(process_info['name'] or '')[:30]:<30} "
                                f"{username[:20]:<20} "
                                f"{created_time:<25} "
                                f"{connections}\n")
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
            
            self.collected_files.append(processes_file)
            logger.info("Collected Windows process information")
        except Exception as e:
            logger.error(f"Error collecting Windows process info: {e}")

    
    def collect_windows_services(self):
        """Collect Windows services information"""
        try:
            services_file = self.generate_log_file_name(WINDOWS_LOG_DIR, "services")
            with open(services_file, "w", encoding="utf-8") as f:
                f.write("=== Windows Services ===\n")
                f.write(f"Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Get services from wmic
                result = subprocess.run(["wmic", "service", "get", "name,startmode,state,status,startname,pathname"], capture_output=True, text=True)
                f.write(result.stdout)
            
            self.collected_files.append(services_file)
            logger.info("Collected Windows services information")
        except Exception as e:
            logger.error(f"Error collecting Windows services info: {e}")
    
    def fetch_linux_logs(self):
        """Advanced Linux log collection"""
        try:
            self.progressSignal.emit(10, "Starting Linux log collection")
            
            # Common system logs
            log_files = [
                "/var/log/syslog",
                "/var/log/auth.log",
                "/var/log/kern.log",
                "/var/log/messages",
                "/var/log/secure",
                "/var/log/ufw.log",
                "/var/log/firewalld",
                "/var/log/audit/audit.log",
                "/var/log/boot.log",
                "/var/log/cron"
            ]
            
            # Process each log file
            for i, log_file in enumerate(log_files):
                progress = 10 + int((i / len(log_files)) * 40)  # Progress from 10% to 50%
                self.progressSignal.emit(progress, f"Processing log file: {os.path.basename(log_file)}")
                
                if os.path.exists(log_file):
                    try:
                        dest_file = self.generate_log_file_name(LINUX_LOG_DIR, os.path.basename(log_file))
                        logger.info(f"Copying Linux log file: {log_file}...")
                        
                        with open(log_file, "r", errors='ignore') as src, open(dest_file, "w", encoding="utf-8") as dest:
                            # Add metadata header
                            dest.write(f"=== {os.path.basename(log_file)} ===\n")
                            dest.write(f"Source: {log_file}\n")
                            dest.write(f"Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            dest.write("=" * 50 + "\n\n")
                            
                            # Filter to keep logs from the last 24 hours and with important keywords
                            current_time = time.time()
                            day_seconds = 86400  # 24 hours in seconds
                            
                            for line in src:
                                # Always keep lines with errors or security-related keywords
                                if ("error" in line.lower() or "fail" in line.lower() or 
                                    "unauthorized" in line.lower() or "denied" in line.lower() or
                                    "warning" in line.lower() or "alert" in line.lower() or
                                    "critical" in line.lower()):
                                    dest.write(line)
                        
                        self.collected_files.append(dest_file)
                        logger.info(f"Copied {log_file} to {dest_file}")
                    except Exception as e:
                        logger.error(f"Error copying Linux log file {log_file}: {e}")
            
            # Collect system information
            self.progressSignal.emit(50, "Collecting Linux system information")
            self.collect_linux_system_info()
            self.progressSignal.emit(70, "Collected Linux system information")
            
            # Collect network information
            self.progressSignal.emit(70, "Collecting Linux network information")
            self.collect_linux_network_info()
            self.progressSignal.emit(85, "Collected Linux network information")
            
            # Collect process information
            self.progressSignal.emit(85, "Collecting Linux process information")
            self.collect_linux_process_info()
            self.progressSignal.emit(95, "Collected Linux process information")
            
            self.progressSignal.emit(100, "Linux log collection complete")
            return True
        
        except Exception as e:
            logger.error(f"Error in Linux log collection: {e}")
            return False
    
    def collect_linux_system_info(self):
        """Collect Linux system information"""
        try:
            sysinfo_file = self.generate_log_file_name(LINUX_LOG_DIR, "system_info")
            
            with open(sysinfo_file, "w", encoding="utf-8") as f:
                f.write("=== System Information ===\n")
                f.write(f"Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Kernel information
                f.write("--- Kernel Information ---\n")
                result = subprocess.run(["uname", "-a"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # OS release information
                f.write("--- OS Release Information ---\n")
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release", "r") as os_release:
                        f.write(os_release.read() + "\n\n")
                
                # CPU information
                f.write("--- CPU Information ---\n")
                if os.path.exists("/proc/cpuinfo"):
                    with open("/proc/cpuinfo", "r") as cpuinfo:
                        f.write(cpuinfo.read() + "\n\n")
                
                # Memory information
                f.write("--- Memory Information ---\n")
                result = subprocess.run(["free", "-h"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Disk usage
                f.write("--- Disk Usage ---\n")
                result = subprocess.run(["df", "-h"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # System uptime
                f.write("--- System Uptime ---\n")
                result = subprocess.run(["uptime"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Installed packages (limited sample)
                f.write("--- Installed Packages (Sample) ---\n")
                try:
                    # Try with apt (Debian/Ubuntu)
                    result = subprocess.run(["apt", "list", "--installed"], capture_output=True, text=True, timeout=5)
                    # Limit output size
                    pkg_lines = result.stdout.split('\n')[:50]
                    f.write('\n'.join(pkg_lines) + "\n...(truncated)...\n\n")
                except:
                    try:
                        # Try with rpm (Red Hat/CentOS)
                        result = subprocess.run(["rpm", "-qa"], capture_output=True, text=True, timeout=5)
                        pkg_lines = result.stdout.split('\n')[:50]
                        f.write('\n'.join(pkg_lines) + "\n...(truncated)...\n\n")
                    except:
                        f.write("Could not retrieve package list\n\n")
            
            self.collected_files.append(sysinfo_file)
            logger.info("Collected Linux system information")
        except Exception as e:
            logger.error(f"Error collecting Linux system info: {e}")
    
    def collect_linux_network_info(self):
        """Collect Linux network information"""
        try:
            network_file = self.generate_log_file_name(LINUX_LOG_DIR, "network_info")
            
            with open(network_file, "w", encoding="utf-8") as f:
                f.write("=== Network Information ===\n")
                f.write(f"Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Interface information
                f.write("--- Network Interfaces ---\n")
                result = subprocess.run(["ip", "addr"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Routing information
                f.write("--- Routing Table ---\n")
                result = subprocess.run(["ip", "route"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Listening ports
                f.write("--- Listening Ports ---\n")
                result = subprocess.run(["ss", "-tuln"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Active connections
                f.write("--- Active Connections ---\n")
                result = subprocess.run(["ss", "-tunp"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # DNS settings
                f.write("--- DNS Configuration ---\n")
                if os.path.exists("/etc/resolv.conf"):
                    with open("/etc/resolv.conf", "r") as resolv_conf:
                        f.write(resolv_conf.read() + "\n\n")
                
                # Network statistics
                f.write("--- Network Statistics ---\n")
                result = subprocess.run(["netstat", "-s"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # ARP table
                f.write("--- ARP Table ---\n")
                result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
                f.write(result.stdout + "\n")
            
            self.collected_files.append(network_file)
            logger.info("Collected Linux network information")
        except Exception as e:
            logger.error(f"Error collecting Linux network info: {e}")
    
    def collect_linux_process_info(self):
        """Collect Linux process information"""
        try:
            processes_file = self.generate_log_file_name(LINUX_LOG_DIR, "processes")
            
            with open(processes_file, "w", encoding="utf-8") as f:
                f.write("=== Running Processes ===\n")
                f.write(f"Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # General process list
                f.write("--- Process List ---\n")
                result = subprocess.run(["ps", "aux", "--sort=-pcpu"], capture_output=True, text=True)
                f.write(result.stdout + "\n\n")
                
                # Detailed process information
                f.write("--- Detailed Process Information ---\n")
                f.write(f"{'PID':<10} {'CPU %':<10} {'MEM %':<10} {'Name':<30} {'User':<15} {'Start Time':<20} {'Connections'}\n")
                f.write("-" * 100 + "\n")
                
                for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time', 'connections']):
                    try:
                        process_info = proc.info
                        created_time = datetime.fromtimestamp(process_info['create_time']).strftime('%Y-%m-%d %H:%M:%S') if process_info['create_time'] else 'N/A'
                        username = process_info['username'] if process_info['username'] else 'N/A'
                        connections = len(process_info['connections']) if process_info['connections'] else 0
                        
                        f.write(f"{process_info['pid']:<10} "
                                f"{process_info['cpu_percent']:<10.1f} "
                                f"{process_info['memory_percent']:<10.1f} "
                                f"{process_info['name'][:30]:<30} "
                                f"{username[:15]:<15} "
                                f"{created_time:<20} "
                                f"{connections}\n")
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Service status
                f.write("\n\n--- Service Status ---\n")
               
                try:
                    # Try systemd first
                    result = subprocess.run(["systemctl", "list-units", "--type=service", "--state=running"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        f.write("Active systemd services:\n")
                        f.write(result.stdout + "\n\n")
                    else:
                        # If systemd fails, try older service command
                        result = subprocess.run(["service", "--status-all"], capture_output=True, text=True, timeout=5)
                        f.write("Service status:\n")
                        f.write(result.stdout + "\n\n")
                except Exception as service_err:
                    f.write(f"Could not retrieve service status: {service_err}\n\n")
                
                # Process resource usage summary
                f.write("\n\n--- Process Resource Usage Summary ---\n")
                f.write("Top 10 CPU consumers:\n")
                try:
                    result = subprocess.run(["ps", "-eo", "pid,ppid,cmd,%mem,%cpu", "--sort=-%cpu", "|", "head", "-11"], 
                                            shell=True, capture_output=True, text=True, timeout=5)
                    f.write(result.stdout + "\n\n")
                except Exception as top_err:
                    f.write(f"Could not retrieve top CPU processes: {top_err}\n\n")
                
                f.write("Top 10 memory consumers:\n")
                try:
                    result = subprocess.run(["ps", "-eo", "pid,ppid,cmd,%mem,%cpu", "--sort=-%mem", "|", "head", "-11"], 
                                            shell=True, capture_output=True, text=True, timeout=5)
                    f.write(result.stdout + "\n")
                except Exception as top_err:
                    f.write(f"Could not retrieve top memory processes: {top_err}\n")
            
            self.collected_files.append(processes_file)
            logger.info("Collected Linux process information")
        except Exception as e:
            logger.error(f"Error collecting Linux process info: {e}")
    
    def collect_linux_security_info(self):
        """Collect Linux security information"""
        try:
            security_file = self.generate_log_file_name(LINUX_LOG_DIR, "security_info")
            
            with open(security_file, "w", encoding="utf-8") as f:
                f.write("=== Linux Security Information ===\n")
                f.write(f"Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Check for failed login attempts
                f.write("--- Failed Login Attempts ---\n")
                try:
                    result = subprocess.run(["lastb", "--fulltimes"], capture_output=True, text=True, timeout=5)
                    f.write(result.stdout + "\n\n")
                except Exception as login_err:
                    f.write(f"Could not retrieve failed login attempts: {login_err}\n\n")
                
                # Check for successful logins
                f.write("--- Successful Logins ---\n")
                try:
                    result = subprocess.run(["last", "-10"], capture_output=True, text=True, timeout=5)
                    f.write(result.stdout + "\n\n")
                except Exception as login_err:
                    f.write(f"Could not retrieve login history: {login_err}\n\n")
                
                # Check for sudo usage
                f.write("--- Sudo Usage ---\n")
                if os.path.exists("/var/log/auth.log"):
                    try:
                        result = subprocess.run(["grep", "sudo", "/var/log/auth.log"], capture_output=True, text=True, timeout=5)
                        f.write(result.stdout + "\n\n")
                    except Exception as sudo_err:
                        f.write(f"Could not retrieve sudo usage: {sudo_err}\n\n")
                
                # List users and groups
                f.write("--- Users and Groups ---\n")
                f.write("Local Users:\n")
                try:
                    with open("/etc/passwd", "r") as passwd_file:
                        f.write(passwd_file.read() + "\n\n")
                except Exception as user_err:
                    f.write(f"Could not read user list: {user_err}\n\n")
                
                f.write("Groups:\n")
                try:
                    with open("/etc/group", "r") as group_file:
                        f.write(group_file.read() + "\n\n")
                except Exception as group_err:
                    f.write(f"Could not read group list: {group_err}\n\n")
                
                # Check for scheduled jobs
                f.write("--- Scheduled Jobs ---\n")
                f.write("Crontab entries:\n")
                try:
                    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
                    f.write(result.stdout + "\n\n")
                except Exception as cron_err:
                    f.write(f"Could not retrieve crontab: {cron_err}\n\n")
                
                # System cron jobs
                f.write("System cron jobs:\n")
                cron_dirs = ["/etc/cron.d", "/etc/cron.daily", "/etc/cron.hourly", "/etc/cron.weekly", "/etc/cron.monthly"]
                for cron_dir in cron_dirs:
                    if os.path.exists(cron_dir):
                        f.write(f"\nContents of {cron_dir}:\n")
                        for file in os.listdir(cron_dir):
                            file_path = os.path.join(cron_dir, file)
                            if os.path.isfile(file_path):
                                f.write(f"- {file}\n")
            
            self.collected_files.append(security_file)
            logger.info("Collected Linux security information")
        except Exception as e:
            logger.error(f"Error collecting Linux security info: {e}")

# Create an instance of the class to be exposed to QWebChannel
class BackendClass_sys(QObject):
    progressSignal = Signal(int, str)  # percentage, message
    
    def __init__(self):
        super().__init__()
        self.log_collector = SystemLogCollector()
        # Pass the progress signal from the collector to this class
        self.log_collector.progressSignal.connect(self.forward_progress)
   
    
    @Slot(result=str)
    def fetch_logs(self):
        """Entry point for the UI to start log collection"""
        # Run log collection in a background thread to avoid freezing the UI
        threading.Thread(target=self._run_log_collection, daemon=True).start()
        return json.dumps({"status": "started", "message": "Log collection started in background"})
    
    def _run_log_collection(self):
        """Run log collection in background thread"""
        try:
            result = self.log_collector.fetch_system_logs()
            # The result is already a JSON string
            return result
        except Exception as e:
            logger.error(f"Error in log collection thread: {e}")
            return json.dumps({
                "success": False,
                "message": f"Error in log collection: {str(e)}",
                "files_collected": 0
            })
    
    def forward_progress(self, percentage, message):
        """Forward progress signals from the collector to the UI"""
        self.progressSignal.emit(percentage, message)