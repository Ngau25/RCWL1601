"""
Script chạy trên máy tính (Terminal) để tự động nạp code OOP vào ESP32,
lắng nghe 2 thông số '<số_lần_đo>, <tên_file>' và xuất dữ liệu ra thư mục result/<tên_file>.csv.

Cách chạy:
    - Nạp code:      python run_terminal.py --upload
    - Bắt đầu đo:    python run_terminal.py --measure
"""

import csv
import sys
import time
from pathlib import Path
import serial
import serial.tools.list_ports

BASE_DIR = Path(__file__).resolve().parent
RESULT_DIR = BASE_DIR / "result"


class ESP32TerminalRunner:
    """Lớp kết nối cổng Serial, nạp file MicroPython, điều khiển đo và xuất file CSV."""

    def __init__(self, port: str | None = None, baudrate: int = 115200):
        self.port = port or self._auto_detect_port()
        self.baudrate = baudrate
        self.ser: serial.Serial | None = None

    @staticmethod
    def _auto_detect_port() -> str:
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            desc = (p.description or "").lower()
            if any(k in desc for k in ("cp210", "ch340", "usb", "uart", "serial")):
                return p.device
        if ports:
            return ports[0].device
        raise RuntimeError("Khong tim thay cong COM nao ket noi voi ESP32!")

    def connect_and_break(self) -> None:
        print(f"[*] Dang ket noi toi ESP32 tai cong {self.port} ({self.baudrate} baud)...")
        self.ser = serial.Serial(self.port, self.baudrate, timeout=0.5)
        self.ser.dtr = False
        self.ser.rts = False
        time.sleep(1.5)

        for _ in range(3):
            self.ser.write(b"\x03\x03")
            time.sleep(0.35)
        self.ser.read_all()

    def _exec_raw(self, code_str: str) -> str:
        assert self.ser is not None
        self.ser.write(b"\x01")
        time.sleep(0.2)
        self.ser.read_all()

        self.ser.write(code_str.encode("utf-8") + b"\x04")
        time.sleep(0.4)
        out = self.ser.read_all().decode("utf-8", errors="ignore")

        self.ser.write(b"\x02")
        time.sleep(0.1)
        self.ser.read_all()
        return out

    def upload_file(self, local_path: str, remote_name: str) -> None:
        print(f"[*] Dang nap file '{local_path}' -> ESP32:/{remote_name} ...")
        with open(local_path, "rb") as f:
            content = f.read()

        cmd = (
            f"f = open('{remote_name}', 'wb')\n"
            f"f.write({repr(content)})\n"
            f"f.close()\n"
            f"print('UPLOAD_OK:{remote_name}')\n"
        )
        res = self._exec_raw(cmd)
        if f"UPLOAD_OK:{remote_name}" not in res:
            print(f"[!] Phan hoi khi nap {remote_name}: {res}")
        else:
            print(f"[+] Nap thanh cong '{remote_name}'!")

    def _init_esp32_app(self) -> None:
        """Khởi tạo đối tượng DistanceMonitorApp trên ESP32."""
        assert self.ser is not None
        init_cmd = (
            "import sys\n"
            "sys.modules.pop('rcwl1601', None)\n"
            "sys.modules.pop('main', None)\n"
            "import main\n"
            "app = main.DistanceMonitorApp(trig_pin=5, echo_pin=18, dht_pin=4, interval_ms=250)\n"
            "print('APP_READY')\n"
        )
        res = self._exec_raw(init_cmd)
        if "APP_READY" not in res:
            raise RuntimeError(
                "Chua khoi tao duoc module tren ESP32. Vui long chay 'nap_code.bat' truoc!"
            )

    def run_batch_on_esp32(self, n: int) -> list[tuple[str, str, str]]:
        """
        Gửi lệnh đo n lần xuống ESP32, in kết quả trực tiếp ra Terminal
        và thu thập danh sách các dòng (t, distance_cm, temperature_c) để xuất CSV.
        """
        assert self.ser is not None
        self.ser.read_all()
        cmd = f"_ = app.measure_n_times({n}, use_filter=True)\r\n"
        self.ser.write(cmd.encode("utf-8"))

        collected_rows: list[tuple[str, str, str]] = []
        while True:
            line = self.ser.readline()
            if not line:
                continue
            text = line.decode("utf-8", errors="ignore").strip()
            if not text:
                continue
            if "app.measure_n_times" in text or text.startswith(">>>") or text.startswith("..."):
                continue
            if "=== DONE_BATCH ===" in text:
                break
            if text.startswith("CSV_DATA:"):
                payload = text.split("CSV_DATA:", 1)[1]
                parts = payload.split(",")
                if len(parts) == 3:
                    collected_rows.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
                continue
            print(text)

        return collected_rows

    @staticmethod
    def save_to_csv(filename: str, rows: list[tuple[str, str, str]]) -> Path:
        """Lưu danh sách (t, distance_cm, temperature_c) vào thư mục result/<filename>.csv."""
        RESULT_DIR.mkdir(parents=True, exist_ok=True)
        clean_name = filename.strip()
        if not clean_name.lower().endswith(".csv"):
            clean_name += ".csv"

        csv_path = RESULT_DIR / clean_name
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["t", "distance_cm", "temperature_c"])
            for t_val, dist_val, temp_val in rows:
                writer.writerow([t_val, dist_val, temp_val])

        return csv_path

    @staticmethod
    def _parse_user_input(user_in: str) -> tuple[int, str]:
        """Tách 2 thông số '<số_lần_đo>, <tên_file>' cách nhau bởi dấu phẩy."""
        if "," not in user_in:
            raise ValueError(
                "Vui long nhap 2 thong so cach nhau boi dau phay: <so_lan_do>, <ten_file> (VD: 10, do_lan_1)"
            )
        raw_n, raw_name = user_in.split(",", 1)
        try:
            n = int(raw_n.strip())
        except ValueError:
            raise ValueError("Thong so dau tien (so lan do) phai la mot so nguyen!")

        if n <= 0:
            raise ValueError("So lan do phai la so nguyen duong (n > 0)!")

        filename = raw_name.strip()
        if not filename:
            raise ValueError("Thong so thu hai (ten file) khong duoc de trong!")

        return n, filename

    def interactive_measurement(self) -> None:
        """
        Lắng nghe 2 thông số '<số_lần_đo>, <tên_file>' từ người dùng,
        tự động đo n lần, lưu ra file result/<tên_file>.csv rồi tiếp tục lắng nghe.
        """
        self._init_esp32_app()
        print("\n============================================================")
        print("  SAN SANG DO KHOANG CACH RCWL-1601 & XUAT FILE CSV (OOP)   ")
        print("  Cu phap nhap: <so_lan_do>, <ten_file>  (Vi du: 10, test1) ")
        print("  Nhap 'q' de thoat chuong trinh.                           ")
        print("============================================================")

        try:
            while True:
                user_in = input("\n>> Nhap '<so_lan_do>, <ten_file>' (hoac 'q' de thoat): ").strip()
                if not user_in:
                    continue
                if user_in.lower() in ("q", "exit", "quit"):
                    print("[*] Da thoat che do do.")
                    break

                try:
                    n, filename = self._parse_user_input(user_in)
                except ValueError as err:
                    print(f"[!] {err}")
                    continue

                rows = self.run_batch_on_esp32(n)
                csv_path = self.save_to_csv(filename, rows)
                rel_path = csv_path.relative_to(BASE_DIR).as_posix()
                print(f"[+] Da xuat {len(rows)} gia tri do ra file: {rel_path}")

        except KeyboardInterrupt:
            print("\n[*] Da dung chuong trinh do.")
        finally:
            self.close()

    def close(self) -> None:
        if self.ser is not None and self.ser.is_open:
            try:
                self.ser.write(b"\x03\x03")
                time.sleep(0.1)
            except Exception:
                pass
            self.ser.close()


if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    try:
        runner = ESP32TerminalRunner()
        runner.connect_and_break()

        if mode in ("--upload", "upload"):
            runner.upload_file(str(BASE_DIR / "rcwl1601.py"), "rcwl1601.py")
            runner.upload_file(str(BASE_DIR / "main.py"), "main.py")
            runner.close()
            print("\n[OK] Da nap xong toan bo code vao ESP32!")
        elif mode in ("--measure", "measure"):
            runner.interactive_measurement()
        else:
            runner.upload_file(str(BASE_DIR / "rcwl1601.py"), "rcwl1601.py")
            runner.upload_file(str(BASE_DIR / "main.py"), "main.py")
            runner.interactive_measurement()
    except Exception as exc:
        print(f"\n[LOI KET NOI] {exc}")
        print("-> Vui long kiem tra day cap USB cam vao ESP32 hoac tat cac phan mem dang chiem cong COM (Thonny/Arduino).")
        sys.exit(1)
