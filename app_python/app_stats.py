import platform
import socket

from datetime import datetime, timezone
from typing import Dict


class AppStats:
    def __init__(self, name: str, description: str, major_version: int, minor_version: int, patch_version: int):
        if len(name) == 0 or name is None:
            raise ValueError("The service name must not be empty!")
        
        if len(description) == 0 or description is None:
            raise ValueError("The service description must not be empty!")
        
        if major_version < 0 or minor_version < 0 or patch_version < 0:
            raise ValueError("The service version must be non negative!")
        
        self.start_time = datetime.now(timezone.utc)
        self.name = name
        self.description = description
        self.version = f"{major_version}.{minor_version}.{patch_version}"
        self.framework = "FastAPI"

    def provide_service_info(self) -> Dict[str, Any]: 
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "framework": self.framework
        }
    
    def provide_system_info(self) -> Dict[str, Any]:
        return {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "cpu_count": os.cpu_count(),
            "python_version": platform.python_version()
        }
    
    def get_uptime(self) -> float:
        delta = datetime.now(timezone.utc) - self.start_time
        return delta.total_seconds()
    
    def provide_runtime_info(self) -> Dict[str, str]:
        uptime_seconds = int(self.get_uptime())
        uptime_minutes = (uptime_seconds // 60) % 60
        uptime_hours = uptime_seconds // 3600

        if uptime_hours > 1 or uptime_hours == 0:
            hours_adapted_wording = "hours"
        else:
            hours_adapted_wording = "hour"

        if uptime_minutes > 1 or uptime_minutes == 0:
            minutes_adapted_wording = "minutes"
        else:
            minutes_adapted_wording = "minute"

        return {
            "uptime_seconds": uptime_seconds,
            "uptime_human": f"{uptime_hours} {hours_adapted_wording}, {uptime_minutes} {minutes_adapted_wording}",
            "current_time": datetime.now(timezone.utc).isoformat(),
            "timezone": "UTC"
        }
