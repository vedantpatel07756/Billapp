from flask import Flask, render_template,request,jsonify,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask_socketio import SocketIO, emit


app = Flask(__name__)
socketio = SocketIO(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

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

# Time Pass
        # DEV-IT contact email for account deletion
DEVIT_EMAIL = "vsfusion2608@gmail.com"

@app.route('/delete-account', methods=['GET'])
def delete_account():
    # Generate the URL for the Play Store account deletion process
    playstore_link = url_for('playstore_account_deletion', _external=True)
    return render_template('delete_account.html', email=DEVIT_EMAIL, playstore_link=playstore_link)

@app.route('/playstore-account-deletion', methods=['GET'])
def playstore_account_deletion():
    return "Account deletion process initiated. Please contact DEV-IT for further assistance."




app.register_blueprint(party_bp)

app.register_blueprint(items_bp)

app.register_blueprint(invoice_bp)
app.register_blueprint(user_bp)


# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    socketio.run(app, debug=True)
# if __name__ == '__main__':
#     app.run(port=5000, debug=True)


# flask run  --host 0.0.0.0 --port 5000 --debug
