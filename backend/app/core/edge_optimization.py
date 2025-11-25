"""
Edge device optimization utilities
Optimized for Jetson Nano and similar edge devices
"""
import os
from typing import Dict, Any
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
import structlog

logger = structlog.get_logger()


def is_edge_device() -> bool:
    """
    Detect if running on edge device (Jetson Nano, etc.)
    Laptops/desktops are NOT considered edge devices even with low memory
    """
    # Check for Jetson Nano specifically (most reliable method)
    if os.path.exists("/proc/device-tree/model"):
        try:
            with open("/proc/device-tree/model", "r") as f:
                model = f.read().strip()
                if "jetson" in model.lower() or "nano" in model.lower():
                    logger.info("Jetson device detected", model=model)
                    return True
        except Exception:
            pass
    
    # Check for Raspberry Pi or other ARM-based edge devices
    if os.path.exists("/proc/cpuinfo"):
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
                # Check for ARM architecture (common in edge devices)
                if "ARM" in cpuinfo or "arm" in cpuinfo:
                    # But exclude if it's a laptop/desktop (check for x86_64)
                    import platform
                    machine = platform.machine()
                    if "arm" in machine.lower() and "x86" not in machine.lower():
                        # Check if it's actually a Jetson/Raspberry Pi
                        if "jetson" in cpuinfo.lower() or "raspberry" in cpuinfo.lower():
                            logger.info("ARM edge device detected")
                            return True
        except Exception:
            pass
    
    # Check environment variable (explicit override)
    edge_env = os.getenv("EDGE_DEVICE", "").lower()
    if edge_env == "true":
        logger.info("Edge device mode enabled via environment variable")
        return True
    elif edge_env == "false":
        logger.info("Edge device mode disabled via environment variable")
        return False
    
    # Check config setting for forced edge mode
    try:
        from app.core.config import settings
        if hasattr(settings, 'FORCE_EDGE_MODE') and settings.FORCE_EDGE_MODE:
            logger.info("Edge device mode forced via FORCE_EDGE_MODE setting")
            return True
    except Exception:
        pass
    
    # Laptops/desktops are NOT edge devices by default
    # Even with low memory, we assume it's a development machine
    # User can explicitly set EDGE_DEVICE=true if needed
    return False


def get_optimal_model_size() -> str:
    """
    Get optimal Ollama model size for current device
    - Edge devices (Jetson Nano): qwen:0.5b (fastest, lowest memory)
    - Laptops/Desktops: Use larger models for better quality
    """
    if is_edge_device():
        # qwen:0.5b is optimized for Jetson Nano - fastest with lowest parameters
        if PSUTIL_AVAILABLE:
            try:
                memory_gb = psutil.virtual_memory().total / (1024 ** 3)
                if memory_gb < 4:
                    return "qwen:0.5b"  # Fastest, lowest memory (recommended for Jetson Nano)
                elif memory_gb < 6:
                    return "qwen:0.5b"  # Still best for speed
                else:
                    return "qwen:0.5b"  # Default for edge devices
            except Exception:
                pass
        # Default for edge devices - qwen:0.5b is fastest
        return "qwen:0.5b"
    else:
        # Laptops/Desktops: Always use llama3.2:3b (never qwen:0.5b)
        from app.core.config import settings
        user_model = settings.OLLAMA_MODEL
        
        # Force llama3.2:3b for laptops (better quality)
        if user_model and user_model != "qwen:0.5b":
            return user_model  # Use user's specified model if not qwen
        else:
            # Default to llama3.2:3b for laptops
            return "llama3.2:3b"


def get_optimal_whisper_model() -> str:
    """Get optimal Whisper model size for current device"""
    if is_edge_device():
        if PSUTIL_AVAILABLE:
            try:
                memory_gb = psutil.virtual_memory().total / (1024 ** 3)
                if memory_gb < 4:
                    return "tiny"  # ~39MB, fastest
                elif memory_gb < 6:
                    return "base"  # ~74MB, good balance
                else:
                    return "small"  # ~244MB, better quality
            except Exception:
                pass
        # Default for edge devices
        return "base"
    else:
        return "base"  # Default


def optimize_for_edge() -> Dict[str, Any]:
    """Get optimization settings for edge devices"""
    is_edge = is_edge_device()
    
    return {
        "is_edge_device": is_edge,
        "ollama_model": get_optimal_model_size(),
        "whisper_model": get_optimal_whisper_model(),
        "rag_chunks": 3 if is_edge else 5,  # Fewer chunks for edge
        "max_tokens": 2000 if is_edge else 4000,  # Shorter responses
        "temperature": 0.1,  # Lower temperature for consistency
        "enable_caching": True,  # Always cache on edge devices
    }

