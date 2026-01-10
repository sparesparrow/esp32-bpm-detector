#!/usr/bin/env python3
"""
Network Scanner for ESP32 BPM Detector
Scans local network to find ESP32 device by testing API endpoints
"""

import asyncio
import socket
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

try:
    import aiohttp
except ImportError:
    aiohttp = None


@dataclass
class ScanResult:
    esp32_ip: Optional[str] = None
    endpoints_status: Dict[str, bool] = None
    scan_duration: float = 0.0
    devices_scanned: int = 0

    def __post_init__(self):
        if self.endpoints_status is None:
            self.endpoints_status = {}

    def is_success(self) -> bool:
        return self.esp32_ip is not None and all(self.endpoints_status.values())


class NetworkScanner:
    """Scan local network for ESP32 BPM detector"""

    API_ENDPOINTS = [
        "/api/v1/system/health",
        "/api/v1/bpm/current",
        "/api/v1/system/config",
    ]

    def __init__(self, timeout: float = 0.5):
        self.timeout = timeout

    def get_local_subnet(self) -> Optional[str]:
        """Get local subnet from network interfaces"""
        try:
            # Get default gateway IP using ip route
            result = subprocess.run(
                ["ip", "route", "get", "8.8.8.8"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Parse: "8.8.8.8 via 192.168.1.1 dev wlan0 src 192.168.1.100"
                import re
                match = re.search(r'src\s+(\d+\.\d+\.\d+)\.\d+', result.stdout)
                if match:
                    return match.group(1)
        except Exception:
            pass

        # Fallback: common subnets
        return "192.168.1"

    async def scan_for_esp32(self, subnet: str = None) -> ScanResult:
        """Scan subnet for ESP32 API endpoints"""
        result = ScanResult()
        start_time = asyncio.get_event_loop().time()

        if subnet is None:
            subnet = self.get_local_subnet()

        if subnet is None:
            return result

        if aiohttp is None:
            # Fallback to sync scanning with urllib
            return self._scan_sync(subnet)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            # Scan IPs in parallel batches
            tasks = []
            for i in range(1, 255):
                ip = f"{subnet}.{i}"
                tasks.append(self._test_ip(session, ip))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for ip_result in results:
                if isinstance(ip_result, tuple) and ip_result[1]:
                    result.esp32_ip = ip_result[0]
                    break
                result.devices_scanned += 1

        if result.esp32_ip:
            result.endpoints_status = await self.verify_endpoints(result.esp32_ip)

        result.scan_duration = asyncio.get_event_loop().time() - start_time
        return result

    async def _test_ip(self, session, ip: str) -> tuple:
        """Test if an IP responds to ESP32 API health endpoint"""
        try:
            async with session.get(
                f"http://{ip}/api/v1/system/health"
            ) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        # Verify it's our ESP32 by checking response structure
                        if "status" in data or "uptime" in data or "heap" in data:
                            return (ip, True)
                    except:
                        pass
        except:
            pass
        return (ip, False)

    async def verify_endpoints(self, ip: str) -> Dict[str, bool]:
        """Verify all API endpoints are responding"""
        endpoints_status = {}

        if aiohttp is None:
            return self._verify_endpoints_sync(ip)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5)
        ) as session:
            for endpoint in self.API_ENDPOINTS:
                try:
                    async with session.get(f"http://{ip}{endpoint}") as resp:
                        endpoints_status[endpoint] = resp.status == 200
                except:
                    endpoints_status[endpoint] = False

        return endpoints_status

    def _scan_sync(self, subnet: str) -> ScanResult:
        """Synchronous fallback scanning using urllib"""
        import urllib.request
        import urllib.error

        result = ScanResult()

        for i in range(1, 255):
            ip = f"{subnet}.{i}"
            result.devices_scanned += 1

            try:
                url = f"http://{ip}/api/v1/system/health"
                req = urllib.request.Request(url, method='GET')
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        result.esp32_ip = ip
                        break
            except:
                continue

        if result.esp32_ip:
            result.endpoints_status = self._verify_endpoints_sync(result.esp32_ip)

        return result

    def _verify_endpoints_sync(self, ip: str) -> Dict[str, bool]:
        """Synchronous endpoint verification"""
        import urllib.request
        import urllib.error

        endpoints_status = {}

        for endpoint in self.API_ENDPOINTS:
            try:
                url = f"http://{ip}{endpoint}"
                req = urllib.request.Request(url, method='GET')
                with urllib.request.urlopen(req, timeout=5) as resp:
                    endpoints_status[endpoint] = resp.status == 200
            except:
                endpoints_status[endpoint] = False

        return endpoints_status

    def scan_known_ip(self, ip: str) -> ScanResult:
        """Test a known IP address directly"""
        result = ScanResult()
        result.esp32_ip = ip
        result.endpoints_status = self._verify_endpoints_sync(ip)

        if not any(result.endpoints_status.values()):
            result.esp32_ip = None

        return result


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="ESP32 Network Scanner")
    parser.add_argument("-s", "--subnet", help="Subnet to scan (e.g., 192.168.1)")
    parser.add_argument("-i", "--ip", help="Test specific IP address")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="Timeout per host")
    args = parser.parse_args()

    scanner = NetworkScanner(timeout=args.timeout)

    if args.ip:
        print(f"Testing specific IP: {args.ip}")
        result = scanner.scan_known_ip(args.ip)
    else:
        subnet = args.subnet or scanner.get_local_subnet()
        print(f"Scanning subnet: {subnet}.0/24...")
        result = await scanner.scan_for_esp32(subnet)

    print()
    print("=" * 60)
    print("Network Scan Results")
    print("=" * 60)
    print(f"ESP32 IP:        {result.esp32_ip or 'Not found'}")
    print(f"Devices Scanned: {result.devices_scanned}")
    print(f"Duration:        {result.scan_duration:.1f}s")
    print()

    if result.endpoints_status:
        print("Endpoint Status:")
        for endpoint, status in result.endpoints_status.items():
            status_str = "OK" if status else "FAILED"
            print(f"  {endpoint}: {status_str}")

    if result.is_success():
        print()
        print(f"SUCCESS: ESP32 found at {result.esp32_ip}")
        return 0
    else:
        print()
        print("FAILED: ESP32 not found or endpoints not responding")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
