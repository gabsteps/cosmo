import os
import time
import psutil


class SystemMonitor:

    def __init__(self):

        self.process = psutil.Process(os.getpid())

        self._last_net_io = psutil.net_io_counters()
        self._last_net_time = time.time()

        psutil.cpu_percent(interval=None)

        self.process.cpu_percent(interval=None)

    def snapshot(self) -> dict:

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu_percent = psutil.cpu_percent(interval=None)

        temperature = self._get_temperature()
        network = self._get_network_usage()
        process = self._get_process_usage()

        return {
            "cpu_percent": cpu_percent,
            "memory_total": memory.total,
            "memory_used": memory.used,
            "memory_available": memory.available,
            "memory_percent": memory.percent,
            "disk_total": disk.total,
            "disk_used": disk.used,
            "disk_free": disk.free,
            "disk_percent": disk.percent,
            "temperature_celsius": temperature,
            "network_upload_bps": network["upload_bps"],
            "network_download_bps": network["download_bps"],
            "network_upload_human": self._format_rate(network["upload_bps"]),
            "network_download_human": self._format_rate(network["download_bps"]),
            "process": process,
        }

    def _get_process_usage(self) -> dict:

        try:

            memory = self.process.memory_info()

            return {
                "pid": self.process.pid,
                "name": self.process.name(),
                "status": self.process.status(),
                "cpu_percent": self.process.cpu_percent(interval=None),
                "memory_rss": memory.rss,
                "memory_vms": memory.vms,
                "memory_percent": round(self.process.memory_percent(), 2),
                "threads": self.process.num_threads(),
                "open_files": len(self.process.open_files()),
                "uptime_seconds": int(time.time() - self.process.create_time()),
                "memory_rss_human": self._format_bytes(memory.rss),
                "memory_vms_human": self._format_bytes(memory.vms),
            }

        except Exception as error:

            return {"error": str(error)}

    def _get_temperature(self) -> float | None:

        try:

            sensors = psutil.sensors_temperatures()

            if not sensors:
                return None

            preferred_keys = (
                "coretemp",
                "k10temp",
                "cpu_thermal",
                "acpitz",
                "thermal_zone",
            )

            for key in preferred_keys:

                if key not in sensors:
                    continue

                temperatures = [
                    entry.current for entry in sensors[key] if entry.current is not None
                ]

                if temperatures:
                    return round(max(temperatures), 1)

            for entries in sensors.values():

                temperatures = [
                    entry.current for entry in entries if entry.current is not None
                ]

                if temperatures:
                    return round(max(temperatures), 1)

        except Exception:

            return None

        return None

    def _get_network_usage(self) -> dict:

        now = time.time()
        current = psutil.net_io_counters()

        elapsed = max(now - self._last_net_time, 0.001)

        upload_bps = (current.bytes_sent - self._last_net_io.bytes_sent) / elapsed

        download_bps = (current.bytes_recv - self._last_net_io.bytes_recv) / elapsed

        self._last_net_io = current
        self._last_net_time = now

        return {
            "upload_bps": max(0, round(upload_bps, 2)),
            "download_bps": max(0, round(download_bps, 2)),
        }

    def _format_rate(self, bytes_per_second: float) -> str:

        return self._format_bytes(bytes_per_second) + "/s"

    def _format_bytes(self, value: float) -> str:

        units = ("B", "KB", "MB", "GB", "TB")

        value = float(value)

        for unit in units:

            if value < 1024:
                return f"{value:.1f} {unit}"

            value /= 1024

        return f"{value:.1f} PB"


system_monitor = SystemMonitor()
