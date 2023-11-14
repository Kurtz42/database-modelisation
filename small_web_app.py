from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib

app = Flask(__name__)
app.secret_key = 'my_secret_key' # ajout de la clé secrète pour éviter l'erreur précédente

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Base = declarative_base()

class Students(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    addr = Column(String(200), nullable=False)
    pin = Column(String(32), nullable=False) # Stockage du PIN en tant que chaîne de caractères de 32 caractères (128 bits)

    def __init__(self, name, city, addr, pin):
        self.name = name
        self.city = city
        self.addr = addr
        self.pin = pin

@app.route('/')
def show_all():
    # Création de la session
    
    Session = sessionmaker(bind=engine)
    session = Session()

    # # Récupération de tous les enregistrements de la table students
    students_list = session.query(Students).all()

        
    # Passage de la liste des étudiants à la vue
    return render_template('show_all.html', students=students_list)

@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['name'] or not request.form['city'] or not request.form['addr']:
         flash('Please enter all the fields', 'error')
      else:
         # Hachage du PIN avec MD5
         hashed_pin = hashlib.md5(request.form['pin'].encode('utf-8')).hexdigest()
         
         student = Students(request.form['name'], request.form['city'],
            request.form['addr'], hashed_pin)
         
         engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
         Session = sessionmaker(bind=engine)
         session = Session()

         session.add(student)
         session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all'))
   return render_template('new.html')

if __name__ == '__main__':
    # from sqlalchemy import create_engine
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    
    Base.metadata.create_all(engine)
    app.run(debug=True)