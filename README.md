# PKHeX Gen7 Expansion Mobile — Android

Dự án cộng đồng (không chính thức): chuyển chức năng PKHeX.Mobile sang .NET MAUI và dùng **Aqua-0/PKHeX v1.0 PKHeX.Core** để hỗ trợ save Pokémon Ultra Sun/Ultra Moon Expansion.

**Trạng thái:** prototype 0.1.0. Mã nguồn và APK **chưa được chứng nhận hoạt động**; GitHub Actions phải build thành công trước khi APK xuất hiện. Không dùng với save gốc nếu chưa sao lưu.

## Cách tải APK

Mở tab **Actions** > **Build Android Debug APK** > chọn một run thành công > **Artifacts** > tải `pkhex-gen7-expansion-debug-apk`. Giải nén artifact để lấy `.apk`, cài trên Android.

## Mã nguồn

Bản nguồn được đưa vào tệp `source-bundle.txz`; GitHub Actions giải nén gói này, tải Aqua-0 v1.0 và thử biên dịch. Sau khi build chạy, workflow cũng cố gắng đưa các file mã nguồn đã giải nén vào repository để tiện tham khảo và chỉnh sửa.

- Giao diện tham khảo: https://github.com/kwsch/PKHeX.Mobile
- Engine mở rộng: https://github.com/Aqua-0/PKHeX/releases/tag/v1.0
- GPLv3: giấy phép gốc được sao chép từ Aqua-0 khi setup.

**Giới hạn prototype:** chưa tương đương toàn bộ PKHeX.Mobile gốc; sprite, Inventory, Mystery Gift, QR và vài module khác chưa được chuyển. Chưa kiểm thử trên save thật.

Khi build thất bại, xem logs tại Actions và sửa nguyên nhân thay vì cài file chưa kiểm chứng.
