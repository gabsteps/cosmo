import time
import psutil


class SystemMonitor:

    def __init__(self):

        self._last_net_io = psutil.net_io_counters()
        self._last_net_time = time.time()

        # Primeira chamada inicializa o cálculo interno do psutil.
        psutil.cpu_percent(interval=None)

    def snapshot(
        self
    ) -> dict:

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu_percent = psutil.cpu_percent(
            interval=None
        )

        temperature = self._get_temperature()

        network = self._get_network_usage()

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
            "network_upload_human": self._format_rate(
                network["upload_bps"]
            ),
            "network_download_human": self._format_rate(
                network["download_bps"]
            ),
        }

    def _get_temperature(
        self
    ) -> float | None:

        try:
            sensors = psutil.sensors_temperatures()

            if not sensors:
                return None

            preferred_keys = (
                "coretemp",
                "k10temp",
                "cpu_thermal",
                "acpitz",
                "thermal_zone"
            )

            for key in preferred_keys:

                if key not in sensors:
                    continue

                entries = sensors[key]

                if not entries:
                    continue

                temperatures = [
                    entry.current
                    for entry in entries
                    if entry.current is not None
                ]

                if temperatures:
                    return round(
                        max(temperatures),
                        1
                    )

            for entries in sensors.values():

                temperatures = [
                    entry.current
                    for entry in entries
                    if entry.current is not None
                ]

                if temperatures:
                    return round(
                        max(temperatures),
                        1
                    )

        except Exception:
            return None

        return None

    def _get_network_usage(
        self
    ) -> dict:

        now = time.time()
        current = psutil.net_io_counters()

        elapsed = max(
            now - self._last_net_time,
            0.001
        )

        upload_bps = (
            current.bytes_sent
            - self._last_net_io.bytes_sent
        ) / elapsed

        download_bps = (
            current.bytes_recv
            - self._last_net_io.bytes_recv
        ) / elapsed

        self._last_net_io = current
        self._last_net_time = now

        return {
            "upload_bps": max(
                0,
                round(upload_bps, 2)
            ),
            "download_bps": max(
                0,
                round(download_bps, 2)
            ),
        }

    def _format_rate(
        self,
        bytes_per_second: float
    ) -> str:

        units = (
            "B/s",
            "KB/s",
            "MB/s",
            "GB/s"
        )

        value = float(
            bytes_per_second
        )

        for unit in units:

            if value < 1024:
                return f"{value:.1f} {unit}"

            value /= 1024

        return f"{value:.1f} TB/s"


system_monitor = SystemMonitor()