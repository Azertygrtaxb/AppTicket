import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Ticket, TicketComment 

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MySqlConnector:
    """
    Classe pour gérer la connexion à MySQL et les interactions avec les utilisateurs.
    """

    def __init__(self, server, databaseName, databaseUser, databasePassword):
        """Initialise la connexion à MySQL."""
        self.DATABASE_URL = f"mysql+pymysql://{databaseUser}:{databasePassword}@{server}/{databaseName}"
        self.engine = create_engine(self.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def create_tables(self):
        """Crée les tables si elles n'existent pas déjà."""
        Base.metadata.create_all(self.engine)
        logging.info("Tables créées avec succès.")

    def close(self):
        """Ferme la connexion."""
        self.session.close()
        logging.info("Connexion fermée.")

    def user_exist(self, username: str) -> bool:
        """Vérifie si un utilisateur existe."""
        return self.session.query(User).filter_by(username=username).first() is not None

    def get_user_hash(self, username: str):
        """Récupère le hash du mot de passe d'un utilisateur."""
        user = self.session.query(User).filter_by(username=username).first()
        return user.hashpassword if user else None

    def find_user_id(self, username: str):
        """Récupère l'ID d'un utilisateur à partir de son nom d'utilisateur."""
        user = self.session.query(User.user_id).filter_by(username=username).first()
        return user.user_id if user else None

    def add_user(self, username: str, hashed_password: str, email: str, role: str, phone_number: str) -> bool:
        """Ajoute un utilisateur."""
        if self.user_exist(username):
            logging.warning(f"L'utilisateur {username} existe déjà.")
            return False

        new_user = User(username=username, hashpassword=hashed_password, email=email, role=role, phone_number=phone_number)
        
        try:
            self.session.add(new_user)
            self.session.commit()
            logging.info(f"Utilisateur {username} ajouté avec succès.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur lors de l'ajout de l'utilisateur {username}: {e}")
            return False

    def get_ticket_summary(self):
        """Récupère uniquement les informations essentielles des tickets."""
        return self.session.query(Ticket.ticket_id, Ticket.title, Ticket.status, Ticket.created_at, Ticket.created_by).all()

    def get_tickets_by_user(self, user_id: int):
        """Récupère les tickets d'un utilisateur."""
        return self.session.query(Ticket.ticket_id, Ticket.title, Ticket.status, Ticket.created_at) \
        .filter_by(created_by=user_id).all()

    def get_open_tickets(self):
        """Récupère les tickets ouverts ou en cours."""
        return self.session.query(Ticket.ticket_id, Ticket.title, Ticket.status, Ticket.created_at) \
            .filter(Ticket.status.in_(["ouvert", "en cours"])).all()

    def create_ticket(self, title: str, description: str, created_by: int) -> bool:
        """Crée un ticket si l'utilisateur existe."""
        if not self.user_exist(created_by):
            return False

        try:
            self.session.add(Ticket(title=title, description=description, created_by=created_by, status="ouvert"))
            self.session.commit()
            return True
        except:
            self.session.rollback()
            return False


    def create_ticket(self, title: str, description: str, created_by: int) -> bool:
        """Création d'un Ticket"""
        user = self.session.query(User).filter_by(user_id=created_by).first()
        if not user:
            logging.error(f"L'utilisateur {created_by} n'existe pas.")
            return False

        try:
            new_ticket = Ticket(title=title, description=description, created_by=created_by, status="ouvert")
            self.session.add(new_ticket)
            self.session.commit()
            logging.info(f"Ticket '{title}' créé avec succès.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur lors de la création du ticket : {e}")
            return False

    def add_comment(self, ticket_id: int, user_id: int, comment: str) -> bool:
        """Ajoute un commentaire à un ticket."""
        ticket = self.session.query(Ticket).get(ticket_id)
        user = self.session.query(User).get(user_id)

        if not ticket or not user:
            logging.error("Ticket ou utilisateur inexistant.")
            return False

        try:
            self.session.add(TicketComment(ticket_id=ticket_id, user_id=user_id, comment=comment))
            self.session.commit()
            logging.info("Commentaire ajouté.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur lors de l'ajout du commentaire : {e}")
            return False

    def get_tickets_by_user(self, user_id: int):
        """Récupère tous les tickets d'un utilisateur avec les informations essentielles."""
        return self.session.query(Ticket.ticket_id, Ticket.title, Ticket.status, Ticket.created_at) \
            .filter_by(created_by=user_id).all()

    def get_open_tickets(self):
        """Récupère les tickets avec le statut 'ouvert' ou 'en cours'."""
        return self.session.query(Ticket.ticket_id, Ticket.title, Ticket.status, Ticket.created_at) \
            .filter(Ticket.status.in_(["ouvert", "en cours"])).all()

    def get_closed_tickets(self):
        """Récupère les tickets fermés."""
        return self.session.query(Ticket.ticket_id, Ticket.title, Ticket.status, Ticket.created_at) \
            .filter_by(status="fermé").all()

    def trier_ticket(self):
        """Récupère tous les tickets triés par date de création (du plus récent au plus ancien)."""
        return self.session.query(Ticket).order_by(Ticket.created_at.desc()).all()

    def user_inactive(self, user_id: int) -> bool:
        """Désactive un utilisateur."""
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if not user:
            logging.warning(f"L'utilisateur avec l'ID {user_id} n'existe pas.")
            return False

        user.is_active = False
        self.session.commit()
        logging.info(f"Utilisateur {user.username} désactivé.")
        return True

    def user_active(self, user_id: int) -> bool:
        """Vérifie si un utilisateur est actif."""
        user = self.session.query(User).filter_by(user_id=user_id).first()
        return user.is_active if user else False

    def search_tickets_by_keyword(self, keyword: str):
        """Rechercher les tickets par mot-clé dans toute la base de données."""
        return self.session.query(Ticket.ticket_id, Ticket.title, Ticket.description, Ticket.status, Ticket.created_at) \
            .filter((Ticket.title.ilike(f'%{keyword}%')) | (Ticket.description.ilike(f'%{keyword}%')) | (Ticket.status.ilike(f'%{keyword}%'))).all()