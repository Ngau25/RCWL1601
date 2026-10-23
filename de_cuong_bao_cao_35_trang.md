# ĐỀ CƯƠNG CHI TIẾT BÁO CÁO THỰC NGHIỆM (QUY MÔ 30 – 35 TRANG)
**Học phần:** Kỹ thuật Đo lường và Cảm biến (`EMA2024E_3`)  
**Đề tài:** Thiết kế hệ thống thu thập dữ liệu và khảo sát thực nghiệm các đặc tính đo lường của cảm biến khoảng cách siêu âm RCWL-1601 kết hợp bù nhiệt độ DHT11 trên vi điều khiển ESP32

---

## Tổng quan phân bổ dung lượng (32 – 35 trang chuẩn A4)

| Phần / Chương | Nội dung trọng tâm | Số trang dự kiến |
| :--- | :--- | :---: |
| **Mở đầu & Danh mục** | Trang bìa, Mục lục, Danh mục bảng biểu, Danh mục hình vẽ, Ký hiệu viết tắt (`FSDT`, `FRDT`, `BSDT`...) | **3 trang** |
| **Chương 1** | Cơ sở lý thuyết về đo lường sóng siêu âm, cảm biến RCWL-1601, DHT11 và lý thuyết xử lý số liệu thực nghiệm | **5 – 6 trang** |
| **Chương 2** | Thiết kế hệ thống đo phần cứng, kiến trúc phần mềm OOP (MicroPython & PC) và quy trình thực nghiệm | **4 – 5 trang** |
| **Chương 3** | Cơ sở thống kê lựa chọn cỡ mẫu tối ưu $N = 50$ từ tập dữ liệu khảo sát 100 mẫu (`100lan...`) | **4 – 5 trang** |
| **Chương 4** | **Khảo sát toàn diện các Đặc tính tĩnh của cảm biến ở điều kiện chuẩn (`FSDT` & `BSDT`):** Dải đo & Vùng chết, Lọc sai số thô ($3\sigma$ & $\text{IQR}$), Độ chụm (Precision), Độ chính xác (Accuracy), Độ tuyến tính (Linearity), Độ nhạy (Sensitivity), Độ phân giải (Resolution), Độ trễ (Hysteresis) và Độ không đảm bảo đo (Loại A, Loại B, Tổng hợp $u_c$, Mở rộng $U_{95\%}$) | **10 – 11 trang** |
| **Chương 5** | **Khảo sát các yếu tố gây nhiễu ngoại cảnh:** Ảnh hưởng của Bề mặt phản xạ (`FRDT` vs. `FSDT`) và Ảnh hưởng của Nhiệt độ môi trường (Phòng thường vs. Phòng điều hòa) | **5 – 6 trang** |
| **Chương 6** | Tổng kết bảng thông số thực nghiệm so với Datasheet & Kết luận | **2 trang** |
| **Tổng cộng** | **Toàn văn báo cáo** | **33 – 35 trang** |

---

## Chi tiết triển khai từng Chương (Công thức, Bảng biểu & Đồ thị cần đưa vào)

### PHẦN MỞ ĐẦU (3 trang)
1. **Trang bìa & Lời nói đầu (1 trang):** Đặt vấn đề về nhu cầu đo khoảng cách không tiếp xúc trong công nghiệp/robot và bài toán đánh giá độ tin cậy của cảm biến siêu âm RCWL-1601.
2. **Mục lục, Danh mục Hình vẽ, Danh mục Bảng biểu (1.5 trang).**
3. **Bảng quy ước mã hóa tập dữ liệu thực nghiệm (0.5 trang):**
   - `100lanforward_smooth_defttemp_XXXcm`: Đo thăm dò $100$ lần ở $50\text{ cm}, 100\text{ cm}, 150\text{ cm}$.
   - `FSDT` (*Forward – Smooth – Default Temp*): Chiều tiến, bề mặt phẳng nhẵn, nhiệt độ phòng.
   - `BSDT` (*Backward – Smooth – Default Temp*): Chiều lùi, bề mặt phẳng nhẵn, nhiệt độ phòng.
   - `FRDT` (*Forward – Rough – Default Temp*): Chiều tiến, bề mặt gồ ghề, nhiệt độ phòng.
   - `FSAT` / `FSLT` (*Forward – Smooth – Air-con/Low Temp*): Chiều tiến, bề mặt nhẵn, nhiệt độ phòng bật điều hòa.

---

### CHƯƠNG 1: CƠ SỞ LÝ THUYẾT ĐO LƯỜNG VÀ CẢM BIẾN SIÊU ÂM (5 – 6 trang)
- **1.1. Nguyên lý đo khoảng cách bằng thời gian bay (Time-of-Flight – ToF) của sóng siêu âm 40 kHz (1.5 trang):**
  - Phương trình cơ bản:

$$d = \frac{v \cdot t}{2}$$

  - Cơ chế truyền sóng âm trong môi trường khí, hiện tượng suy hao biên độ theo khoảng cách ($I \propto 1/d^2$ và hấp thụ môi trường), góc mở chùm tia (Beam Pattern $\pm 15^\circ$).
- **1.2. Sự phụ thuộc của vận tốc âm thanh vào nhiệt độ và nguyên lý bù nhiệt (1 trang):**
  - Công thức Laplace cho vận tốc truyền âm trong không khí (đơn vị $\text{m/s}$):

$$v(T) = 331.3 \sqrt{1 + \frac{T}{273.15}} \approx 331.3 + 0.606 \cdot T$$

  - Phân tích độ nhạy nhiệt độ lý thuyết: mỗi $1^\circ\text{C}$ thay đổi làm vận tốc âm thay đổi $\approx 0.6\text{ m/s}$ ($\approx 0.18\%$).
- **1.3. Cấu tạo phần cứng cảm biến RCWL-1601 và cảm biến nhiệt ẩm DHT11 (1 trang):**
  - Sơ đồ khối IC thu phát siêu âm **RCWL-9610** (dải áp rộng $3.0 - 5.5\text{ V}$), giản đồ xung `TRIG` ($10\text{ }\mu\text{s}$) và `ECHO`.
  - Nguyên lý giao tiếp 1-Wire của DHT11.
- **1.4. Hệ thống các chỉ tiêu kỹ thuật đánh giá cảm biến và Lý thuyết sai số (2 trang):**
  - Phân loại sai số: Sai số hệ thống (Systematic Error), Sai số ngẫu nhiên (Random Error) và Sai số thô (Gross Error / Outliers).
  - Các chỉ số thống kê và đặc tính tĩnh chuẩn:
    - Giá trị trung bình mẫu $\bar{x}$, Trung vị $\text{Med}$, Khoảng tứ phân vị $\text{IQR} = Q_3 - Q_1$, Phương sai mẫu $s^2$, Độ lệch chuẩn mẫu $s$.
    - **Chỉ số bổ sung 1 – Tiêu chuẩn lọc sai số thô ($3\sigma$ & $\text{IQR}$):** Phát hiện và loại bỏ các điểm nhảy bậc chu kỳ sóng âm.
    - Độ chụm (Precision - $s$, $\text{CV}\%$), Độ chính xác (Accuracy - $\Delta x$, $\delta\%$).
    - Phương pháp bình phương tối thiểu (Least Squares) tìm đường đặc tính tuyến tính $\hat{y} = ax + b$, Độ nhạy $S$, Hệ số xác định $R^2$, Sai số phi tuyến $\delta_{\text{NL}}\%$, Độ trễ (Hysteresis $\Delta H_{\max}$, $\gamma_H\%$).
    - **Chỉ số bổ sung 2 – Độ phân giải (Resolution):** Độ phân giải lượng tử phần cứng ($\Delta d_{\text{quant}}$) và Độ phân giải thực tế hữu ích ($\Delta d_{\text{eff}}$).
    - **Chỉ số bổ sung 3 – Độ không đảm bảo đo theo chuẩn ISO/GUM:** Độ không đảm bảo đo Loại A ($u_A$), Loại B ($u_B$), Tổng hợp ($u_c$) và Mở rộng ($U_{95\%}$).

---

### CHƯƠNG 2: THIẾT KẾ HỆ THỐNG ĐO VÀ QUY TRÌNH THỰC NGHIỆM (4 – 5 trang)
- **2.1. Thiết kế phần cứng và sơ đồ đấu nối trên ESP32 Expansion Board 30-Pin (1.5 trang):**
  - Sơ đồ nối dây chi tiết (`GPIO 5` - `TRIG`, `GPIO 18` - `ECHO`, `GPIO 4` - `DHT11`, nguồn `3.3V`), ảnh chụp mạch thực tế và bố trí bàn đo có thước chuẩn.
- **2.2. Thiết kế kiến trúc phần mềm hướng đối tượng (OOP) (2 trang):**
  - Sơ đồ lớp UML (Class Diagram) cho 3 lớp: `RCWL1601`, `DHT11Sensor`, `DistanceMonitorApp` trên ESP32 và `ESP32TerminalRunner` trên máy tính.
  - Lưu đồ thuật toán (Flowchart) đo xung `time_pulse_us`, lọc trung vị 3 mẫu liên tiếp và truyền chuỗi `CSV_DATA` qua UART về máy tính.
- **2.3. Thiết kế ma trận kịch bản thực nghiệm (1 trang):**
  - Bảng mô tả điều kiện đo cho từng bộ dữ liệu (`100lan`, `FSDT`, `BSDT`, `FRDT`, và bộ dữ liệu điều hòa).

---

### CHƯƠNG 3: PHÂN TÍCH LỰA CHỌN SỐ LẦN ĐO TỐI ƯU N = 50 TỪ TẬP MẪU LỚN (4 – 5 trang)
*(Sử dụng trực tiếp 3 file trong `du_lieu_tho/`: `100lanforward_smooth_defttemp_050cm.csv`, `100lanforward_smooth_defttemp_100cm.csv`, `100lanforward_smooth_defttemp_150cm.csv`)*

- **3.1. Bài toán tối ưu hóa giữa Độ tin cậy thống kê và Thời gian thực nghiệm (0.5 trang).**
- **3.2. Phân tích sự hội tụ của Trung bình tích lũy và Độ lệch chuẩn theo k = 2 .. 100 (1.5 trang):**
  - Bảng trích xuất giá trị $\bar{x}(k)$, $s(k)$, $\varepsilon_{95\%}(k)$ tại các mốc $k = 5, 10, 20, 30, 40, 50, 75, 100$ cho cả 3 cự ly $50, 100, 150\text{ cm}$.
- **3.3. Biểu đồ hội tụ cỡ mẫu và Luận giải việc chốt N = 50 mẫu/mốc (2.5 trang):**
  - Chèn 3 biểu đồ 4 góc (`_optimal_n.png`) của $50\text{ cm}, 100\text{ cm}, 150\text{ cm}$ + 1 biểu đồ gộp so sánh đường cong $\varepsilon_{95\%}(k)$ của cả 3 mốc trên cùng 1 hệ trục.
  - Luận giải vì sao $N = 50$ vượt qua hoàn toàn điểm khuỷu tay ($k \approx 30 - 35$) ở cả 3 cự ly và tiết kiệm 50% thời gian thực nghiệm.

---

### CHƯƠNG 4: ĐÁNH GIÁ TOÀN DIỆN CÁC ĐẶC TÍNH TĨNH CỦA CẢM BIẾN Ở ĐIỀU KIỆN CHUẨN (`FSDT` & `BSDT`) (10 – 11 trang)
*(Chương này gom toàn bộ các đặc tính nội tại của cảm biến trong điều kiện chuẩn, sử dụng `du_lieu_tong_hop/FSDT.csv` và `du_lieu_tong_hop/BSDT.csv`)*

- **4.1. Bảng tổng hợp thống kê toàn dải & Phân tích Lọc sai số thô ($3\sigma$ & $\text{IQR}$) (1.5 trang):**
  - Bảng tổng hợp các mốc khoảng cách ($1\text{ cm} \to 600\text{ cm}$) trước và sau khi áp dụng bộ lọc sai số thô $3\sigma$ / $\text{IQR}$. Đánh giá tỷ lệ xuất hiện điểm dị biệt ở từng vùng khoảng cách.
- **4.2. Khảo sát Vùng chết (Blind Zone: 1 cm – 3 cm) và Giới hạn đo xa (400 cm – 600 cm) (1.5 trang):**
  - Phân tích dữ liệu tại `001cm`, `002cm`, `003cm`, `005cm` (hiện tượng xuyên âm trực tiếp và phản xạ nhiều lần) và tại `420cm` $\to$ `600cm` (suy hao sóng âm, bão hòa xung). Xác định **Dải đo hiệu dụng (Effective Span)**.
- **4.3. Đánh giá Độ chụm / Độ lặp lại (Precision & Repeatability) (1.5 trang):**
  - Phân tích Độ lệch chuẩn mẫu $s$, Hệ số biến thiên $\text{CV}\%$ và Khoảng tứ phân vị $\text{IQR}$ theo cự ly.
- **4.4. Đánh giá Độ chính xác (Accuracy) – Sai số tuyệt đối & Sai số tương đối (1.5 trang):**
  - Phân tích sai số tuyệt đối $\Delta d = \bar{d} - d_{\text{true}}$ và sai số tương đối $\delta\% = \frac{|\Delta d|}{d_{\text{true}}} \times 100\%$ trên toàn dải đo.
- **4.5. Đánh giá Độ tuyến tính (Linearity), Độ nhạy (Sensitivity) và Độ phân giải (Resolution) (2 trang):**
  - Phương trình hồi quy tuyến tính $\bar{d} = a \cdot d_{\text{true}} + b$ và $\bar{t} = S_t \cdot d_{\text{true}} + t_0$; tính độ nhạy thực nghiệm $S_t\text{ }(\mu\text{s/cm})$, hệ số $R^2$ và sai số phi tuyến cực đại $\delta_{\text{NL}}\%$.
  - Phân tích **Độ phân giải (Resolution):** So sánh Độ phân giải lượng tử lý thuyết ($\Delta d_{\min} = \frac{v \cdot 1\text{ }\mu\text{s}}{2} \approx 0.0175\text{ cm}$) với Độ phân giải thực tế hữu ích.
- **4.6. Khảo sát Độ trễ (Hysteresis) giữa Chiều tiến (`FSDT`) và Chiều lùi (`BSDT`) (1.5 trang):**
  - Phân tích trên các mốc chung (`010cm` $\to$ `300cm`): Tính độ lệch trễ từng mốc $\Delta H_k = |\bar{d}_{\text{forward}} - \bar{d}_{\text{backward}}|$, độ trễ cực đại $\Delta H_{\max}$, sai số độ trễ toàn thang $\gamma_H\%$ và vẽ Đồ thị Vòng trễ (Hysteresis Loop).
- **4.7. Đánh giá Độ không đảm bảo đo (Measurement Uncertainty theo chuẩn ISO/GUM) (1.5 trang):**
  - Tính **Độ không đảm bảo đo Loại A** ($u_A = s/\sqrt{N}$ từ $N = 50$ lần đo).
  - Tính **Độ không đảm bảo đo Loại B** ($u_B$ tổng hợp từ sai số thước chuẩn $\pm 1\text{ mm}$, độ phân giải bộ đếm $1\text{ }\mu\text{s}$ của ESP32 và sai số $\pm 2^\circ\text{C}$ của DHT11).
  - Tính **Độ không đảm bảo đo tổng hợp** $u_c = \sqrt{u_A^2 + u_B^2}$ và **Độ không đảm bảo đo mở rộng** $U_{95\%} = 2 \cdot u_c$.

---

### CHƯƠNG 5: KHẢO SÁT CÁC YẾU TỐ GÂY NHIỄU NGOẠI CẢNH (BỀ MẶT PHẢN XẠ & NHIỆT ĐỘ MÔI TRƯỜNG) (5 – 6 trang)
*(Chương này tách riêng các yếu tố môi trường/đối tượng bên ngoài tác động làm thay đổi đặc tính chuẩn của Chương 4)*

- **5.1. Ảnh hưởng của Bề mặt phản xạ (Reflective Surface): Bề mặt nhẵn (`FSDT`) vs. Bề mặt gồ ghề (`FRDT`) (3 trang):**
  - Đối chiếu trực tiếp trên các mốc từ `010cm` đến `375cm`.
  - Phân tích hiện tượng tán xạ sóng âm (Acoustic Scattering) trên bề mặt gồ ghề làm suy giảm cả **Precision** (tăng $s$, tăng số điểm nhảy bậc), suy giảm **Accuracy** (trễ sườn xung làm $\bar{d}_{\text{rough}} > \bar{d}_{\text{smooth}}$) và thu hẹp **Dải đo tối đa** (chỉ đạt $375\text{ cm}$ so với $600\text{ cm}$).
  - Đồ thị so sánh Boxplot, Error Bar và Độ lệch chuẩn giữa `Smooth` và `Rough`.
- **5.2. Ảnh hưởng của Nhiệt độ môi trường (Phòng thường vs. Phòng điều hòa) & Đánh giá hiệu quả bù nhiệt DHT11 (2.5 trang):**
  - So sánh thời gian truyền sóng thực tế $\bar{t}\text{ }(\mu\text{s})$ tại cùng cự ly ở 2 mức nhiệt độ.
  - Tính toán sai số trôi nhiệt (Thermal Drift) nếu không có DHT11 và chứng minh hiệu quả ổn định kết quả đo khi có thuật toán bù nhiệt từ DHT11.

---

### CHƯƠNG 6: TỔNG KẾT ĐẶC TÍNH KỸ THUẬT & KẾT LUẬN (2 trang)
- **6.1. Bảng tổng hợp Hồ sơ kỹ thuật thực nghiệm (Experimental Datasheet) của RCWL-1601 đối chiếu với Nhà sản xuất.**
- **6.2. Kết luận vùng làm việc tối ưu & Khuyến nghị giải pháp xử lý tín hiệu.**
- **Tài liệu tham khảo & Phụ lục Code chương trình.**
