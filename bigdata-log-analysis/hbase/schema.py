"""
HBase Tablo Şemaları
"""
HBASE_SCHEMA = {
    "response_metrics": {
        "cf": ["metrics"],
        "desc": "Endpoint performans metrikleri"
    },
    "service_errors": {
        "cf": ["stats"],
        "desc": "Servis hata istatistikleri"
    },
    "region_traffic": {
        "cf": ["traffic"],
        "desc": "Bölgesel trafik"
    },
    "hourly_traffic": {
        "cf": ["traffic"],
        "desc": "Saatlik trafik trendleri"
    },
    "top_users": {
        "cf": ["user"],
        "desc": "En aktif kullanıcılar"
    }
}