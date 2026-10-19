"""
Module OOP điều khiển cảm biến siêu âm RCWL-1601 kết hợp cảm biến nhiệt độ DHT11
trên ESP32 (MicroPython).
Học phần: Kỹ thuật đo lường và cảm biến (EMA2024E_3)
"""

from machine import Pin, time_pulse_us
import dht
import time


class RCWL1601Error(Exception):
    """Ngoại lệ khi cảm biến RCWL-1601 đo ngoài phạm vi hoặc lỗi kết nối."""
    pass


class DHT11Sensor:
    """
    Lớp (Class) đại diện cho cảm biến nhiệt độ - độ ẩm DHT11 (3 chân: +, -, OUT).
    Dùng để đo nhiệt độ môi trường thực tế và bù vận tốc âm thanh cho RCWL-1601.
    """

    def __init__(self, data_pin: int = 4, default_temp_c: float = 25.0):
        self.pin = Pin(data_pin, Pin.IN, Pin.PULL_UP)
        self._dht = dht.DHT11(self.pin)
        self.last_temp_c = default_temp_c
        self.last_humidity = 0.0
        self._last_read_ms = 0

    def read_temperature_c(self) -> float:
        """
        Đọc nhiệt độ (°C) từ DHT11.
        DHT11 yêu cầu chu kỳ đọc tối thiểu ~1000ms. Nếu đọc quá nhanh hoặc lỗi,
        trả về giá trị nhiệt độ hợp lệ gần nhất.
        """
        now_ms = time.ticks_ms()
        if self._last_read_ms == 0 or time.ticks_diff(now_ms, self._last_read_ms) >= 1000:
            try:
                self._dht.measure()
                self.last_temp_c = float(self._dht.temperature())
                self.last_humidity = float(self._dht.humidity())
                self._last_read_ms = now_ms
            except Exception as err:
                print(f"[DHT11 Canh bao] Khong doc duoc DHT11 ({err}), dung nhiet do {self.last_temp_c:.1f} °C")
        return self.last_temp_c


class RCWL1601:
    """
    Lớp (Class) đại diện cho cảm biến khoảng cách siêu âm RCWL-1601.

    Thuộc tính:
        trig (Pin): Chân xuất xung kích hoạt (OUTPUT).
        echo (Pin): Chân nhận xung phản hồi (INPUT).
        timeout_us (int): Thời gian chờ xung tối đa (micro-giây).
        temperature_c (float): Nhiệt độ môi trường (°C) để bù vận tốc âm thanh.
    """

    MIN_DISTANCE_CM = 2.0
    MAX_DISTANCE_CM = 450.0

    def __init__(
        self,
        trig_pin: int = 5,
        echo_pin: int = 18,
        timeout_us: int = 30000,
        temperature_c: float = 25.0,
    ):
        self.trig = Pin(trig_pin, Pin.OUT, value=0)
        self.echo = Pin(echo_pin, Pin.IN)
        self.timeout_us = timeout_us
        self._temperature_c = temperature_c
        self._sound_speed_cm_us = self._calc_sound_speed(temperature_c)

    @staticmethod
    def _calc_sound_speed(temp_c: float) -> float:
        """
        Tính vận tốc âm thanh (cm/us) có bù nhiệt độ:
        v (m/s) = 331.3 + 0.606 * T(°C)
        Đổi sang cm/us: chia cho 10,000.
        """
        speed_m_s = 331.3 + 0.606 * temp_c
        return speed_m_s / 10000.0

    @property
    def temperature_c(self) -> float:
        return self._temperature_c

    @temperature_c.setter
    def temperature_c(self, temp_c: float) -> None:
        self._temperature_c = temp_c
        self._sound_speed_cm_us = self._calc_sound_speed(temp_c)

    @property
    def sound_speed_m_s(self) -> float:
        """Vận tốc âm thanh hiện tại (m/s)."""
        return self._sound_speed_cm_us * 10000.0

    def _send_trigger_pulse(self) -> None:
        """Phát xung HIGH tối thiểu 10us tại chân TRIG."""
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)

    def measure_pulse_us(self) -> int:
        """
        Đo độ rộng xung HIGH (micro-giây) tại chân ECHO.
        Ném ngoại lệ RCWL1601Error nếu timeout (< 0).
        """
        self._send_trigger_pulse()
        duration = time_pulse_us(self.echo, 1, self.timeout_us)
        if duration < 0:
            raise RCWL1601Error("Timeout: Khong nhan duoc xung phan xa (ngoai vung do hoac chua cam day).")
        return duration

    def read_sample(self) -> tuple:
        """
        Đo 1 lần và trả về bộ (time_us, distance_cm):
            - time_us (float): Thời gian truyền sóng siêu âm tính bằng micro-giây (us).
            - distance_cm (float): Khoảng cách tính bằng cm (đã bù nhiệt độ).
        """
        duration_us = self.measure_pulse_us()
        time_us = float(duration_us)
        distance_cm = (duration_us * self._sound_speed_cm_us) / 2.0
        return time_us, distance_cm

    def read_distance_cm(self) -> float:
        """Đo và trả về khoảng cách (đơn vị: cm) cho 1 lần đo."""
        _, distance_cm = self.read_sample()
        return distance_cm

    def read_filtered_sample(self, samples: int = 3, delay_ms: int = 60) -> tuple:
        """
        Đo nhiều mẫu và lọc trung vị (Median Filter), trả về (time_us, distance_cm).
        """
        valid_samples = []
        for _ in range(samples):
            try:
                time_us, dist_cm = self.read_sample()
                if self.MIN_DISTANCE_CM <= dist_cm <= self.MAX_DISTANCE_CM:
                    valid_samples.append((time_us, dist_cm))
            except RCWL1601Error:
                pass
            time.sleep_ms(delay_ms)

        if not valid_samples:
            raise RCWL1601Error("Ngoai pham vi do (2cm - 450cm) hoac loi tin hieu.")

        valid_samples.sort(key=lambda item: item[1])
        mid = len(valid_samples) // 2
        return valid_samples[mid]

    def read_filtered_cm(self, samples: int = 3, delay_ms: int = 60) -> float:
        """Đo nhiều mẫu có lọc trung vị và chỉ trả về khoảng cách (cm)."""
        _, dist_cm = self.read_filtered_sample(samples=samples, delay_ms=delay_ms)
        return dist_cm
