import os
import glob
from minio import Minio
from minio.error import S3Error
from tqdm import tqdm

# ============================================
# MinIO Yapılandırması
# ============================================
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"
MINIO_BUCKET = "logs"
MINIO_SECURE = False
LOGS_DIR = "logs"

def upload_to_minio():
    print(f"{'='*60}")
    print(f"🚀 MinIO Yükleyici Başlatılıyor...")
    print(f"{'='*60}")

    # 1. MinIO Bağlantısı
    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        print(f"✅ İstemci oluşturuldu: {MINIO_ENDPOINT}")
    except Exception as e:
        print(f"❌ MinIO istemcisi hatası: {e}")
        return

    # 2. Bucket Kontrolü
    try:
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
            print(f"✅ Bucket oluşturuldu: '{MINIO_BUCKET}'")
        else:
            print(f"ℹ️  Bucket zaten mevcut: '{MINIO_BUCKET}'")
    except S3Error as e:
        print(f"❌ Bucket hatası: {e}")
        return

    # 3. Dosyaları Bul
    log_files = glob.glob(os.path.join(LOGS_DIR, "*.json"))
    if not log_files:
        print(f"⚠️  '{LOGS_DIR}' klasöründe dosya yok! Log generator çalıştı mı?")
        return

    print(f"📂 Bulunan dosya sayısı: {len(log_files)}")

    # 4. Yükleme
    success = 0
    for file_path in tqdm(log_files, desc="Yükleniyor", unit="dosya"):
        try:
            file_name = os.path.basename(file_path)
            client.fput_object(MINIO_BUCKET, file_name, file_path, content_type="application/json")
            success += 1
        except Exception as e:
            print(f"❌ Hata ({file_name}): {e}")

    print(f"\n✅ Toplam {success} dosya başarıyla MinIO'ya yüklendi!")

if __name__ == "__main__":
    upload_to_minio()