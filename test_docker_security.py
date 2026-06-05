#!/usr/bin/env python3
"""
Docker deployment and security tests for Tenable.sc MCP Server.
Validates container health, security settings, and deployment configuration.
"""
import sys
import json
import subprocess
import re
from typing import Dict, List, Tuple


class DockerSecurityTest:
    """Docker deployment and security validation."""
    
    def __init__(self):
        """Initialize test suite."""
        self.results = {}
        self.issues = []
    
    def run_command(self, cmd: List[str]) -> Tuple[int, str, str]:
        """Run shell command and return result."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)
    
    def test_docker_installed(self) -> Dict:
        """Test if Docker is installed and accessible."""
        print("\n[Test 1: Docker Installation]")
        
        returncode, stdout, stderr = self.run_command(["docker", "--version"])
        
        if returncode == 0:
            version = stdout.strip()
            print(f"  ✅ Docker installed: {version}")
            return {"status": "pass", "version": version}
        else:
            print(f"  ❌ Docker not found: {stderr}")
            self.issues.append("Docker not installed or not accessible")
            return {"status": "fail", "error": stderr}
    
    def test_containers_running(self) -> Dict:
        """Test if required containers are running."""
        print("\n[Test 2: Container Status]")
        
        required_containers = [
            "tenable-sc-mcp",
            "tenable-sc-mcp-redis"
        ]
        
        returncode, stdout, stderr = self.run_command([
            "docker", "ps", "--format", "{{.Names}}\t{{.Status}}"
        ])
        
        if returncode != 0:
            print(f"  ❌ Failed to list containers: {stderr}")
            self.issues.append("Cannot list Docker containers")
            return {"status": "fail", "error": stderr}
        
        running_containers = {}
        for line in stdout.strip().split('\n'):
            if '\t' in line:
                name, status = line.split('\t', 1)
                running_containers[name] = status
        
        results = {}
        all_running = True
        
        for container in required_containers:
            if container in running_containers:
                status = running_containers[container]
                is_up = "Up" in status
                if is_up:
                    print(f"  ✅ {container}: {status}")
                else:
                    print(f"  ❌ {container}: {status}")
                    self.issues.append(f"Container {container} not running")
                    all_running = False
                results[container] = {"status": status, "running": is_up}
            else:
                print(f"  ❌ {container}: Not found")
                self.issues.append(f"Container {container} not found")
                all_running = False
                results[container] = {"status": "not_found", "running": False}
        
        return {
            "status": "pass" if all_running else "fail",
            "containers": results
        }
    
    def test_redis_health(self) -> Dict:
        """Test Redis container health."""
        print("\n[Test 3: Redis Health]")
        
        returncode, stdout, stderr = self.run_command([
            "docker", "inspect", "tenable-sc-mcp-redis",
            "--format", "{{.State.Health.Status}}"
        ])
        
        if returncode == 0:
            health = stdout.strip()
            is_healthy = health == "healthy"
            if is_healthy:
                print(f"  ✅ Redis health: {health}")
            else:
                print(f"  ⚠️  Redis health: {health}")
                self.issues.append(f"Redis not healthy: {health}")
            return {"status": "pass" if is_healthy else "warning", "health": health}
        else:
            print(f"  ⚠️  Cannot check Redis health (no healthcheck configured)")
            return {"status": "warning", "health": "unknown"}
    
    def test_container_logs(self) -> Dict:
        """Check container logs for errors."""
        print("\n[Test 4: Container Logs]")
        
        containers = ["tenable-sc-mcp", "tenable-sc-mcp-redis"]
        results = {}
        
        for container in containers:
            returncode, stdout, stderr = self.run_command([
                "docker", "logs", "--tail", "50", container
            ])
            
            if returncode == 0:
                log_lines = stdout.strip().split('\n')
                
                # Look for errors
                error_lines = [line for line in log_lines if 
                             re.search(r'\b(error|critical|fatal|exception)\b', line, re.IGNORECASE)]
                
                if error_lines:
                    print(f"  ⚠️  {container}: Found {len(error_lines)} error lines")
                    results[container] = {
                        "status": "warning",
                        "errors": len(error_lines),
                        "recent_errors": error_lines[-5:]  # Last 5 errors
                    }
                else:
                    print(f"  ✅ {container}: No errors in recent logs")
                    results[container] = {"status": "pass", "errors": 0}
            else:
                print(f"  ❌ {container}: Cannot read logs")
                results[container] = {"status": "fail", "error": stderr}
        
        return results
    
    def test_port_exposure(self) -> Dict:
        """Test if ports are correctly exposed."""
        print("\n[Test 5: Port Exposure]")
        
        expected_ports = {
            "tenable-sc-mcp": ["8000"],
            "tenable-sc-mcp-redis": ["6379"]
        }
        
        results = {}
        all_exposed = True
        
        for container, ports in expected_ports.items():
            returncode, stdout, stderr = self.run_command([
                "docker", "port", container
            ])
            
            if returncode == 0:
                exposed_ports = stdout.strip()
                
                for port in ports:
                    if port in exposed_ports:
                        print(f"  ✅ {container}: Port {port} exposed")
                        results[f"{container}:{port}"] = {"status": "pass", "exposed": True}
                    else:
                        print(f"  ❌ {container}: Port {port} not exposed")
                        self.issues.append(f"Port {port} not exposed on {container}")
                        results[f"{container}:{port}"] = {"status": "fail", "exposed": False}
                        all_exposed = False
            else:
                print(f"  ❌ {container}: Cannot check ports")
                results[container] = {"status": "fail", "error": stderr}
                all_exposed = False
        
        return {
            "status": "pass" if all_exposed else "fail",
            "ports": results
        }
    
    def test_volume_mounts(self) -> Dict:
        """Test volume mounts and configuration."""
        print("\n[Test 6: Volume Mounts]")
        
        returncode, stdout, stderr = self.run_command([
            "docker", "inspect", "tenable-sc-mcp",
            "--format", "{{json .Mounts}}"
        ])
        
        if returncode == 0:
            try:
                mounts = json.loads(stdout)
                
                # Check for config file mount
                config_mounted = False
                for mount in mounts:
                    if "/config/tsc.env" in mount.get("Destination", ""):
                        config_mounted = True
                        print(f"  ✅ Config file mounted: {mount.get('Source')}")
                        break
                
                if not config_mounted:
                    print("  ⚠️  No config file mounted")
                    self.issues.append("Config file not mounted")
                
                return {
                    "status": "pass" if config_mounted else "warning",
                    "config_mounted": config_mounted,
                    "mounts": len(mounts)
                }
            except json.JSONDecodeError:
                print("  ❌ Cannot parse mount info")
                return {"status": "fail", "error": "JSON parse error"}
        else:
            print("  ❌ Cannot inspect container mounts")
            return {"status": "fail", "error": stderr}
    
    def test_security_settings(self) -> Dict:
        """Test container security settings."""
        print("\n[Test 7: Security Settings]")
        
        container = "tenable-sc-mcp"
        
        # Check if running as non-root
        returncode, stdout, stderr = self.run_command([
            "docker", "inspect", container,
            "--format", "{{.Config.User}}"
        ])
        
        results = {}
        
        if returncode == 0:
            user = stdout.strip()
            is_non_root = user != "" and user != "0" and user != "root"
            
            if is_non_root:
                print(f"  ✅ Running as non-root user: {user}")
                results["non_root_user"] = {"status": "pass", "user": user}
            else:
                print(f"  ⚠️  Running as root user")
                self.issues.append("Container running as root")
                results["non_root_user"] = {"status": "warning", "user": user or "root"}
        
        # Check resource limits
        returncode, stdout, stderr = self.run_command([
            "docker", "inspect", container,
            "--format", "{{json .HostConfig.Memory}}"
        ])
        
        if returncode == 0:
            memory_limit = stdout.strip()
            if memory_limit == "0":
                print(f"  ⚠️  No memory limit set")
                results["memory_limit"] = {"status": "warning", "limit": "unlimited"}
            else:
                print(f"  ✅ Memory limit: {memory_limit} bytes")
                results["memory_limit"] = {"status": "pass", "limit": memory_limit}
        
        return results
    
    def test_network_connectivity(self) -> Dict:
        """Test network connectivity between containers."""
        print("\n[Test 8: Network Connectivity]")
        
        # Test if MCP server can reach Redis
        returncode, stdout, stderr = self.run_command([
            "docker", "exec", "tenable-sc-mcp",
            "sh", "-c", "command -v nc >/dev/null && nc -zv redis 6379 || echo 'nc not available'"
        ])
        
        # Alternative: Check via Docker network
        returncode2, stdout2, stderr2 = self.run_command([
            "docker", "network", "inspect", "tenable-sc-mcp-server_default"
        ])
        
        if returncode2 == 0:
            try:
                network_info = json.loads(stdout2)
                if network_info and len(network_info) > 0:
                    containers = network_info[0].get("Containers", {})
                    if len(containers) >= 2:
                        print(f"  ✅ Network configured: {len(containers)} containers connected")
                        return {"status": "pass", "containers_connected": len(containers)}
                    else:
                        print(f"  ⚠️  Only {len(containers)} container(s) on network")
                        return {"status": "warning", "containers_connected": len(containers)}
            except Exception as e:
                print(f"  ⚠️  Cannot parse network info: {e}")
                return {"status": "warning", "error": str(e)}
        
        print("  ⚠️  Cannot verify network connectivity")
        return {"status": "warning", "error": "Cannot inspect network"}
    
    def test_environment_variables(self) -> Dict:
        """Test if required environment variables are set."""
        print("\n[Test 9: Environment Variables]")
        
        returncode, stdout, stderr = self.run_command([
            "docker", "exec", "tenable-sc-mcp",
            "sh", "-c", "env | grep TSC_ | wc -l"
        ])
        
        if returncode == 0:
            count = int(stdout.strip()) if stdout.strip().isdigit() else 0
            
            if count >= 3:  # At least URL, ACCESS_KEY, SECRET_KEY
                print(f"  ✅ Environment configured: {count} TSC_* variables set")
                return {"status": "pass", "tsc_vars": count}
            else:
                print(f"  ❌ Insufficient environment: only {count} TSC_* variables")
                self.issues.append("Missing TSC environment variables")
                return {"status": "fail", "tsc_vars": count}
        else:
            print("  ⚠️  Cannot check environment variables")
            return {"status": "warning", "error": stderr}
    
    def run_all_tests(self) -> Dict:
        """Run all Docker and security tests."""
        print("\n" + "="*70)
        print("🐳 DOCKER DEPLOYMENT & SECURITY TESTS")
        print("="*70)
        
        results = {}
        
        results["docker_installed"] = self.test_docker_installed()
        results["containers_running"] = self.test_containers_running()
        results["redis_health"] = self.test_redis_health()
        results["container_logs"] = self.test_container_logs()
        results["port_exposure"] = self.test_port_exposure()
        results["volume_mounts"] = self.test_volume_mounts()
        results["security_settings"] = self.test_security_settings()
        results["network_connectivity"] = self.test_network_connectivity()
        results["environment_variables"] = self.test_environment_variables()
        
        return results


def main():
    """Run all tests and output results."""
    
    tester = DockerSecurityTest()
    results = tester.run_all_tests()
    
    # Save results
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    output_file = "docker_security_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to {output_file}")
    
    # Count results
    pass_count = 0
    warning_count = 0
    fail_count = 0
    
    for test_name, test_result in results.items():
        if isinstance(test_result, dict):
            status = test_result.get("status", "unknown")
            if status == "pass":
                pass_count += 1
            elif status == "warning":
                warning_count += 1
            elif status == "fail":
                fail_count += 1
    
    print(f"\n🎯 RESULTS:")
    print(f"  • Tests passed:  {pass_count}")
    print(f"  • Warnings:      {warning_count}")
    print(f"  • Tests failed:  {fail_count}")
    
    # Show issues
    if tester.issues:
        print(f"\n⚠️  ISSUES FOUND ({len(tester.issues)}):")
        for i, issue in enumerate(tester.issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✅ No critical issues found")
    
    print("\n" + "="*70)
    if fail_count == 0:
        print("✅ DOCKER DEPLOYMENT VALIDATED")
    else:
        print("⚠️  DOCKER DEPLOYMENT HAS ISSUES")
    print("="*70)
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
