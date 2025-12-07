"""
HBase Veri Yükleyici - TAMAMLANMIŞ (Rank Hatası Düzeltildi)
"""
import happybase
from pyspark.sql import SparkSession
import sys
import time
# schema.py dosyasından şemayı çekiyoruz
from schema import HBASE_SCHEMA

# Ayarlar
HBASE_HOST = "hbase"
HBASE_PORT = 9090
MINIO_OPTS = {
    "endpoint": "http://minio:9000",
    "access_key": "minioadmin",
    "secret_key": "minioadmin123"
}

def connect_hbase():
    print(f"📡 HBase'e bağlanılıyor ({HBASE_HOST})...")
    try:
        conn = happybase.Connection(host=HBASE_HOST, port=HBASE_PORT, timeout=10000)
        conn.open()
        print("✅ Bağlantı başarılı")
        return conn
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        sys.exit(1)

def create_tables(conn):
    try:
        existing = set(t.decode('utf-8') for t in conn.tables())
        for t_name, schema in HBASE_SCHEMA.items():
            if t_name not in existing:
                print(f"🔨 Tablo oluşturuluyor: {t_name}")
                conn.create_table(t_name, {cf: dict() for cf in schema['cf']})
    except Exception as e:
        print(f"⚠️ Tablo oluşturma hatası: {e}")

def get_spark():
    return SparkSession.builder \
        .appName("HBaseLoader") \
        .config("spark.executor.memory", "1g") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_OPTS["endpoint"]) \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_OPTS["access_key"]) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_OPTS["secret_key"]) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .getOrCreate()

def load_table(spark, conn, table_name, path, row_key_col, col_family):
    print(f"📥 {table_name} yükleniyor...")
    try:
        # Veriyi oku
        df = spark.read.parquet(path)
        rows = df.collect()
        
        if not rows:
            print(f"   ⚠️ {path} altında veri bulunamadı, atlanıyor.")
            return

        table = conn.table(table_name)
        batch = table.batch()
        
        count = 0
        # DÜZELTME BURADA: enumerate ile sıralamayı biz veriyoruz
        for i, row in enumerate(rows):
            # Row Key belirle
            if table_name == "top_users":
                # Veri zaten sıralı olduğu için index'i (i) rank olarak kullanıyoruz
                rank = i + 1 
                rk = f"user_{rank}_{row['user_id']}".encode()
                
                # Rank bilgisini kolonlara da ekleyelim ki dashboard'da görünsün
                batch.put(rk, {f"{col_family}:rank".encode(): str(rank).encode()})
                
            elif table_name == "hourly_traffic":
                 rk = f"hour_{row['hour']}".encode()
            else:
                rk = str(row[row_key_col]).encode()
            
            # Diğer kolonları ekle
            data = {}
            for col_name in row.asDict():
                if col_name != row_key_col:
                    val = str(row[col_name]).encode()
                    data[f"{col_family}:{col_name}".encode()] = val
            
            batch.put(rk, data)
            count += 1
        
        batch.send()
        print(f"✅ {count} satır yüklendi.")
    except Exception as e:
        print(f"⚠️  Hata ({table_name}): {e}")

def main():
    conn = connect_hbase()
    create_tables(conn)
    
    spark = get_spark()
    spark.sparkContext.setLogLevel("ERROR")
    
    base = "s3a://analytics/results"
    
    # Verileri Yükle
    load_table(spark, conn, "response_metrics", f"{base}/response_time_metrics", "endpoint", "metrics")
    load_table(spark, conn, "service_errors", f"{base}/service_errors", "service", "stats")
    load_table(spark, conn, "region_traffic", f"{base}/region_traffic", "region", "traffic")
    load_table(spark, conn, "hourly_traffic", f"{base}/hourly_traffic", "hour", "traffic")
    load_table(spark, conn, "top_users", f"{base}/top_users", "user_id", "user")
    
    conn.close()
    spark.stop()

if __name__ == "__main__":
    main()