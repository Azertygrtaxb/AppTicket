from flask import Blueprint, render_template, Flask, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import logging
from app.models import User
from app.utils.mysqlconnector import MySqlConnector
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.config import DB_PASSWORD, DB_NAME, DB_HOST, DB_USER

base_route = Blueprint('base_route', __name__)

# Connexion à la base de données
db = MySqlConnector(server=DB_HOST, databaseName=DB_NAME, databaseUser=DB_USER, databasePassword=DB_PASSWORD)

@base_route.route('/')
@login_required
def home():

    if 'username' in session:
        return render_template('home.html', username=session['username'], userrole = session['userrole'])
    else:
        return redirect(url_for('login'))
    
@base_route.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')  # Mot de passe en clair envoyé depuis le front
        
        # Vérifier si l'utilisateur existe
        if not db.user_exist(username):
            return render_template('login.html', error="Identifiants incorrects.")

        # Récupérer le hash du mot de passe stocké en base
        stored_hash = db.get_user_hash(username)

        if not stored_hash:
            return render_template('login.html', error="Identifiants incorrects.")
        
        # Vérifier si les hash correspondent en hashant le mot de passe envoyé
        if not check_password_hash(stored_hash, password):  # Comparaison avec le mot de passe en clair
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

        # Connexion 
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
    # Récupération de l'id de utilisateur connecté.
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

@base_route.route('/add_comment/<int:ticket_id>', methods=['POST'])
@login_required
def add_comment(ticket_id):
    if 'username' not in session:
        return redirect(url_for('base_route.login'))

    user_id = int(current_user.get_id())
    comment = request.form.get('comment')  
    # Vérifie s'il y a bien un commentaire
    if not comment:
        flash("Le commentaire ne peut pas être vide.", "error")
        return redirect(url_for('base_route.view_ticket', ticket_id=ticket_id))
    # Ajoute le commentaire a la DB
    success = db.add_comment(ticket_id, user_id, comment)

    if success:
        flash("Commentaire ajouté avec succès.", "success")
    else:
        flash("Erreur lors de l'ajout du commentaire.", "error")

    return redirect(url_for('base_route.view_ticket', ticket_id=ticket_id))


@base_route.route('/tickets')
@login_required
def user_tickets():
    user_id = int(current_user.get_id())  
    # Récupération des ticket
    tickets = db.get_tickets_by_user(user_id)  

    return render_template("tickets.html", tickets=tickets, username=session['username'], userrole = session['userrole'])

@base_route.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    if 'username' not in session:
        return redirect(url_for('base_route.login'))
    
    # Récupérer les détails du ticket depuis la base de données
    ticket = db.get_ticket_by_id(ticket_id)
    
    if not ticket:
        flash("Ticket introuvable.", "error")
        return redirect(url_for('base_route.user_tickets'))
    
    # Récupérer les commentaires associés au ticket
    comments = db.get_comments_by_ticket(ticket_id)

    return render_template('ticket_details.html',ticket=ticket, comments=comments, username=session['username'], userrole=session['userrole'])

@base_route.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    if 'username' not in session:
        return redirect(url_for('base_route.login'))

    success = db.delete_ticket(ticket_id)

    if success:
        flash("Ticket supprimé avec succès.", "success")
    else:
        flash("Erreur lors de la suppression du ticket.", "error")

    return redirect(url_for('base_route.user_tickets'))

@base_route.route('/update_user')
@login_required
def update_user():
    try:
        data = request.get_json()

        # Récupération des données envoyées
        username = data.get('username')
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        # Vérification des champs requis
        if not username:
            return jsonify({"error": "Le champ 'username' est requis."}), 400

        # Hashage du mot de passe si fourni
        hashed_password = generate_password_hash(password) if password else None

        # Mise à jour des informations utilisateur
        success = db.update_user_info(username, hashed_password, email, phone_number)

        if success:
            return jsonify({"message": f"Utilisateur {username} mis à jour avec succès."}), 200
        else:
            return jsonify({"error": "Échec de la mise à jour. L'utilisateur n'existe peut-être pas."}), 400

    except Exception as e:
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500
        
        
@base_route.route('/all_tickets')
@login_required
def all_tickets():
    if 'username' not in session:
        return redirect(url_for('base_route.login'))
    # Récupération des tickets
    tickets = db.get_open_tickets()  

    return render_template('all_tickets.html', username=session['username'], userrole=session['userrole'], tickets=tickets)
        
@base_route.route('/config_users', methods=['GET', 'POST'])
@login_required
def add_user():
    # Récupération des infos du frontend
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('hashed_password')
        role = request.form.get('role')
        phone_number = request.form.get('phone')

        logging.info('hash : ' + password)
        # Création de l'utilisateur dans la BDD
        success = db.add_user(username, password, email, role, phone_number)

        if success:
            return redirect(url_for('base_route.home'))
        else:
            return render_template('config_users.html', error="Erreur: l'utilisateur existe déjà.")

    return render_template('config_users.html', error=None, username=session['username'], userrole = session['userrole'])


@base_route.route('/assign_ticket', methods=['POST'])
@login_required
def assign_ticket():
    if 'username' not in session:
        return redirect(url_for('base_route.login'))
    # Récupération des infos du front
    ticket_id = request.form.get('ticket_id')
    user_id = request.form.get('user_id')

    # Verifier si on a les ID
    if not ticket_id or not user_id:
        flash("ID du ticket ou de l'utilisateur manquant.", "error")
        return redirect(url_for('base_route.all_tickets'))

    try:
        ticket_id = int(ticket_id)
        user_id = int(user_id)
    except ValueError:
        flash("ID invalide.", "error")
        return redirect(url_for('base_route.all_tickets'))

    success = db.assign_user_to_ticket(ticket_id, user_id)

    if success:
        flash(f"Le ticket {ticket_id} a été assigné à l'utilisateur {user_id}.", "success")
    else:
        flash("Échec de l'assignation du ticket.", "error")

    return redirect(url_for('base_route.all_tickets'))


@base_route.route('/statistics')
@login_required
def statistics():
    if 'username' in session:
        return render_template('statistics.html', username=session['username'], userrole = session['userrole'])
    else:
        return redirect(url_for('login'))

@base_route.route('/users')
@login_required
def all_users():
    if 'username' not in session:
        return redirect(url_for('base_route.login'))
    # Récupérer la liste des utilisateurs
    users = db.get_all_users()

    return render_template('users.html', users=users, username=session['username'], userrole=session['userrole'])


@base_route.route('/knowledge')
@login_required
def knowledge():
    if 'username' in session:
        return render_template('about.html', username=session['username'], userrole = session['userrole'])
    else:
        return redirect(url_for('login'))
    
@base_route.route('/deactivate_user', methods=['PUT'])
def deactivate_user():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Le champ 'user_id' est requis"}), 400

    success = db.user_inactive(user_id)

    if success:
        return jsonify({"message": f"Utilisateur {user_id} désactivé avec succès."}), 200
    else:
        return jsonify({"error": "Échec de la désactivation de l'utilisateur"}), 400
