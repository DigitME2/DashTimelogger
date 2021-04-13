from flask import Flask
from flask_user import UserManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

db = SQLAlchemy()
migrate = Migrate()
manager = Manager()


from .models import User

def init_app():
    # Initialize flask app and load the configuration from config class
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    # SQLAlchemy is used to connect and manage the database
    db.init_app(app)

    # Migrate library is used to migrate the database in case the data schema changes
    migrate.init_app(app, db)

    # Manager is used to add command line option to python app
    # This is only used for migrating the database and should be disabled by default
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    # Uncomment this if you want to enable flask-manager
    #manager.run()

    # UserManager is used to manage the User sessions, logging in and registration.
    try:
        user_manager = UserManager(app, db, User)
    except:
        print('error')
        
    @app.context_processor
    def context_processor():
        return dict(user_manager=user_manager)   
        
    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        # Import Dash application
        from .timelogger_dash.init_dash import init_dashboard

        # Initialize Dash into our application
        app = init_dashboard(app, db)
        return app
        
