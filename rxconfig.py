import reflex as rx

config = rx.Config(
    app_name="sva_eps",
    api_url="http://localhost:8000",
    # Añadimos la conexión a PostgreSQL de Supabase
    db_url="postgresql://postgres.lugzlpuwbmnhwrifqnxm:hackatec123@aws-1-us-west-2.pooler.supabase.com:5432/postgres"
)