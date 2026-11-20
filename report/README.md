# Báo cáo giai đoạn 1 — Nhóm 01 (HR-04)

GMR: ánh xạ chuyển động người sang robot hình người theo thời gian thực.

Báo cáo 10–15 trang theo đúng 8 mục của `docs/huong_dan/08b. Huong dan bao cao giai doan 1 - 15DHTH07 - HK1 2026-2027.pdf`:
1. Giới thiệu bài toán + tóm tắt bài báo
2. Tuyên bố cần kiểm chứng (số hiệu Bảng/Hình + con số gốc)
3. Nhật ký cài đặt
4. Kết quả chạy mô hình có sẵn, đối chiếu bài báo
5. Kết quả tự huấn luyện (3 hạt giống, đường cong, thời gian)
6. Sim2sim: bảng tụt hiệu năng + đồ thị
7. Kết luận dứt khoát
8. Phân công + tự thuật từng thành viên

## Xuất PDF

```
python report/make_report.py
```

Script đọc `report/bao_cao.md`, dựng DOCX tạm (A4, Times New Roman, số trang) rồi gọi LibreOffice Writer xuất `report/bao_cao.pdf`. Cần `markdown`, `beautifulsoup4`, `python-docx`, `pillow`, `pypdf`; đặt biến `SOFFICE_BIN` nếu LibreOffice không ở đường dẫn mặc định. Mục lục nằm trong `bao_cao.md` — nếu sửa nội dung làm các mục đổi trang, cập nhật cột **Trang** rồi chạy lại script.
