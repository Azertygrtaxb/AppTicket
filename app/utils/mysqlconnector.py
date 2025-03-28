import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Ticket, TicketComment, KnowledgeBase
from sqlalchemy import func
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MySqlConnector:
    def __init__(self, server, databaseName, databaseUser, databasePassword):
        self.DATABASE_URL = f"mysql+pymysql://{databaseUser}:{databasePassword}@{server}/{databaseName}"
        self.engine = create_engine(self.DATABASE_URL)
        self.session = sessionmaker(bind=self.engine)()

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        logging.info("Tables créées avec succès.")

    def close(self):
        self.session.close()
        logging.info("Connexion fermée.")

    def user_exist(self, username: str) -> bool:
        return self.session.query(User).filter_by(username=username).first() is not None

    def get_user_hash(self, username: str):
        user = self.session.query(User).filter_by(username=username).first()
        return user.hashpassword if user else None

    def find_user_id(self, username: str):
        user = self.session.query(User.user_id).filter_by(username=username).first()
        return user.user_id if user else None

    def add_user(self, username: str, hashed_password: str, email: str, role: str, phone_number: str) -> bool:
        if self.user_exist(username):
            logging.warning(f"L'utilisateur {username} existe déjà.")
            return False
        new_user = User(username=username, hashpassword=hashed_password, email=email, role=role, phone_number=phone_number)
        try:
            self.session.add(new_user)
            self.session.commit()
            logging.info(f"Utilisateur {username} ajouté.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur ajout utilisateur {username}: {e}")
            return False

    def get_ticket_summary(self):
        return self.session.query(
            Ticket.ticket_id,
            Ticket.title,
            Ticket.status,
            Ticket.created_at,
            Ticket.created_by,
            Ticket.description,
            Ticket.priority,
            Ticket.category_id,
            Ticket.updated_at,
            Ticket.assigned_to
        ).all()


    def get_tickets_by_user(self, user_id: int):
        return self.session.query(
            Ticket.ticket_id,
            Ticket.title,
            Ticket.status,
            Ticket.created_at
        ).filter_by(created_by=user_id).all()

    def get_open_tickets(self):
        return self.session.query(
            Ticket.ticket_id,
            Ticket.title,
            Ticket.status,
            Ticket.created_at
        ).filter(Ticket.status.in_(["ouvert", "en cours"])).all()

    def create_ticket(self, title: str, description: str, created_by: int) -> bool:
        if not self.session.get(User, created_by):
            logging.error(f"Utilisateur {created_by} non trouvé.")
            return False
        try:
            ticket = Ticket(title=title, description=description, created_by=created_by, status="ouvert")
            self.session.add(ticket)
            self.session.commit()
            logging.info(f"Ticket '{title}' créé.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur création ticket: {e}")
            return False

    def add_comment(self, ticket_id: int, user_id: int, comment: str) -> bool:
        if not (self.session.get(Ticket, ticket_id) and self.session.get(User, user_id)):
            logging.error("Ticket ou utilisateur inexistant.")
            return False
        try:
            self.session.add(TicketComment(ticket_id=ticket_id, user_id=user_id, comment=comment))
            self.session.commit()
            logging.info("Commentaire ajouté.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur ajout commentaire: {e}")
            return False

    def close_ticket(self, ticket_id: int) -> bool:
        ticket = self.session.get(Ticket, ticket_id)
        if not ticket:
            logging.error(f"Ticket {ticket_id} non trouvé.")
            return False
        try:
            ticket.status = "ferme"
            self.session.commit()
            logging.info(f"Ticket {ticket_id} clôturé.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur clôture ticket {ticket_id}: {e}")
            return False

    def update_user_info(self, username: str, hashed_password: str, email: str, phone_number: str) -> bool:
        user = self.session.query(User).filter_by(username=username).first()
        if not user:
            logging.info(f"Utilisateur {username} non trouvé.")
            return False
        try:
            user.hashpassword = hashed_password
            user.email = email
            user.phone_number = phone_number
            self.session.commit()
            logging.info(f"Infos de l'utilisateur {username} mises à jour.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur mise à jour utilisateur {username} : {e}")
            return False

    def update_user_role(self, username: str, new_role: str):
        user = self.session.query(User).filter_by(username=username).first()
        if user:
            user.role = new_role
            self.session.commit()
            logging.info(f"Rôle de {username} mis à jour en {new_role}.")
            return True
        logging.error(f"Utilisateur {username} non trouvé.")
        return False

    def get_all_users(self):
        return self.session.query(User).all()

    def get_closed_tickets(self):
        """Récupère tous les tickets fermés."""
        return self.session.query(
            Ticket.ticket_id,
            Ticket.title,
            Ticket.status,
            Ticket.created_at
        ).filter_by(status="fermé").all()

    def trier_ticket(self):
        """Trie les tickets par date de création (du plus récent au plus ancien)."""
        return self.session.query(Ticket).order_by(Ticket.created_at.desc()).all()

    def return_number_of_tickets(self):
        """Récupère le nombre de tickets par statut (ouvert, en cours, resolu, ferme).
        Retourne un dictionnaire : {'ouvert': x, 'en cours': y, ...}"""
        results = self.session.query(
            Ticket.status, func.count(Ticket.ticket_id)
        ).group_by(Ticket.status).all()

        return {status: count for status, count in results}


    def user_active(self, user_id: int) -> bool:
        """Vérifie si un utilisateur est actif."""
        user = self.session.query(User).filter_by(user_id=user_id).first()
        return user.is_active if user else False

    def user_inactive(self, user_id: int) -> bool:
        """Désactive un utilisateur (le met inactif)."""
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if not user:
            logging.warning(f"Utilisateur {user_id} non trouvé.")
            return False
        user.is_active = False
        self.session.commit()
        logging.info(f"Utilisateur {user.username} désactivé.")
        return True

    def search_tickets_by_keyword(self, keyword: str):
        """Recherche les tickets contenant un mot-clé dans le titre, la description ou le statut."""
        p = f'%{keyword}%'
        cond = Ticket.title.ilike(p) | Ticket.description.ilike(p) | Ticket.status.ilike(p)

        return self.session.query(
            Ticket.ticket_id,
            Ticket.title,
            Ticket.description,
            Ticket.status,
            Ticket.created_at
        ).filter(cond).all()

    def search_knowledge_base(self, keyword: str):
        """
        Recherche dans la base de connaissances les articles contenant le mot-clé.
        Cherche dans le titre, le contenu et les mots-clés associés.
        """
        p = f'%{keyword}%'
        cond = KnowledgeBase.title.ilike(p) | KnowledgeBase.content.ilike(p) | KnowledgeBase.keyword.ilike(p)

        return self.session.query(
            KnowledgeBase.article_id,
            KnowledgeBase.title,
            KnowledgeBase.content,
            KnowledgeBase.keyword,
            KnowledgeBase.created_at
        ).filter(cond).all()

    def get_assigned_user(self, ticket_id: int):
        ticket = self.session.get(Ticket, ticket_id)
        if not ticket:
            logging.error(f"Ticket {ticket_id} non trouvé.")
            return None
        if ticket.assigned_to is None:
            logging.info(f"Aucun utilisateur assigné pour le ticket {ticket_id}.")
            return None
        return ticket.User

    def assign_user_to_ticket(self, ticket_id: int, user_id: int) -> bool:
        ticket = self.session.get(Ticket, ticket_id)
        user = self.session.get(User, user_id)
        if not ticket or not user:
            logging.error("Ticket ou utilisateur non trouvé.")
            return False
        try:
            ticket.assigned_to = user_id
            self.session.commit()
            logging.info(f"Utilisateur {user.username} assigné au ticket {ticket_id}.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur assignation ticket {ticket_id}: {e}")
            return False

    def remove_assigned_user_from_ticket(self, ticket_id: int) -> bool:
        ticket = self.session.get(Ticket, ticket_id)
        if not ticket:
            logging.error(f"Ticket {ticket_id} non trouvé.")
            return False
        try:
            ticket.assigned_to = None
            self.session.commit()
            logging.info(f"Assignation supprimée pour le ticket {ticket_id}.")
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erreur suppression assignation ticket {ticket_id}: {e}")
            return False
