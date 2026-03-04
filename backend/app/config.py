from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'pkp-bet-backend'
    database_url: str = 'postgresql+psycopg2://pkp:pkp@db:5432/pkp_bet'
    plk_api_base_url: str = 'https://pdp-api.plk-sa.pl'
    plk_api_key: str = ''


settings = Settings()
