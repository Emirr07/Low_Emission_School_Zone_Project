# Kepez Karbon Emisyonu ve Akıllı Kentsel Ulaştırma Simülasyonu

Bu proje, okul çevrelerinde çocukların hava kalitesini korumak amacıyla geliştirilmiş dinamik bir **WebGIS ve Sürdürülebilir Ulaştırma Yönetim Paneli** prototipidir. Belirli okul giriş/çıkış saatlerinde okul çevrelerinin ulaşıma kapatılmasını ve bu senaryonun şehir içi CO₂ emisyon şebekesine olan 15 dakikalık anlık etkilerini interaktif olarak simüle eder.

## 🛠️ Kullanılan Teknolojiler
- **Mekânsal Veri Tabanı:** PostgreSQL / PostGIS
- **Backend API:** Python / FastAPI / Uvicorn
- **Frontend (Arayüz):** JavaScript / Leaflet.js / CSS3 (Glassmorphism)

## 🚀 Kurulum ve Çalıştırma

### 1. Veri Tabanı Hazırlığı
PostgreSQL veri tabanınızda projenin SQL sorgularını çalıştırarak `kepez_yol_trafigi`, `okul_buffer_200m` ve `okul_yollari_kesisen` tablolarını hazır hale getirin.

### 2. Backend API Sunucusunu Başlatma
Proje klasöründe terminali açarak gerekli bağımlılıkları yükleyin ve sunucuyu ayağa kaldırın:

```bash
# Bağımlılıkları yükleyin
pip install -r requirements.txt

# API sunucusunu çalıştırın
python main.py