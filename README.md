Proje ÖzetiBu proje, büyük ölçekli ham web sunucusu log verisini etkin bir şekilde işlemek, analiz etmek ve görselleştirmek için uçtan uca, dağıtık bir veri işleme pipeline'ı (borusu) kurmayı amaçlamıştır. Bu çalışma, modern Big Data teknolojilerini kullanarak verimlilik, depolama optimizasyonu ve düşük gecikmeli erişim konularına odaklanmaktadır.⚙️ Teknik Amaçlar ve BaşarımlarBaşarım/HedefKullanılan TeknolojiSonuç Odaklı AçıklamaDepolama OptimizasyonuApache Spark (PySpark), Parquet5 milyon satırlık (1.2 GB) ham log verisini satır tabanlı JSON formatından sütun tabanlı Parquet formatına dönüştürerek depolama maliyetinde %75 tasarruf sağlandı.Dağıtık Veri İşlemePySparkVeri setinin dağıtık ortamda hızlı işlenmesi sağlandı ve anahtar performans ölçütleri (Okuma/Yazma süreleri) optimize edildi.Veri GörselleştirmeStreamlitSpark ile işlenen temizlenmiş ve analiz edilmiş verileri kullanarak, interaktif bir web tabanlı izleme ve analiz dashboard'u geliştirildi.Düşük Gecikmeli Veri ErişimiHBaseAnaliz sonuçları, okuma performansına odaklanmış bir şema tasarımıyla HBase NoSQL veritabanına kaydedilerek anlık erişim gerektiren dashboard için optimize edildi.Veri AnaliziPySpark, Veri KalitesiProje kapsamında, genel servis hata oranı %7.75 olarak hesaplandı ve en hatalı servis olan payment-service tespit edilerek kök neden analizi için zemin hazırlandı.🛠️ Kullanılan TeknolojilerBu projenin omurgasını oluşturan temel teknolojiler şunlardır:Programlama Dili: PythonDağıtık İşleme: Apache Spark (PySpark)Veri Depolama: MinIO (S3 Uyumlu Nesne Depolama), Parquet (Sütun Tabanlı Format)Veritabanı: HBase (NoSQL, Geniş Sütunlu)Görselleştirme: StreamlitÇevre: Docker / Docker Compose (Yerel Dağıtık ortam simülasyonu için)📂 Proje Yapısıbigdata-log-analysis/
├── data/
│   └── raw_logs.jsonl
├── notebooks/
│   └── spark_analysis.ipynb      # Spark transformasyon ve analiz kodları
├── src/
│   ├── spark_job.py              # PySpark script'i
│   └── streamlit_app.py          # Görselleştirme uygulaması
├── docker-compose.yml            # Tüm servislerin (Spark, MinIO, HBase) ayarları
└── README.md                     # Bu dosya
🏃 Nasıl Çalıştırılır (Kurulum)Depoyu Klonlayın:Bashgit clone https://github.com/KullaniciAdiniz/bigdata-log-analysis.git
cd bigdata-log-analysis
Docker Ortamını Başlatın:Bashdocker-compose up -d
Spark İşini Çalıştırın:(Örnek komut, Spark konteyneri içinde çalıştırılmalıdır.)Bashdocker exec -it spark-master /bin/bash -c "spark-submit /app/src/spark_job.py"
Streamlit Dashboard'u Görüntüleyin:Tarayıcınızda http://localhost:8501 adresine giderek analiz sonuçlarını görüntüleyebilirsiniz.
