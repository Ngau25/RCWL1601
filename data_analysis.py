"""
Module phân tích thống kê và vẽ đồ thị dữ liệu đo khoảng cách từ thư mục result/.
Học phần: Kỹ thuật đo lường và cảm biến (EMA2024E_3)
"""

import csv
import math
import statistics
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESULT_DIR = BASE_DIR / "result"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class DistanceDataAnalyzer:
    """
    Lớp (Class) đọc file CSV trong thư mục result/, tính toán các đại lượng thống kê
    cho cột khoảng cách `distance_cm` và vẽ bộ 4 đồ thị phân tích kỹ thuật đo lường.
    """

    def __init__(self, result_dir: Path = RESULT_DIR):
        self.result_dir = Path(result_dir)

    def resolve_csv_path(self, filename: str) -> Path:
        """Chuẩn hóa tên file và trả về đường dẫn đầy đủ trong thư mục result/."""
        clean_name = filename.strip()
        if not clean_name.lower().endswith(".csv"):
            clean_name += ".csv"
        csv_path = self.result_dir / clean_name
        if not csv_path.exists():
            raise FileNotFoundError(f"Khong tim thay file: {csv_path}")
        return csv_path

    def load_records(self, filename: str) -> list[dict[str, float]]:
        """
        Đọc toàn bộ các dòng từ file CSV và trả về danh sách dict:
        [{"t": float, "distance_cm": float, "temperature_c": float (nếu có)}, ...]
        """
        csv_path = self.resolve_csv_path(filename)
        records: list[dict[str, float]] = []

        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or "distance_cm" not in reader.fieldnames:
                raise ValueError(f"File '{csv_path.name}' khong co cot 'distance_cm'!")

            for row in reader:
                dist_str = (row.get("distance_cm") or "").strip()
                t_str = (row.get("t") or "").strip()
                temp_str = (row.get("temperature_c") or "").strip()
                if not dist_str:
                    continue
                item: dict[str, float] = {
                    "distance_cm": float(dist_str),
                    "t": float(t_str) if t_str else 0.0,
                }
                if temp_str:
                    item["temperature_c"] = float(temp_str)
                records.append(item)

        if not records:
            raise ValueError(f"File '{csv_path.name}' khong chua du lieu do hop le!")

        return records

    def load_distance_data(self, filename: str) -> list[float]:
        """Đọc cột `distance_cm` từ file CSV và trả về danh sách số thực (float)."""
        return [r["distance_cm"] for r in self.load_records(filename)]

    def analyze(self, filename: str) -> dict[str, float | int | str]:
        """
        Phân tích cột `distance_cm` của file CSV trong thư mục result/ và trả về
        dictionary chứa đầy đủ các chỉ số thống kê đo lường.
        """
        csv_path = self.resolve_csv_path(filename)
        data = self.load_distance_data(filename)
        n = len(data)

        total_sum = math.fsum(data)
        sum_squares = math.fsum(x * x for x in data)
        mean_val = total_sum / n
        median_val = statistics.median(data)
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val

        # Sai lệch tuyệt đối so với giá trị trung bình
        sum_abs_dev = math.fsum(abs(x - mean_val) for x in data)
        mean_abs_dev = sum_abs_dev / n

        # Tổng bình phương sai lệch: sum((x_i - mean)^2)
        sum_sq_dev = math.fsum((x - mean_val) ** 2 for x in data)

        # Phương sai & Độ lệch chuẩn tổng thể (chia cho n)
        variance_pop = sum_sq_dev / n
        std_pop = math.sqrt(variance_pop)

        # Phương sai & Độ lệch chuẩn mẫu (chia cho n - 1, chuẩn kỹ thuật đo lường)
        if n > 1:
            variance_sample = sum_sq_dev / (n - 1)
            std_sample = math.sqrt(variance_sample)
            std_error = std_sample / math.sqrt(n)
        else:
            variance_sample = 0.0
            std_sample = 0.0
            std_error = 0.0

        # Hệ số biến thiên CV (%)
        cv_percent = (std_sample / mean_val * 100.0) if mean_val != 0 else 0.0

        return {
            "file": csv_path.name,
            "n": n,
            "sum": total_sum,
            "sum_squares": sum_squares,
            "mean": mean_val,
            "median": median_val,
            "min": min_val,
            "max": max_val,
            "range": range_val,
            "sum_abs_dev": sum_abs_dev,
            "mean_abs_dev": mean_abs_dev,
            "sum_sq_dev": sum_sq_dev,
            "variance_sample": variance_sample,
            "variance_pop": variance_pop,
            "std_sample": std_sample,
            "std_pop": std_pop,
            "std_error": std_error,
            "cv_percent": cv_percent,
        }

    def print_report(self, filename: str) -> dict[str, float | int | str]:
        """Tính toán và in bảng báo cáo thống kê chi tiết ra màn hình."""
        stats = self.analyze(filename)
        print("\n" + "=" * 62)
        print(f"  BAO CAO PHAN TICH DU LIEU DO: result/{stats['file']}")
        print("=" * 62)
        print(f"  1. So lan do (n)                        : {stats['n']}")
        print(f"  2. Tong (Sum = Σx_i)                    : {stats['sum']:.6f} cm")
        print(f"  3. Tong binh phuong (Σx_i²)             : {stats['sum_squares']:.6f} cm²")
        print(f"  4. Trung binh cong (Mean = x̄)           : {stats['mean']:.6f} cm")
        print(f"  5. Trung vi (Median)                    : {stats['median']:.6f} cm")
        print(f"  6. Gia tri nho nhat (Min)               : {stats['min']:.6f} cm")
        print(f"  7. Gia tri lon nhat (Max)               : {stats['max']:.6f} cm")
        print(f"  8. Khoang bien thien (Range = Max-Min)  : {stats['range']:.6f} cm")
        print("-" * 62)
        print(f"  9. Tong sai lech tuyet doi (Σ|x_i - x̄|) : {stats['sum_abs_dev']:.6f} cm")
        print(f" 10. Sai lech tuyet doi TB (MAD)          : {stats['mean_abs_dev']:.6f} cm")
        print(f" 11. Tong binh phuong sai lech Σ(x_i-x̄)²  : {stats['sum_sq_dev']:.6f} cm²")
        print(f" 12. Phuong sai mau (s², chia n-1)        : {stats['variance_sample']:.6f} cm²")
        print(f" 13. Do lech chuan mau (s / Sample Std)   : {stats['std_sample']:.6f} cm")
        print(f" 14. Do lech chuan tong the (σ / Pop Std) : {stats['std_pop']:.6f} cm")
        print(f" 15. Sai so chuan cua TB (SE = s/√n)      : {stats['std_error']:.6f} cm")
        print(f" 16. He so bien thien (CV = s/x̄ * 100%)   : {stats['cv_percent']:.4f} %")
        print("=" * 62)
        return stats

    def plot_charts(
        self,
        filename: str,
        show: bool = True,
        save_png: bool = True,
    ) -> Path | None:
        """
        Vẽ cửa sổ 4 đồ thị phân tích kỹ thuật đo lường từ file CSV:
            1. Chuỗi giá trị đo theo thứ tự lần đo kèm đường Mean, Median và dải ±1s
            2. Biểu đồ tần suất (Histogram) & đường cong phân phối chuẩn Gauss
            3. Đồ thị sai số dư từng lần đo (v_i = x_i - x̄)
            4. Đồ thị quan hệ tuyến tính Khoảng cách d (cm) theo Thời gian truyền sóng t (us)
        """
        import matplotlib.pyplot as plt

        csv_path = self.resolve_csv_path(filename)
        records = self.load_records(filename)
        stats = self.analyze(filename)

        indices = list(range(1, len(records) + 1))
        distances = [r["distance_cm"] for r in records]
        times_us = [r["t"] for r in records]

        mean_val = float(stats["mean"])
        median_val = float(stats["median"])
        std_val = float(stats["std_sample"])
        residuals = [d - mean_val for d in distances]

        fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
        fig.suptitle(
            f"PHÂN TÍCH DỮ LIỆU ĐO KHOẢNG CÁCH RCWL-1601 ({csv_path.name} - n = {len(distances)})",
            fontsize=13,
            fontweight="bold",
        )

        # --- Đồ thị 1: Chuỗi phép đo x_i theo lần đo i ---
        ax1 = axes[0, 0]
        ax1.plot(indices, distances, marker="o", linestyle="-", color="#1f77b4", label="Giá trị đo $x_i$")
        ax1.axhline(mean_val, color="#d62728", linestyle="--", linewidth=1.5, label=f"Trung bình ($\\bar{{x}}$ = {mean_val:.3f} cm)")
        ax1.axhline(median_val, color="#2ca02c", linestyle=":", linewidth=1.5, label=f"Trung vị (Med = {median_val:.3f} cm)")
        if std_val > 0:
            ax1.fill_between(
                indices,
                mean_val - std_val,
                mean_val + std_val,
                color="#d62728",
                alpha=0.12,
                label=f"Dải $\\bar{{x}} \\pm s$ ($s$ = {std_val:.3f} cm)",
            )
        ax1.set_title("1. Chuỗi giá trị đo theo lần đo")
        ax1.set_xlabel("Lần đo thứ $i$")
        ax1.set_ylabel("Khoảng cách $d$ (cm)")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend(loc="best", fontsize=8.5)

        # --- Đồ thị 2: Histogram & Đường cong phân phối chuẩn Gauss ---
        ax2 = axes[0, 1]
        num_bins = max(5, min(15, int(math.sqrt(len(distances)) * 2)))
        counts, bin_edges, _ = ax2.hist(
            distances,
            bins=num_bins,
            color="#4c72b0",
            edgecolor="black",
            alpha=0.7,
            density=False,
            label="Tần số mẫu đo",
        )
        if std_val > 1e-9 and len(bin_edges) > 1:
            bin_width = bin_edges[1] - bin_edges[0]
            x_min_plot = min(distances) - 0.5 * std_val
            x_max_plot = max(distances) + 0.5 * std_val
            xs = [x_min_plot + k * (x_max_plot - x_min_plot) / 200.0 for k in range(201)]
            gauss_y = [
                (len(distances) * bin_width)
                * (1.0 / (std_val * math.sqrt(2.0 * math.pi)))
                * math.exp(-0.5 * ((x - mean_val) / std_val) ** 2)
                for x in xs
            ]
            ax2.plot(xs, gauss_y, color="#d62728", linewidth=2.0, label="Phân phối chuẩn Gauss")
        ax2.axvline(mean_val, color="#d62728", linestyle="--", linewidth=1.2)
        ax2.set_title("2. Phân bố tần suất & Đường cong Gauss")
        ax2.set_xlabel("Khoảng cách $d$ (cm)")
        ax2.set_ylabel("Số lần xuất hiện (Tần số)")
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend(loc="best", fontsize=8.5)

        # --- Đồ thị 3: Sai số dư từng lần đo v_i = x_i - x̄ ---
        ax3 = axes[1, 0]
        bar_colors = ["#ff7f0e" if r >= 0 else "#9467bd" for r in residuals]
        ax3.bar(indices, residuals, color=bar_colors, edgecolor="black", alpha=0.8, width=0.55)
        ax3.axhline(0.0, color="black", linewidth=1.2)
        if std_val > 0:
            ax3.axhline(std_val, color="#d62728", linestyle="--", linewidth=1.0, label=f"$+s$ (+{std_val:.3f} cm)")
            ax3.axhline(-std_val, color="#d62728", linestyle="--", linewidth=1.0, label=f"$-s$ (-{std_val:.3f} cm)")
            ax3.legend(loc="best", fontsize=8.5)
        ax3.set_title("3. Sai lệch ngẫu nhiên từng lần đo ($v_i = x_i - \\bar{x}$)")
        ax3.set_xlabel("Lần đo thứ $i$")
        ax3.set_ylabel("Độ lệch $v_i$ (cm)")
        ax3.grid(True, linestyle="--", alpha=0.5)

        # --- Đồ thị 4: Quan hệ Khoảng cách d (cm) theo Thời gian phản hồi t (us) ---
        ax4 = axes[1, 1]
        ax4.scatter(times_us, distances, color="#2ca02c", edgecolors="black", s=45, zorder=3, label="Điểm đo $(t_i, d_i)$")
        if len(times_us) >= 2 and max(times_us) > min(times_us):
            t_min, t_max = min(times_us), max(times_us)
            ratio = sum(d / t for t, d in zip(times_us, distances) if t > 0) / max(1, sum(1 for t in times_us if t > 0))
            ax4.plot(
                [t_min, t_max],
                [t_min * ratio, t_max * ratio],
                color="#1f77b4",
                linestyle="--",
                linewidth=1.5,
                label=f"Đặc tính $d = (v/2) \\cdot t$",
            )
        ax4.set_title("4. Quan hệ Khoảng cách $d$ theo Thời gian xung $t$")
        ax4.set_xlabel("Thời gian truyền sóng $t$ ($\\mu$s)")
        ax4.set_ylabel("Khoảng cách $d$ (cm)")
        ax4.grid(True, linestyle="--", alpha=0.5)
        ax4.legend(loc="best", fontsize=8.5)

        plt.tight_layout(rect=[0, 0.01, 1, 0.95])

        saved_path: Path | None = None
        if save_png:
            png_name = csv_path.stem + "_charts.png"
            saved_path = self.result_dir / png_name
            fig.savefig(saved_path, dpi=150)
            print(f"[+] Da luu hinh anh do thi tai: result/{png_name}")

        if show:
            plt.show()
        return saved_path


    @staticmethod
    def _student_t_95(df: int) -> float:
        """Tra cứu hệ số Student t_(0.975, df) ở độ tin cậy 95% (hai phía)."""
        t_table = {
            1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
            6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
            11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
            16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
            21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
            26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
        }
        if df in t_table:
            return t_table[df]
        if df <= 0:
            return 12.706
        # Xấp xỉ chính xác cho df > 30
        return 1.95996 + 2.372 / df + 2.82 / (df * df)

    def plot_optimal_sample_size(
        self,
        filename: str,
        target_err_cm: float = 0.15,
        show: bool = True,
        save_png: bool = True,
    ) -> Path | None:
        """
        Phân tích và vẽ biểu đồ 4 góc khảo sát số mẫu đo tối ưu N (Sample Size Convergence)
        từ tập dữ liệu lớn (ví dụ xppen100.csv):
            1. Phân bố chuỗi mẫu đo và nhận diện các điểm nhảy bậc (Outliers)
            2. Sự hội tụ của Trung bình tích lũy x̄(k) và Trung vị tích lũy Med(k) theo cỡ mẫu k
            3. Sự hội tụ của Độ lệch chuẩn mẫu s(k) theo cỡ mẫu k
            4. Đường cong Bán kính khoảng tin cậy 95% ε_95%(k) và xác định Điểm khuỷu tay (Optimal N)
        """
        import matplotlib.pyplot as plt

        csv_path = self.resolve_csv_path(filename)
        distances = self.load_distance_data(filename)
        total_n = len(distances)
        if total_n < 5:
            raise ValueError("Can it nhat 5 mau do de phan tich hoi tu co mau N!")

        indices = list(range(1, total_n + 1))
        overall_mean = math.fsum(distances) / total_n
        overall_med = statistics.median(distances)

        # Tính chuỗi tích lũy cho k = 2 .. total_n
        ks = list(range(2, total_n + 1))
        cum_means: list[float] = []
        cum_medians: list[float] = []
        cum_stds: list[float] = []
        cum_ci95s: list[float] = []

        for k in ks:
            sub = distances[:k]
            m_k = math.fsum(sub) / k
            med_k = statistics.median(sub)
            s_k = math.sqrt(math.fsum((x - m_k) ** 2 for x in sub) / (k - 1))
            t_val = self._student_t_95(k - 1)
            ci_k = t_val * s_k / math.sqrt(k)

            cum_means.append(m_k)
            cum_medians.append(med_k)
            cum_stds.append(s_k)
            cum_ci95s.append(ci_k)

        # Tìm N tối ưu tại ngưỡng sai số target_err_cm (mặc định 0.15 cm = 1.5 mm) và 0.10 cm (1.0 mm)
        opt_k_15 = next((ks[i] for i in range(len(ks)) if all(c <= target_err_cm for c in cum_ci95s[i:])), total_n)
        opt_k_10 = next((ks[i] for i in range(len(ks)) if all(c <= 0.10 for c in cum_ci95s[i:])), total_n)

        fig, axes = plt.subplots(2, 2, figsize=(13.5, 8.8))
        fig.suptitle(
            f"KHẢO SÁT SỐ LẦN ĐO TỐI ƯU N TỪ TẬP MẪU LỚN ({csv_path.name} - N = {total_n} mẫu)",
            fontsize=13,
            fontweight="bold",
        )

        # --- Đồ thị 1: Chuỗi dữ liệu & Phân loại cụm chính vs điểm nhảy bậc ---
        ax1 = axes[0, 0]
        inliers_x = [i for i, d in zip(indices, distances) if abs(d - overall_med) <= 0.25]
        inliers_y = [d for d in distances if abs(d - overall_med) <= 0.25]
        outliers_x = [i for i, d in zip(indices, distances) if abs(d - overall_med) > 0.25]
        outliers_y = [d for d in distances if abs(d - overall_med) > 0.25]

        ax1.plot(indices, distances, color="#b0c4de", linestyle="-", linewidth=1.0, zorder=1)
        ax1.scatter(inliers_x, inliers_y, color="#1f77b4", s=28, zorder=3, label=f"Mẫu ổn định tại ~{overall_med:.3f} cm ({len(inliers_y)}/{total_n} mẫu)")
        if outliers_x:
            ax1.scatter(outliers_x, outliers_y, color="#d62728", marker="x", s=50, zorder=4, label=f"Điểm nhảy bậc ±1 cm ({len(outliers_y)}/{total_n} mẫu)")
        ax1.axhline(overall_med, color="#2ca02c", linestyle="--", linewidth=1.4, label=f"Trung vị chuẩn ({overall_med:.3f} cm)")
        ax1.axhline(overall_mean, color="#ff7f0e", linestyle=":", linewidth=1.4, label=f"Trung bình 100 mẫu ({overall_mean:.3f} cm)")
        ax1.set_title("1. Phân bố 100 mẫu đo & Điểm nhảy bậc (Outliers)")
        ax1.set_xlabel("Thứ tự mẫu đo $i$")
        ax1.set_ylabel("Khoảng cách $d$ (cm)")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend(loc="best", fontsize=8)

        # --- Đồ thị 2: Sự hội tụ của Trung bình tích lũy x̄(k) và Trung vị tích lũy Med(k) ---
        ax2 = axes[0, 1]
        ax2.plot(ks, cum_means, color="#1f77b4", linewidth=2.0, label="Trung bình tích lũy $\\bar{x}(k)$")
        ax2.plot(ks, cum_medians, color="#2ca02c", linewidth=2.0, linestyle="--", label="Trung vị tích lũy $\\mathrm{Med}(k)$")
        ax2.axhline(overall_mean, color="#d62728", linestyle=":", linewidth=1.2, label=f"Giá trị tiệm cận $\\bar{{x}}_{{100}}$ = {overall_mean:.3f} cm")
        ax2.fill_between(
            ks,
            overall_mean - 0.10,
            overall_mean + 0.10,
            color="#2ca02c",
            alpha=0.12,
            label="Dải hội tụ ổn định $\\pm 0.10$ cm ($\\pm 1$ mm)",
        )
        ax2.axvline(opt_k_15, color="#ff7f0e", linestyle="--", linewidth=1.2, label=f"Mốc hội tụ $N \\approx {opt_k_15}$ mẫu")
        ax2.set_title("2. Sự hội tụ của Trung bình $\\bar{x}(k)$ & Trung vị theo số mẫu $k$")
        ax2.set_xlabel("Số lượng mẫu lấy tính toán $k$")
        ax2.set_ylabel("Khoảng cách (cm)")
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend(loc="best", fontsize=8)

        # --- Đồ thị 3: Sự hội tụ của Độ lệch chuẩn mẫu s(k) theo k ---
        ax3 = axes[1, 0]
        ax3.plot(ks, cum_stds, color="#9467bd", linewidth=2.0, label="Độ lệch chuẩn tích lũy $s(k)$")
        ax3.axhline(cum_stds[-1], color="black", linestyle="--", linewidth=1.2, label=f"$s_{{100}}$ = {cum_stds[-1]:.3f} cm")
        ax3.axvline(opt_k_15, color="#ff7f0e", linestyle="--", linewidth=1.2, label=f"Ổn định từ $N \\approx {opt_k_15}$")
        ax3.set_title("3. Sự ổn định của Độ lệch chuẩn mẫu $s(k)$ theo số mẫu $k$")
        ax3.set_xlabel("Số lượng mẫu $k$")
        ax3.set_ylabel("Độ lệch chuẩn $s(k)$ (cm)")
        ax3.grid(True, linestyle="--", alpha=0.5)
        ax3.legend(loc="best", fontsize=8)

        # --- Đồ thị 4: Bán kính khoảng tin cậy 95% ε(k) & Điểm khuỷu tay (Elbow Point) ---
        ax4 = axes[1, 1]
        ax4.plot(ks, cum_ci95s, color="#d62728", linewidth=2.2, label="Sai số khoảng tin cậy 95%: $\\varepsilon_{95\\%}(k) = t \\cdot s(k)/\\sqrt{k}$")
        ax4.axhline(target_err_cm, color="#ff7f0e", linestyle="--", linewidth=1.4, label=f"Ngưỡng $\\Delta = {target_err_cm:.2f}$ cm (đạt tại $N = {opt_k_15}$)")
        ax4.axhline(0.10, color="#2ca02c", linestyle=":", linewidth=1.4, label=f"Ngưỡng $\\Delta = 0.10$ cm / 1 mm (đạt tại $N = {opt_k_10}$)")
        if opt_k_15 in ks:
            idx_15 = ks.index(opt_k_15)
            ax4.scatter([opt_k_15], [cum_ci95s[idx_15]], color="#ff7f0e", edgecolors="black", s=75, zorder=5)
            ax4.annotate(
                f"Điểm khuỷu tay\nN = {opt_k_15} (±{cum_ci95s[idx_15]:.3f} cm)",
                xy=(opt_k_15, cum_ci95s[idx_15]),
                xytext=(min(total_n - 25, opt_k_15 + 8), cum_ci95s[idx_15] + 0.18),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
                fontsize=8.5,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc="#fff8dc", ec="#ff7f0e"),
            )
        ax4.set_ylim(0, min(1.5, max(cum_ci95s) * 1.05))
        ax4.set_title("4. Độ không đảm bảo đo $\\varepsilon_{95\\%}(k)$ & Chọn số mẫu tối ưu $N$")
        ax4.set_xlabel("Số lượng mẫu đo $k$")
        ax4.set_ylabel("Bán kính khoảng tin cậy $\\varepsilon_{95\\%}$ (cm)")
        ax4.grid(True, linestyle="--", alpha=0.5)
        ax4.legend(loc="upper right", fontsize=8)

        plt.tight_layout(rect=[0, 0.01, 1, 0.95])

        saved_path: Path | None = None
        if save_png:
            png_name = csv_path.stem + "_optimal_n.png"
            saved_path = self.result_dir / png_name
            fig.savefig(saved_path, dpi=150)
            print(f"[+] Da luu bieu do khao sat co mau N tai: result/{png_name}")

        if show:
            plt.show()

        return saved_path


def analyze_distance_file(
    filename: str,
    plot: bool = True,
    show_plot: bool = True,
) -> dict[str, float | int | str]:
    """
    Hàm tiện ích nhận vào tên file trong thư mục result/,
    in báo cáo thống kê cột distance_cm, vẽ cả 2 bảng đồ thị và trả về dictionary kết quả.
    """
    import matplotlib.pyplot as plt

    analyzer = DistanceDataAnalyzer()
    stats = analyzer.print_report(filename)
    if plot:
        analyzer.plot_charts(filename, show=False, save_png=True)
        if int(stats["n"]) >= 5:
            analyzer.plot_optimal_sample_size(filename, show=False, save_png=True)
        if show_plot:
            plt.show()
        else:
            plt.close("all")
    return stats


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--no-show"]
    show_window = "--no-show" not in sys.argv[1:]

    if args:
        for arg_name in args:
            try:
                analyze_distance_file(arg_name, plot=True, show_plot=show_window)
            except Exception as exc:
                print(f"[!] Loi: {exc}")
    else:
        print("============================================================")
        print("  CHUONG TRINH PHAN TICH & VE DO THI DU LIEU DO (result/)   ")
        print("============================================================")
        while True:
            try:
                fname = input("\n>> Nhap ten file trong thu muc result (hoac 'q' de thoat): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[*] Da thoat.")
                break
            if not fname:
                continue
            if fname.lower() in ("q", "exit", "quit"):
                print("[*] Da thoat.")
                break
            try:
                analyze_distance_file(fname, plot=True, show_plot=True)
            except Exception as exc:
                print(f"[!] {exc}")
