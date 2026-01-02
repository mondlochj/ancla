import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Proxy configuration for Apache
    APPLICATION_ROOT = '/ancla'
    PREFERRED_URL_SCHEME = 'https'
    SERVER_NAME = os.getenv('SERVER_NAME')  # Set in production: aroaero.com

    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.jetoko.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    FROM_EMAIL = os.getenv('FROM_EMAIL')

    # File uploads
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/opt/ancla/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Session configuration
    SESSION_COOKIE_SECURE = True  # Always secure (behind HTTPS proxy)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_PATH = '/ancla'

    # Business rules
    MIN_LOAN_AMOUNT = 10000  # Q10,000
    MAX_LTV = 0.40  # 40%
    DEFAULT_INTEREST_RATE = 0.10  # 10% monthly
    LATE_FEE_RATE = 0.05  # 5% late fee
    GRACE_PERIOD_DAYS = 5
    DEFAULT_TRIGGER_DAYS = 15
    LEGAL_READY_DAYS = 30


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow non-HTTPS in development
    SERVER_NAME = None  # Don't enforce server name in dev
    PREFERRED_URL_SCHEME = 'http'


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
