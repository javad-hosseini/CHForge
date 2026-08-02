"""
System Information Collector
Collects hardware and system information for benchmarking context

to run:

from project root folder:

cd /CHForge
python -m chforge.system.info

"""

import json
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any

import psutil

# Try to import logger, fallback to basic logging if not available
try:
    from ..utils.logger import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(handler)


@dataclass
class CPUInfo:
    """CPU Information"""
    model: str
    cores: int
    physical_cores: int
    threads: int
    frequency_mhz: Optional[float] = None
    architecture: str = ""
    cache_size: Optional[str] = None
    virtualization: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "cores": self.cores,
            "physical_cores": self.physical_cores,
            "threads": self.threads,
            "frequency_mhz": self.frequency_mhz,
            "architecture": self.architecture,
            "cache_size": self.cache_size,
            "virtualization": self.virtualization,
        }


@dataclass
class GPUInfo:
    """GPU Information"""
    name: str
    vendor: str
    memory_mb: Optional[int] = None
    driver_version: Optional[str] = None
    compute_capability: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "vendor": self.vendor,
            "memory_mb": self.memory_mb,
            "driver_version": self.driver_version,
            "compute_capability": self.compute_capability,
        }


@dataclass
class MemoryInfo:
    """Memory Information"""
    total_gb: float
    available_gb: float
    used_gb: float
    percentage: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_gb": round(self.total_gb, 2),
            "available_gb": round(self.available_gb, 2),
            "used_gb": round(self.used_gb, 2),
            "percentage": round(self.percentage, 2),
        }


@dataclass
class DiskInfo:
    """Disk Information"""
    device: str
    mount_point: str
    total_gb: float
    used_gb: float
    free_gb: float
    percentage: float
    filesystem: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device": self.device,
            "mount_point": self.mount_point,
            "total_gb": round(self.total_gb, 2),
            "used_gb": round(self.used_gb, 2),
            "free_gb": round(self.free_gb, 2),
            "percentage": round(self.percentage, 2),
            "filesystem": self.filesystem,
        }


@dataclass
class SystemInfo:
    """Complete System Information"""
    hostname: str
    os: str
    os_version: str
    kernel: str
    architecture: str
    python_version: str
    cpu: CPUInfo
    gpus: List[GPUInfo] = field(default_factory=list)
    memory: Optional[MemoryInfo] = None
    disks: List[DiskInfo] = field(default_factory=list)
    network_interfaces: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hostname": self.hostname,
            "os": self.os,
            "os_version": self.os_version,
            "kernel": self.kernel,
            "architecture": self.architecture,
            "python_version": self.python_version,
            "cpu": self.cpu.to_dict() if self.cpu else None,
            "gpus": [g.to_dict() for g in self.gpus],
            "memory": self.memory.to_dict() if self.memory else None,
            "disks": [d.to_dict() for d in self.disks],
            "network_interfaces": self.network_interfaces,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def print_summary(self) -> None:
        """Print a human-readable summary of system information"""
        print("\n" + "=" * 70)
        print("🖥️  SYSTEM INFORMATION")
        print("=" * 70)

        print(f"\n📌 Hostname: {self.hostname}")
        print(f"📌 OS: {self.os}")
        print(f"📌 Version: {self.os_version}")
        print(f"📌 Kernel: {self.kernel}")
        print(f"📌 Architecture: {self.architecture}")
        print(f"📌 Python: {self.python_version}")

        print("\n" + "-" * 70)
        print("💻 CPU:")
        print(f"   Model: {self.cpu.model}")
        print(f"   Physical Cores: {self.cpu.physical_cores}")
        print(f"   Logical Cores (Threads): {self.cpu.threads}")
        if self.cpu.frequency_mhz:
            print(f"   Frequency: {self.cpu.frequency_mhz:.0f} MHz")
        if self.cpu.cache_size:
            print(f"   Cache: {self.cpu.cache_size}")

        if self.gpus:
            print("\n" + "-" * 70)
            print("🎮 GPU(s):")
            for gpu in self.gpus:
                print(f"   - {gpu.name} ({gpu.vendor})")
                if gpu.memory_mb:
                    print(f"     Memory: {gpu.memory_mb} MB")
                if gpu.driver_version:
                    print(f"     Driver: {gpu.driver_version}")

        if self.memory:
            print("\n" + "-" * 70)
            print("🧠 Memory:")
            print(f"   Total: {self.memory.total_gb:.2f} GB")
            print(f"   Used: {self.memory.used_gb:.2f} GB ({self.memory.percentage:.1f}%)")
            print(f"   Available: {self.memory.available_gb:.2f} GB")

        if self.disks:
            print("\n" + "-" * 70)
            print("💾 Disk(s):")
            for disk in self.disks[:3]:
                print(f"   - {disk.device} ({disk.mount_point})")
                print(f"     Total: {disk.total_gb:.2f} GB | Used: {disk.used_gb:.2f} GB ({disk.percentage:.1f}%)")

        if self.network_interfaces:
            print("\n" + "-" * 70)
            print("🌐 Network:")
            for name, ip in list(self.network_interfaces.items())[:3]:
                print(f"   - {name}: {ip}")

        print("\n" + "=" * 70)


class SystemInfoCollector:
    """Collects system information from the host machine"""

    @staticmethod
    def collect() -> SystemInfo:
        """Collect all system information"""
        logger.info("Collecting system information...")

        hostname = platform.node()

        # تشخیص دقیق ویندوز
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                     r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                product_name, _ = winreg.QueryValueEx(key, "ProductName")
                winreg.CloseKey(key)
                os_name = product_name  # "Windows 11 Pro" یا "Windows 10 Pro"
            except:
                os_name = platform.system()
        else:
            os_name = platform.system()

        os_version = platform.release()
        kernel = platform.version()
        arch = platform.machine()
        python_ver = platform.python_version()

        cpu = SystemInfoCollector._get_cpu_info()
        gpus = SystemInfoCollector._get_gpu_info()
        memory = SystemInfoCollector._get_memory_info()
        disks = SystemInfoCollector._get_disk_info()
        network = SystemInfoCollector._get_network_info()

        return SystemInfo(
            hostname=hostname,
            os=os_name,
            os_version=os_version,
            kernel=kernel,
            architecture=arch,
            python_version=python_ver,
            cpu=cpu,
            gpus=gpus,
            memory=memory,
            disks=disks,
            network_interfaces=network,
        )

    @staticmethod
    def _get_cpu_model_fallback() -> str:
        """Get CPU model without psutil"""
        model = "Unknown"
        try:
            if platform.system() == "Windows":
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                         r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                    model, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                    winreg.CloseKey(key)
                except:
                    pass
            elif platform.system() == "Linux":
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            model = line.split(":")[1].strip()
                            break
            elif platform.system() == "Darwin":
                result = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                        capture_output=True, text=True)
                model = result.stdout.strip()
        except Exception as e:
            logger.debug(f"Could not get CPU model: {e}")
        return model

    @staticmethod
    def _get_cpu_info() -> CPUInfo:
        """Collect CPU information"""
        physical_cores = psutil.cpu_count(logical=False) or 0
        logical_cores = psutil.cpu_count(logical=True) or 0
        cpu_freq = psutil.cpu_freq()
        model = SystemInfoCollector._get_cpu_model_fallback()

        # Get cache size
        cache_size = None
        try:
            if platform.system() == "Linux":
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "cache size" in line:
                            cache_size = line.split(":")[1].strip()
                            break
            elif platform.system() == "Windows":
                # Windows cache info via wmic
                result = subprocess.run(
                    ["wmic", "cpu", "get", "L2CacheSize,L3CacheSize", "/format:csv"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) > 1:
                        parts = lines[1].split(",")
                        if len(parts) >= 3:
                            l2 = parts[1].strip()
                            l3 = parts[2].strip()
                            if l2 and l3:
                                cache_size = f"L2: {l2}KB, L3: {l3}KB"
        except:
            pass

        return CPUInfo(
            model=model,
            cores=physical_cores,
            physical_cores=physical_cores,
            threads=logical_cores,
            frequency_mhz=float(cpu_freq.max) if cpu_freq else None,
            architecture=platform.machine(),
            cache_size=cache_size,
        )

    @staticmethod
    def _get_gpu_info() -> List[GPUInfo]:
        """Collect GPU information"""
        gpus = []

        # NVIDIA GPU via nvidia-smi
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,vendor,memory.total,driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 4:
                            memory = None
                            if parts[2]:
                                memory_str = parts[2].replace(" MiB", "").replace(" MB", "").strip()
                                if memory_str.isdigit():
                                    memory = int(memory_str)
                            gpus.append(GPUInfo(
                                name=parts[0],
                                vendor=parts[1],
                                memory_mb=memory,
                                driver_version=parts[3] if len(parts) > 3 else None,
                            ))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("nvidia-smi not found or timed out")

        # Intel/AMD GPU via lspci (Linux)
        if platform.system() == "Linux" and not gpus:
            try:
                result = subprocess.run(
                    ["lspci", "-v"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                for line in result.stdout.split("\n"):
                    if "VGA" in line or "3D" in line:
                        gpu_name = line.strip()
                        vendor = "Unknown"
                        if "NVIDIA" in gpu_name:
                            vendor = "NVIDIA"
                        elif "AMD" in gpu_name or "ATI" in gpu_name:
                            vendor = "AMD"
                        elif "Intel" in gpu_name:
                            vendor = "Intel"
                        gpus.append(GPUInfo(name=gpu_name, vendor=vendor))
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        # Windows GPU via wmic
        if platform.system() == "Windows" and not gpus:
            try:
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name,adapterram", "/format:csv"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    for line in lines[1:]:
                        if line and "Microsoft" not in line and "Virtual" not in line:
                            parts = line.split(",")
                            if len(parts) >= 2:
                                ram = None
                                if parts[1] and parts[1].isdigit():
                                    ram = int(int(parts[1]) / (1024 * 1024))  # bytes to MB
                                gpus.append(GPUInfo(
                                    name=parts[0].strip(),
                                    vendor="Unknown",
                                    memory_mb=ram,
                                ))
            except:
                pass

        return gpus

    @staticmethod
    def _get_memory_info() -> Optional[MemoryInfo]:
        """Collect memory information"""
        try:
            mem = psutil.virtual_memory()
            return MemoryInfo(
                total_gb=mem.total / (1024 ** 3),
                available_gb=mem.available / (1024 ** 3),
                used_gb=mem.used / (1024 ** 3),
                percentage=mem.percent,
            )
        except Exception as e:
            logger.warning(f"Memory info unavailable: {e}")
            return None

    @staticmethod
    def _get_disk_info() -> List[DiskInfo]:
        """Collect disk information"""
        disks = []
        try:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append(DiskInfo(
                        device=partition.device,
                        mount_point=partition.mountpoint,
                        total_gb=usage.total / (1024 ** 3),
                        used_gb=usage.used / (1024 ** 3),
                        free_gb=usage.free / (1024 ** 3),
                        percentage=usage.percent,
                        filesystem=partition.fstype,
                    ))
                except PermissionError:
                    continue
        except Exception as e:
            logger.warning(f"Disk info unavailable: {e}")

        return disks

    @staticmethod
    def _get_network_info() -> Dict[str, str]:
        """Collect network interface information"""
        interfaces = {}
        try:
            for name, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == 2:  # AF_INET (IPv4)
                        if not addr.address.startswith("127."):
                            interfaces[name] = addr.address
                            break
        except Exception as e:
            logger.warning(f"Network info unavailable: {e}")

        return interfaces


def get_system_info() -> SystemInfo:
    """Get system information"""
    return SystemInfoCollector.collect()


def print_system_info() -> None:
    """Print system information summary"""
    info = get_system_info()
    info.print_summary()


if __name__ == "__main__":
    # For standalone execution
    if sys.path[0] == str(Path(__file__).parent):
        sys.path.insert(0, str(Path(__file__).parent.parent))

    print_system_info()
