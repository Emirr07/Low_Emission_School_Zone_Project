# Kepez İlçesi Akıllı Ulaştırma ve Dinamik Düşük Emisyon Okul Bölgeleri (LEZ) WebGIS Simülasyonu

Bu proje; kentsel ulaştırma planlaması, sürdürülebilirlik ve halk sağlığı odaklı bir **Mekânsal Karar Destek Sistemi (MKDS)** prototipidir. Projenin temel amacı, okul giriş ve çıkış saatlerinde hassas nüfusun (öğrencilerin) maruz kaldığı CO₂ emisyonunu sıfıra indirmek amacıyla okul çevrelerindeki yolların dinamik olarak ulaşıma kapatılmasını ve bu kapatma eyleminin çevre şebekelerdeki emisyon dağılımına olan anlık (15 dakikalık periyotlar) etkilerini CBS tabanlı simüle etmektir.

---

## 🧐 Projenin Amacı ve Metodoloji
Geleneksel Düşük Emisyon Bölgeleri (Low Emission Zones - LEZ) genellikle statik ve geniş kentsel alanları kapsar. Bu projede ise **"Dinamik ve Zamana Bağlı LEZ"** konsepti geliştirilmiştir. 
- Okul binaları odak alınarak **200 metrelik yaya erişim tampon bölgeleri (Pedestrian Buffer Zones)** analizi yapılmıştır.
- Eğitim-öğretim saatlerine bağlı olarak **08:00 - 08:59** ve **16:00 - 16:59** zaman dilimlerinde, tampon bölgeyle kesişen okul yolları araç trafiğine tamamen kapatılarak **"Güvenli/Sıfır Emisyon Koridoru"** haline getirilmektedir.
- Kapatılan yolların çevredeki diğer arterlerde oluşturduğu anlık trafik yükü ve emisyon dalgalanması, matematiksel bir modelle **15 dakikalık çeyrek saat periyotlarına (günde 96 farklı adım)** bölünerek veri tabanı seviyesinde simüle edilmiştir.

---

## 🛠️ Kullanılan Teknolojiler ve Sistem Mimarisi

Proje, modern bir Üç Katmanlı (3-Tier) WebGIS mimarisi üzerine inşa edilmiştir:

1. **Veri Katmanı (Mekânsal Veri Tabanı):** PostgreSQL 16 & PostGIS uzantısı. Tüm coğrafi analizler, geometrik kesişimler ve zaman serisi simülasyon tabloları veri tabanı tarafında indeksli olarak tutulmaktadır.
2. **Sunucu Katmanı (Backend API):** Python 3 / FastAPI. Veri tabanındaki GeoJSON geometrilerini ve zamana bağlı emisyon skorlarını asenkron ve yüksek performanslı olarak frontend katmanına besler. Sunucu yönetiminde Uvicorn asenkron sunucu ağ geçidi kullanılmıştır.
3. **Sunum Katmanı (Frontend/Arayüz):** HTML5, CSS3 (Modern Glassmorphic UI Tasarımı) ve Leaflet.js open-source harita kütüphanesi. Kullanıcı etkileşimli slider mimarisiyle 15 dakikalık veri akışı anlık olarak asenkron (AJAX/Fetch API) yöntemlerle haritada render edilir.

---

## 📊 Veri Kaynakları ve Mekânsal Analiz Süreçleri

Projedeki coğrafi altlıklar ve öznitelik verileri şu kaynaklardan temin edilerek PostGIS içerisine aktarılmıştır:

- **Yol Ağı Grafı (`kepez_yollari`):** OpenStreetMap (OSM) Overpass API aracılığıyla Antalya Kepez bölgesindeki tüm birincil, ikincil ve konutsal yollar (LineString) topolojik olarak çekilmiş, `EPSG:4326` (WGS 84) coğrafi koordinat sisteminden Türkiye için uygun projeksiyon sistemi olan `EPSG:5254` (TUREF / TM30) sistemine dönüştürülmüştür.
- **Okul Konumları ve Bina Geometrileri (`kepez_okullari`):** MEB veri kaynakları ve OSM bina verileri entegre edilerek bölgedeki okul poligonları sisteme dahil edilmiştir.
- **Tampon Bölge Analizi (`okul_buffer_200m`):** PostGIS üzerinde `ST_Buffer(ST_Transform(geom, 5254), 200)` fonksiyonu çalıştırılarak okulların etrafında 200 metrelik hassas koruma alanları üretilmiştir.
- **Mekânsal Kesişim Analizi (`okul_yollari_kesisen`):** `ST_Intersects` ve `ST_Within` fonksiyonları kullanılarak okul tampon bölgelerinin içinde kalan veya bu bölgeleri kesen yol segmentleri otomatik olarak tespit edilmiş ve ulaşıma kapatılacak aday yollar olarak indekslenmiştir.

---

## 🧮 15 Dakikalık Trafik ve Emisyon Simülasyon Modeli

Sistemde her yol segmenti için günde 96 farklı zaman dilimi ($24 \text{ saat} \times 4 \text{ çeyrek saat}$) üretilmiştir. Yapay emisyon skorunun (`yogunluk_skoru`) hesaplanmasında kullanılan matematiksel model şu bileşenlerden oluşur:

$$\text{Emisyon Skoru} = \text{Taban Emisyon} + \text{Şehir Trafik Eğrisi} + \text{Okul Etki Katsayısı} + \text{Dinamik Periyot Dalgalanması} + \text{Doğal Gürültü}$$

- **Taban Emisyon ($0.10$):** Şehirdeki minimum karbon salınım seviyesi.
- **Şehir Trafik Eğrisi ($0.0 - 0.60$):** Sabah ($08:00 - 09:59$) ve Akşam ($17:00 - 18:59$) iş çıkışı saatlerinde makro düzeyde trafiğin tepe yapmasını sağlayan katsayılar.
- **Okul Etki Katsayısı ($0.25$):** Sadece okul bölgelerindeki açık yollarda, giriş/çıkış saatlerinde (`08` ve `16` ncı saatler) yerel yoğunluğu artıran katsayı.
- **Dinamik Periyot Dalgalanması ($\cos(\text{adim} \times 0.8) \times 0.12$):** Zaman çubuğu kaydırıldığında, 15 dakikalık periyotlar arasında yollardaki emisyonun sabit kalmayıp dinamik ve organik olarak yukarı/aşağı dalgalanmasını sağlayan trigonometrik fonksiyon.
- **Doğal Gürültü ($\text{random}() \times 0.08 - 0.04$):** Gerçek hayat kaosu ve ölçüm cihazı varyasyonları için eklenen rastgele gürültü faktörü.

---

## 🎨 Arayüz Özellikleri ve Görselleştirme Sınırları

Harita üzerinde emisyon skorları dinamik olarak analiz edilerek jürinin kolay takibi için 3 ana sınıfa (Sınıflandırılmış Kloroplet Harita) ayrılmıştır:
- **🟢 Düşük Emisyon (%0 - %29):** Karbon salınımının güvenli seviyede olduğu akıcı trafik.
- **🟡 Orta Emisyon (%30 - %69):** Yoğunlaşmaya başlayan şehir trafiği.
- **🔴 Yüksek Emisyon (%70 - %100):** Emisyon limitlerinin aşıldığı, yoğun ve kilit trafik hacmi.
- **🔲 Ulaşıma Kapalı Güvenli Koridorlar:** Okul saatlerinde emisyonu düşen, koyu lacivert renkli ve kesikli çizgilerle belirtilen özel yaya koridorları.

---

## ⚙️ Kurulum, Bağımlılıklar ve Uygulamanın Başlatılması

### 1. Gereksinimlerin Yüklenmesi
Projenin çalışması için gerekli olan Python paketleri `requirements.txt` dosyasında listelenmiştir. Yüklemek için terminalde şu komutu çalıştırın:
```bash
pip install -r requirements.txt

---

https://emirr07.github.io/Low_Emission_School_Zone_Project/