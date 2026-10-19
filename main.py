"""
Chương trình chính chạy trên ESP32 (MicroPython) kết hợp:
  1. Cảm biến siêu âm RCWL-1601: TRIG -> D5 (GPIO 5), ECHO -> D18 (GPIO 18)
  2. Cảm biến nhiệt độ DHT11 (3 chân): OUT -> D4 (GPIO 4), + -> V (3.3V), - -> G (GND)
"""

import time
from rcwl1601 import RCWL1601, RCWL1601Error, DHT11Sensor


class DistanceMonitorApp:
    """Lớp quản lý luồng đo khoảng cách siêu âm có bù nhiệt độ thực tế từ DHT11."""

    def __init__(
        self,
        trig_pin: int = 5,
        echo_pin: int = 18,
        dht_pin: int = 4,
        temperature_c: float = 25.0,
        interval_ms: int = 250,
    ):
        self.dht_sensor = DHT11Sensor(data_pin=dht_pin, default_temp_c=temperature_c)
        self.sensor = RCWL1601(
            trig_pin=trig_pin,
            echo_pin=echo_pin,
            temperature_c=temperature_c,
        )
        self.interval_ms = interval_ms

    def update_ambient_temperature(self) -> float:
        """Đọc nhiệt độ từ DHT11 và cập nhật vận tốc âm thanh cho RCWL-1601."""
        temp_c = self.dht_sensor.read_temperature_c()
        self.sensor.temperature_c = temp_c
        return temp_c

    def measure_n_times(self, n: int, use_filter: bool = True) -> list:
        """
        Đọc nhiệt độ thực tế từ DHT11 để bù vận tốc âm thanh, sau đó đo tự động n lần.
        In thời gian truyền sóng t (us, 3 chữ số thập phân) và khoảng cách (cm, 6 chữ số thập phân).
        """
        results = []
        temp_c = self.update_ambient_temperature()
        print(
            f"\n--- Bat dau do {n} lan "
            f"(Nhiet do DHT11: {temp_c:.1f} °C | Van toc am: {self.sensor.sound_speed_m_s:.2f} m/s) ---"
        )

        for i in range(1, n + 1):
            try:
                temp_c = self.update_ambient_temperature()
                if use_filter:
                    time_us, dist_cm = self.sensor.read_filtered_sample(samples=3, delay_ms=60)
                else:
                    time_us, dist_cm = self.sensor.read_sample()

                results.append((time_us, dist_cm, temp_c))
                print(
                    f"[{i}/{n}] T = {temp_c:.1f} °C | t = {time_us:.3f} us | Khoang cach: {dist_cm:.6f} cm"
                )
                print(f"CSV_DATA:{time_us:.3f},{dist_cm:.6f},{temp_c:.1f}")
            except RCWL1601Error as err:
                print(f"[{i}/{n}] [Canh bao] {err}")

            if i < n:
                time.sleep_ms(self.interval_ms)

        print("=== DONE_BATCH ===")
        return results

    def run_interactive(self, use_filter: bool = True) -> None:
        """
        Lắng nghe số lần đo n từ người dùng trên REPL, đo n lần rồi tiếp tục lắng nghe.
        """
        temp_c = self.update_ambient_temperature()
        print("==================================================")
        print("  DO KHOANG CACH RCWL-1601 + DHT11 (OOP)          ")
        print(f"  Nhiet do DHT11 hien tai: {temp_c:.1f} °C")
        print("==================================================")

        try:
            while True:
                raw = input("\nNhap so lan do n (hoac 'q' de thoat): ").strip()
                if not raw:
                    continue
                if raw.lower() in ("q", "exit", "quit"):
                    print("Da thoat che do do.")
                    break
                try:
                    n = int(raw)
                    if n <= 0:
                        print("[!] Vui long nhap so nguyen duong (n > 0).")
                        continue
                except ValueError:
                    print("[!] Gia tri khong hop le! Vui long nhap mot so nguyen n.")
                    continue

                self.measure_n_times(n, use_filter=use_filter)

        except KeyboardInterrupt:
            print("\nDa dung chuong trinh do.")


if __name__ == "__main__":
    app = DistanceMonitorApp(
        trig_pin=5,
        echo_pin=18,
        dht_pin=4,
        temperature_c=25.0,
        interval_ms=250,
    )
    app.run_interactive(use_filter=True)
