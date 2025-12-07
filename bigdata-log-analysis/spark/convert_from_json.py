"""
JSON'dan Parquet'ye Dönüştürme - TAMAMLANMIŞ
"""
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import to_timestamp
import time

# MinIO Ayarları
MINIO_CONF = {
    "endpoint": "http://minio:9000",
    "access_key": "minioadmin",
    "secret_key": "minioadmin123"
}

def main():
    print("🚀 DÖNÜŞTÜRME BAŞLIYOR...")
    
    # Spark Oturumu
    spark = SparkSession.builder \
        .appName("FormatConverter") \
        .config("spark.executor.memory", "2g") \
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

    # Şema Tanımı
    schema = StructType([
        StructField("timestamp", StringType(), True),
        StructField("service", StringType(), True),
        StructField("endpoint", StringType(), True),
        StructField("level", StringType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("ip", StringType(), True),
        StructField("region", StringType(), True),
        StructField("response_time", IntegerType(), True),
        StructField("status_code", IntegerType(), True),
        StructField("error_code", StringType(), True),
        StructField("message", StringType(), True),
        StructField("warn_detail", StringType(), True) 
    ])

    # 1. JSON Oku
    print("📥 JSON verisi okunuyor (MinIO)...")
    start = time.time()
    df = spark.read.schema(schema).json("s3a://logs/*.json")
    df = df.withColumn("timestamp", to_timestamp("timestamp"))
    
    count = df.count()
    print(f"✅ {count:,} kayıt bulundu. (Süre: {time.time()-start:.2f}sn)")

    # 2. Parquet Yaz
    print("📦 Parquet formatına dönüştürülüyor...")
    start = time.time()
    # Analytics klasörü altına yazıyoruz ki analiz scripti bulabilsin
    df.write.mode("overwrite").parquet("s3a://parquet/logs")
    print(f"✅ Dönüştürme tamamlandı. (Süre: {time.time()-start:.2f}sn)")

    spark.stop()

if __name__ == "__main__":
    main()