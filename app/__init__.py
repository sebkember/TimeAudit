from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .routes.auth import auth_pages_bp
from .routes.pages import pages_bp
from .routes.api.account import account_bp
from .routes.api.activities import activities_bp
from .routes.api.auth import auth_bp
from .routes.api.goals import goals_bp
from .routes.api.scheduled_activities import scheduled_activities_bp

limiter = Limiter(key_func=get_remote_address)

def app_factory():
  app = Flask(__name__)

  # Workaround for limiter circular import
  from .routes.api.ai import generate_bp

  # Attach rate limiter
  limiter.init_app(app)

  # Register blueprints
  app.register_blueprint(auth_pages_bp)
  app.register_blueprint(pages_bp)
  app.register_blueprint(account_bp)
  app.register_blueprint(activities_bp)
  app.register_blueprint(generate_bp)
  app.register_blueprint(auth_bp)
  app.register_blueprint(goals_bp)
  app.register_blueprint(scheduled_activities_bp  )

  return app