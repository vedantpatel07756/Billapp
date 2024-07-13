from flask import Flask, render_template,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# class PartyData(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), nullable=False)
#     contact_number = db.Column(db.String(20), nullable=False)
#     gst_number = db.Column(db.String(15), nullable=False)
#     pan_number = db.Column(db.String(10), nullable=False)
#     type = db.Column(db.String(50), nullable=False)
#     balance=db.Column(db.Integer(),nullable=False)
#     task=db.Column(db.String(50),nullable=False)

with app.app_context():
    from .party import party_bp
    from .items import items_bp
    from .invoice_bp import invoice_bp
    from .user import user_bp
    db.create_all()



# Time Pass


@app.route('/')
def home():
    # Pass individual variables to the template
    title = 'Home Page'
    greeting = 'Welcome to our website!'
    content = 'This is the home page content.'
    return render_template('index.html', title=title, greeting=greeting, content=content)




app.register_blueprint(party_bp)

app.register_blueprint(items_bp)

app.register_blueprint(invoice_bp)
app.register_blueprint(user_bp)


if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)


# flask run  --host 0.0.0.0 --port 5000 --debug
