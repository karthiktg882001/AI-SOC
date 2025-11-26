"""
System Info Router - Real-time system information collection
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import platform
import psutil
import socket
from database import get_db
from models import SystemInfo, User
from routers.auth import get_current_user

router = APIRouter()

class SystemInfoResponse(BaseModel):
    platform: str
    os_version: str
    cpu_info: Dict[str, Any]
    memory_info: Dict[str, Any]
    network_info: Dict[str, Any]
    disk_info: Dict[str, Any]
    processes: List[Dict[str, Any]]
    timestamp: str

@router.get("/realtime", response_model=SystemInfoResponse)
async def get_realtime_system_info(current_user: User = Depends(get_current_user)):
    """Get real-time system information"""
    try:
        # Platform info
        platform_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": socket.gethostname()
        }
        
        # CPU info
        cpu_info = {
            "count": psutil.cpu_count(),
            "percent": psutil.cpu_percent(interval=1),
            "per_cpu": psutil.cpu_percent(interval=1, percpu=True),
            "freq": {
                "current": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                "min": psutil.cpu_freq().min if psutil.cpu_freq() else None,
                "max": psutil.cpu_freq().max if psutil.cpu_freq() else None
            }
        }
        
        # Memory info
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": swap.percent
        }
        
        # Network info
        network = psutil.net_io_counters()
        network_info = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv,
            "interfaces": []
        }
        
        # Network interfaces
        interfaces = psutil.net_if_addrs()
        for interface_name, addresses in interfaces.items():
            interface_info = {
                "name": interface_name,
                "addresses": []
            }
            for addr in addresses:
                interface_info["addresses"].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask if hasattr(addr, 'netmask') else None
                })
            network_info["interfaces"].append(interface_info)
        
        # Disk info
        disk_info = {
            "partitions": [],
            "usage": {}
        }
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info["partitions"].append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            except PermissionError:
                pass
        
        # Processes (top 20 by CPU)
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] is not None:
                    processes.append({
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "cpu_percent": proc_info['cpu_percent'],
                        "memory_percent": proc_info['memory_percent'],
                        "status": proc_info['status']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU and get top 20
        processes = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:20]
        
        return SystemInfoResponse(
            platform=platform_info["system"],
            os_version=f"{platform_info['system']} {platform_info['release']} {platform_info['version']}",
            cpu_info=cpu_info,
            memory_info=memory_info,
            network_info=network_info,
            disk_info=disk_info,
            processes=processes,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting system info: {str(e)}")

@router.get("/version")
async def get_version():
    """Get application version"""
    return {
        "version": "1.0.0",
        "name": "AI SOC Assistant",
        "description": "AI-Driven Security Operations Center",
        "build_date": "2024-01-01",
        "features": [
            "Real-time Threat Detection",
            "Deep Learning Anomaly Detection",
            "Generative AI Analysis",
            "Active Defense System",
            "Multi-platform Support"
        ]
    }

@router.post("/save-system-info")
async def save_system_info(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save system info to database"""
    try:
        system_info_data = await get_realtime_system_info(current_user)
        
        system_info = SystemInfo(
            user_id=current_user.id,
            device_id=device_id,
            platform=system_info_data.platform,
            os_version=system_info_data.os_version,
            cpu_info=system_info_data.cpu_info,
            memory_info=system_info_data.memory_info,
            network_info=system_info_data.network_info,
            disk_info=system_info_data.disk_info,
            processes=system_info_data.processes,
            timestamp=datetime.now()
        )
        
        db.add(system_info)
        db.commit()
        db.refresh(system_info)
        
        return {"message": "System info saved successfully", "id": system_info.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving system info: {str(e)}")

