import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import unittest
import uuid
from sqlalchemy import text
from app.utils.mysqlconnector import MySqlConnector
from app.models import User, Ticket

# Permet d'ajouter le répertoire parent au chemin d'import


class TestMysqlConnector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connector = MySqlConnector("51.75.25.241", "TicketsSupport", "root", "rootpassword")
        cls.connector.create_tables()
        cls.username = "test_user"
        # Création d'un utilisateur de test s'il n'existe pas
        if not cls.connector.user_exist(cls.username):
            cls.connector.add_user(cls.username, "hashed_password", "test_user@example.com", "user", "1234567890")
        # Rendre l'utilisateur actif
        cls.user = cls.connector.session.query(User).filter_by(username=cls.username).first()
        cls.connector.session.query(User).filter_by(user_id=cls.user.user_id).update({"is_active": True})
        cls.connector.session.commit()

    # Tests sur les utilisateurs
    def test_user_exists(self):
        self.assertTrue(self.connector.user_exist(self.username))

    def test_user_not_exists(self):
        self.assertFalse(self.connector.user_exist("fake_user"))

    def test_get_user_hash(self):
        self.assertEqual(self.connector.get_user_hash(self.username), "hashed_password")

    def test_add_user(self):
        new_username = f"user_{uuid.uuid4().hex[:6]}"
        new_email = f"{new_username}@example.com"
        success = self.connector.add_user(new_username, "hashed_password", new_email, "user", "1234567890")
        self.assertTrue(success)

    # Tests sur la création de ticket
    def test_create_ticket(self):
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        success = self.connector.create_ticket("Connexion perdue", "Problème de connexion", user.user_id)
        self.assertTrue(success)

    # Récupération de tickets
    def test_get_tickets_by_user(self):
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        tickets = self.connector.get_tickets_by_user(user.user_id)
        self.assertIsInstance(tickets, list)

    def test_get_ticket_summary(self):
        tickets = self.connector.get_ticket_summary()
        self.assertGreater(len(tickets), 0)
        # Vérifie le nombre de champs retournés (dans mysqlconnector, il y en a 10)
        self.assertEqual(len(tickets[0]), 10)

    def test_search_tickets_by_keyword(self):
        keyword = "Connexion perdue"
        tickets = self.connector.search_tickets_by_keyword(keyword)
        self.assertGreater(len(tickets), 0)
        # Vérifie que le mot-clé se trouve dans le titre, la description ou le statut
        self.assertTrue(any(keyword.lower() in str(t[1:4]).lower() for t in tickets))

    def test_get_open_tickets(self):
        tickets = self.connector.get_open_tickets()
        # Index 2 correspond au statut
        self.assertTrue(all(t[2] in ["ouvert", "en cours"] for t in tickets))

    def test_get_closed_tickets(self):
        tickets = self.connector.get_closed_tickets()
        self.assertTrue(all(ticket[2] == "ferme" for ticket in tickets))


    def test_sort_tickets_by_date(self):
        tickets = self.connector.trier_ticket()
        for i in range(len(tickets) - 1):
            self.assertGreaterEqual(tickets[i].created_at, tickets[i + 1].created_at)

    # Tests sur l'activation / désactivation d'utilisateur
    def test_user_active(self):
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        self.assertTrue(self.connector.user_active(user.user_id))

    def test_user_inactive(self):
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        self.connector.user_inactive(user.user_id)
        self.assertFalse(self.connector.user_active(user.user_id))

    # Test d'ajout de commentaire
    def test_add_comment(self):
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        ticket = self.connector.session.query(Ticket).first()
        success = self.connector.add_comment(ticket.ticket_id, user.user_id, "Commentaire de test.")
        self.assertTrue(success)

    # Vérification de la création des tables
    def test_create_tables(self):
        self.connector.create_tables()
        self.assertTrue(True)

    # Vérification de la fermeture de la connexion
    def test_close(self):
        self.connector.close()
        self.assertTrue(True)

    # Vérification de la récupération de l'ID utilisateur
    def test_find_user_id(self):
        user_id = self.connector.find_user_id(self.username)
        self.assertIsNotNone(user_id)

    # Nouveaux tests pour les fonctions ajoutées

    def test_get_all_users(self):
        users = self.connector.get_all_users()
        self.assertTrue(len(users) > 0)

    def test_update_role_users(self):
        new_role = "admin"
        success = self.connector.update_user_role(self.username, new_role)
        self.assertTrue(success)




        

    def test_close_ticket(self):
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        new_ticket = Ticket(title="Ticket à fermer", description="Description", created_by=user.user_id, status="ouvert")
        self.connector.session.add(new_ticket)
        self.connector.session.commit()
        tid = new_ticket.ticket_id

        success = self.connector.close_ticket(tid)
        self.assertTrue(success)

        closed_ticket = self.connector.session.query(Ticket).get(tid)
        self.assertEqual(closed_ticket.status, "ferme")

    def test_search_knowledge_base(self):
        # Par défaut, il n'y a pas d'articles insérés, donc la liste devrait être vide
        results = self.connector.search_knowledge_base("test")
        self.assertEqual(len(results), 0)

    def test_assign_and_remove_user_from_ticket(self):
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        new_ticket = Ticket(title="Ticket assignation", description="Desc", created_by=user.user_id, status="ouvert")
        self.connector.session.add(new_ticket)
        self.connector.session.commit()
        tid = new_ticket.ticket_id

        # Assignation
        success_assign = self.connector.assign_user_to_ticket(tid, user.user_id)
        self.assertTrue(success_assign)
        assigned_user = self.connector.get_assigned_user(tid)
        self.assertIsNotNone(assigned_user)
        self.assertEqual(assigned_user.user_id, user.user_id)

        # Suppression de l'assignation
        success_remove = self.connector.remove_assigned_user_from_ticket(tid)
        self.assertTrue(success_remove)
        assigned_user_after = self.connector.get_assigned_user(tid)
        self.assertIsNone(assigned_user_after)

    @classmethod
    def tearDownClass(cls):
        # Nettoyage de la base après les tests
        cls.connector.session.execute(text(f"DELETE FROM Users WHERE username = '{cls.username}'"))
        cls.connector.close()

if __name__ == '__main__':
    unittest.main()