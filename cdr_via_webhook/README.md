# Hipcall CDR Webhook Dummy App

Bu uygulama, Hipcall üzerinden gelen çağrı kayıtlarını (CDR) webhook aracılığıyla almak ve bir CRM dashboard'unda görüntülemek için tasarlanmıştır.

## Kurulum ve Çalıştırma

1. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
2. Veritabanını başlatın:
   ```bash
   python init_db.py
   ```
3. Uygulamayı çalıştırın:
   ```bash
   python app.py
   ```
   Uygulama varsayılan olarak `http://localhost:5007` adresinde çalışacaktır.

## ngrok ile Dış Dünyaya Açma (Yerel Test İçin)

Hipcall'un yerel bilgisayarınızdaki uygulamaya ulaşabilmesi için `ngrok` kullanabilirsiniz:

1. Yeni bir terminal penceresi açın ve şu komutu çalıştırın:
   ```bash
   ngrok http 5007
   ```
2. Ekrandaki **Forwarding** satırında yazan (örn: `https://abcd-123.ngrok-free.app`) adresi kopyalayın.
3. Hipcall panelindeki URL alanına bu adresi sonuna `/webhook/hipcall-cdr` ekleyerek yapıştırın:
   `https://abcd-123.ngrok-free.app/webhook/hipcall-cdr`

## Hipcall Entegrasyonu

Hipcall panelinde bir webhook oluştururken şu ayarları yapın:

- **Target URL:** `http://[SUNUCU_IP_VEYA_DOMAIN]:5007/webhook/hipcall-cdr`
- **Events:** `Çağrı kapanışı` (call.ended)

## Proje Yapısı

- `app.py`: Flask sunucusu ve webhook endpoint'i.
- `init_db.py`: SQLite veritabanı şema oluşturucu.
- `templates/`: Dashboard arayüzü (HTML).
- `static/`: CSS ve JS dosyaları.
- `data/`: Veritabanı dosyasının saklandığı dizin.
