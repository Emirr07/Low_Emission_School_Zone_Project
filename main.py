from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Kepez CBS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="leszp",
        user="postgres",
        password="YOUR_PASSWORD",
        port="5432"
    )
    return conn

@app.get("/api/okullar")
def get_okullar():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
    SELECT jsonb_build_object(
        'type',     'FeatureCollection',
        'features', jsonb_agg(features.feature)
    ) AS geojson
    FROM (
        SELECT jsonb_build_object(
            'type',       'Feature',
            'id',         id,
            'geometry',   ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
            'properties', jsonb_build_object('okul_adi', okul_adi)
        ) AS feature
        FROM okul_buffer_200m
    ) features;
    """
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if not result or not result['geojson'] or result['geojson']['features'] is None:
        return {"type": "FeatureCollection", "features": []}
    return result['geojson']

@app.get("/api/okul-binalari")
def get_okul_binalari():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
    SELECT jsonb_build_object(
        'type',     'FeatureCollection',
        'features', jsonb_agg(features.feature)
    ) AS geojson
    FROM (
        SELECT jsonb_build_object(
            'type',       'Feature',
            'id',         id,
            'geometry',   ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
            'properties', jsonb_build_object('okul_adi', id)
        ) AS feature
        FROM kepez_okullari
    ) features;
    """
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if not result or not result['geojson'] or result['geojson']['features'] is None:
        return {"type": "FeatureCollection", "features": []}
    return result['geojson']

@app.get("/api/trafik")
def get_trafik(saat: int = 12, dakika: int = 0):
    if saat < 0 or saat > 23: saat = 12
    if dakika not in [0, 15, 30, 45]: dakika = 0
        
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT jsonb_build_object(
        'type',     'FeatureCollection',
        'features', jsonb_agg(features.feature)
    ) AS geojson
    FROM (
        SELECT jsonb_build_object(
            'type',       'Feature',
            'id',         yol_id,
            'geometry',   ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
            'properties', jsonb_build_object(
                'kapali_mi', CASE WHEN %s IN (8, 16) AND yol_id IN (SELECT DISTINCT yol_id FROM okul_yollari_kesisen) THEN true ELSE false END,
                'emisyon',   CASE WHEN %s IN (8, 16) AND yol_id IN (SELECT DISTINCT yol_id FROM okul_yollari_kesisen) THEN 0.0 ELSE yogunluk_skoru END
            )
        ) AS feature
        FROM kepez_yol_trafigi
        WHERE saat = %s AND dakika = %s
    ) features;
    """
    cursor.execute(query, (saat, saat, saat, dakika))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if not result or not result['geojson'] or result['geojson']['features'] is None:
        return {"type": "FeatureCollection", "features": []}
    return result['geojson']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)