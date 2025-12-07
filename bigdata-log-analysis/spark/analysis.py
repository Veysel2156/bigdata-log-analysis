"""
Spark Analiz Görevi - TAMAMLANMIŞ (Hourly Traffic Eklendi)
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, percentile_approx, when, hour, desc
import time

def main():
    print("🚀 ANALİZ BAŞLIYOR...")
    
    # Spark Ayarları
    spark = SparkSession.builder \
        .appName("LogAnalytics") \
        .config("spark.executor.memory", "2g") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("ERROR")

    # Veriyi Oku
    print("📥 Veri yükleniyor...")
    df = spark.read.parquet("s3a://parquet/logs")
    
    # Hour kolonu yoksa ekleyelim (timestamp'ten çıkaralım)
    if "hour" not in df.columns:
        df = df.withColumn("hour", hour("timestamp"))
    
    # 1. Yanıt Süreleri
    print("📊 1/5 Yanıt Süreleri Hesaplanıyor...")
    response_metrics = df.groupBy("endpoint").agg(
        count("*").alias("request_count"),
        avg("response_time").alias("avg_response_time"),
        percentile_approx("response_time", 0.95).alias("p95_response_time"),
        percentile_approx("response_time", 0.99).alias("p99_response_time")
    )
    response_metrics.write.mode("overwrite").parquet("s3a://analytics/results/response_time_metrics")

    # 2. Servis Hataları
    print("📊 2/5 Servis Hataları Hesaplanıyor...")
    service_errors = df.groupBy("service").agg(
        count("*").alias("total_requests"),
        count(when(col("level") == "ERROR", 1)).alias("error_count")
    ).withColumn("error_rate", (col("error_count") / col("total_requests")) * 100)
    service_errors.write.mode("overwrite").parquet("s3a://analytics/results/service_errors")

    # 3. Bölgesel Trafik
    print("📊 3/5 Bölgesel Trafik Hesaplanıyor...")
    region_traffic = df.groupBy("region").agg(
        count("*").alias("request_count"),
        avg("response_time").alias("avg_response_time")
    )
    region_traffic.write.mode("overwrite").parquet("s3a://analytics/results/region_traffic")

    # 4. Saatlik Trafik (EKSİK OLAN BUYDU)
    print("📊 4/5 Saatlik Trafik Hesaplanıyor...")
    hourly_traffic = df.groupBy("hour").agg(
        count("*").alias("request_count"),
        avg("response_time").alias("avg_response_time")
    ).orderBy("hour")
    hourly_traffic.write.mode("overwrite").parquet("s3a://analytics/results/hourly_traffic")

    # 5. Top Kullanıcılar
    print("📊 5/5 En Aktif Kullanıcılar Hesaplanıyor...")
    top_users = df.groupBy("user_id").agg(
        count("*").alias("request_count")
    ).orderBy(desc("request_count")).limit(100)
    top_users.write.mode("overwrite").parquet("s3a://analytics/results/top_users")

    print("✅ Tüm analizler tamamlandı ve kaydedildi!")
    spark.stop()

if __name__ == "__main__":
    main()