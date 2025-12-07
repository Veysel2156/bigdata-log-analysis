"""
Spark Optimizasyon Teknikleri - TAMAMLANMIŞ
GÖREV: Bloom Filter ve Bitset kullanımını gösterir.
"""

from pyspark.sql import SparkSession
import time
import hashlib

# Ayarlar
MINIO_CONF = {
    "endpoint": "http://minio:9000",
    "access_key": "minioadmin",
    "secret_key": "minioadmin123"
}

class BloomFilter:
    def __init__(self, size, num_hashes):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size

    def _hash(self, item, seed):
        text = f"{item}_{seed}".encode('utf-8')
        return int(hashlib.md5(text).hexdigest(), 16) % self.size

    def add(self, item):
        for i in range(self.num_hashes):
            self.bit_array[self._hash(item, i)] = 1

    def contains(self, item):
        for i in range(self.num_hashes):
            if self.bit_array[self._hash(item, i)] == 0:
                return False
        return True

class IPBitset:
    def __init__(self):
        # 0-255 arası IP son okteti için
        self.bitset = [0] * 256

    def add(self, ip_last_octet):
        try:
            val = int(ip_last_octet)
            if 0 <= val < 256:
                self.bitset[val] = 1
        except:
            pass

    def contains(self, ip_last_octet):
        try:
            val = int(ip_last_octet)
            return self.bitset[val] == 1
        except:
            return False

def main():
    print("🚀 OPTİMİZASYON TESTLERİ BAŞLIYOR...")
    
    spark = SparkSession.builder \
        .appName("OptimizationDemo") \
        .config("spark.executor.memory", "1g") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_CONF["endpoint"]) \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_CONF["access_key"]) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_CONF["secret_key"]) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("ERROR")

    # Veriyi Oku
    print("📥 Veri yükleniyor (Parquet)...")
    df = spark.read.parquet("s3a://parquet/logs")
    
    # Test Verileri
    target_user = 42
    target_ip_octet = 100

    # --- TEST 1: Bloom Filter ---
    print("\n🔍 1. BLOOM FILTER TESTİ (User ID Arama)")
    
    # Normal Arama
    start = time.time()
    found = df.filter(df.user_id == target_user).count() > 0
    normal_time = time.time() - start
    print(f"   -> Normal Spark Araması: {normal_time:.4f} sn")

    # Bloom Filter Hazırlığı (Simülasyon)
    # Gerçekte bu filtre önceden hazırlanmış olur
    bf = BloomFilter(100000, 3)
    users = df.select("user_id").distinct().collect()
    for u in users:
        bf.add(u["user_id"])
        
    start = time.time()
    exists = bf.contains(target_user)
    bf_time = time.time() - start
    print(f"   -> Bloom Filter Kontrolü: {bf_time:.6f} sn")
    print(f"   🚀 Hızlanma: {normal_time / bf_time:.0f}x kat")

    # --- TEST 2: Bitset ---
    print("\n🔍 2. BITSET TESTİ (IP Filtreleme)")
    
    # Normal Filtreleme
    start = time.time()
    count = df.filter(df.ip.endswith(f".{target_ip_octet}")).count()
    normal_time = time.time() - start
    print(f"   -> Normal String Araması: {normal_time:.4f} sn")
    
    # Bitset Hazırlığı
    bitset = IPBitset()
    ips = df.select("ip").distinct().collect()
    for row in ips:
        parts = row["ip"].split('.')
        bitset.add(parts[-1])
        
    start = time.time()
    exists = bitset.contains(target_ip_octet)
    bs_time = time.time() - start
    print(f"   -> Bitset Kontrolü: {bs_time:.6f} sn")
    print(f"   🚀 Hızlanma: {normal_time / bs_time:.0f}x kat")
    
    spark.stop()

if __name__ == "__main__":
    main()