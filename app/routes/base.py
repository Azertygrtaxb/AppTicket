from flask import Blueprint, render_template, Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import hashlib
from app.models import User
from app.utils.mysqlconnector import MySqlConnector

base_route = Blueprint('base_route', __name__)

@base_route.route('/')
@login_required
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'], userrole = session['userrole'])
    else:
        return redirect(url_for('login'))
    
# Connexion à la base de données
db = MySqlConnector(server="51.75.25.241", databaseName="TicketsSupport", databaseUser="root", databasePassword="rootpassword")

@base_route.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password_hash = request.form.get('hashed_password')  # Hash envoyé depuis le front
        
        # Vérifier si l'utilisateur existe
        if not db.user_exist(username):
            return render_template('login.html', error="Identifiants incorrects.")

        # Récupérer le hash du mot de passe stocké en base
        stored_hash = db.get_user_hash(username)

        if not stored_hash:
            return render_template('login.html', error="Identifiants incorrects.")
        
        # Vérifier si les hash correspondent
        if password_hash != stored_hash:
            return render_template('login.html', error="Identifiants incorrects.")

        # Récupération de l'utilisateur
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            return render_template('login.html', error="Identifiants incorrects.")

        # Vérification si l'utilisateur est actif
        if not user.is_active:
            return render_template('login.html', error="Votre compte est désactivé. Contactez l'administrateur.")

        # Stocker les infos dans la session
        session['user_id'] = user.user_id 
        session['username'] = user.username
        session['userrole'] = user.role

        # Connexion avec Flask-Login
        login_user(user, force=True)
        
        return redirect(url_for('base_route.home'))

    return render_template('login.html', error=None)


@base_route.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    logout_user()
    return redirect(url_for('base_route.login'))
    
@base_route.route('/about')
@login_required
def about():
    if 'username' in session:
        return render_template('about.html', username=session['username'], userrole = session['userrole'])
    else:
        return redirect(url_for('login'))
    
@base_route.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket():
    # Récupération de l'ID utilisateur connecté avec Flask-Login
    created_by = int(current_user.get_id())  

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        # Création du ticket
        success = db.create_ticket(title, description, created_by)

        if success:
            return redirect(url_for('base_route.home'))
        else:
            return render_template('create_ticket.html', error="Erreur lors de la création du ticket.", username=session['username'], userrole = session['userrole'])

    return render_template('create_ticket.html', error=None, username=session['username'], userrole = session['userrole'])

@base_route.route('/tickets')
@login_required
def user_tickets():
    user_id = int(current_user.get_id())  
    # Récupération des ticket
    tickets = db.get_tickets_by_user(user_id)  

    return render_template("tickets.html", tickets=tickets, username=session['username'], userrole = session['userrole'])
        
@base_route.route('/update_user')
@login_required
def update_user():
    if 'username' in session:
        return render_template('update_user.html', username=session['username'], userrole = session['userrole'])
    else:
        return redirect(url_for('login'))
        
        
@base_route.route('/all_tickets')
@login_required
def all_tickets():
    if 'username' in session:
        return render_template('all_tickets.html', username=session['username'], userrole = session['userrole'])
    else:
        return redirect(url_for('login'))
        
@base_route.route('/config_users', methods=['GET', 'POST'])
@login_required
def add_user():
    # Récupération des infos du frontend
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        phone_number = request.form.get('phone_number')

        # Calcul du hash saisi
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Création de l'utilisateur dans la BDD
        success = db.add_user(username, hashed_password, email, role, phone_number)

        if success:
            return redirect(url_for('base_route.home'))
        else:
            return render_template('config_users.html', error="Erreur: l'utilisateur existe déjà.")

    return render_template('config_users.html', error=None, username=session['username'], userrole = session['userrole'])




@base_route.route('/assigned_tickets')
@login_required
def assigned_tickets():
    if 'username' in session:
        return render_template('assigned_tickets.html', username=session['username'], userrole = session['userrole'])
    else:
        return redirect(url_for('login'))


@base_route.route('/statistics')
@login_required
def statistics():
    if 'username' in session:
        return render_template('statistics.html', username=session['username'], userrole = session['userrole'])
    else:
        return redirect(url_for('login'))