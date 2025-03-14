import os
import sys

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import uuid
from sqlalchemy.engine.result import Row
from sqlalchemy import text
from app.utils.mysqlconnector import MySqlConnector
from app.models import User, Ticket, Category


class TestMysqlConnector(unittest.TestCase):
    """Tests unitaires pour vérifier les fonctionnalités de la base de données."""

    @classmethod
    def setUpClass(cls):
        """Connexion à la base et création d'un utilisateur test."""
        cls.connector = MySqlConnector("51.75.25.241", "TicketsSupport", "root", "rootpassword")
        cls.connector.create_tables()
        cls.username = "test_user"
        
        if not cls.connector.user_exist(cls.username):
            cls.connector.add_user(cls.username, "hashed_password", "test_user@example.com", "user", "1234567890")
        
        # S'assurer que l'utilisateur est actif au début des tests
        cls.user = cls.connector.session.query(User).filter_by(username=cls.username).first()
        cls.connector.session.query(User).filter_by(user_id=cls.user.user_id).update({"is_active": True})
        cls.connector.session.commit()

    #  Test de la gestion des utilisateurs
    def test_user_exists(self):
        """Vérifie que l'utilisateur test existe."""
        self.assertTrue(self.connector.user_exist(self.username))

    def test_user_not_exists(self):
        """Vérifie qu'un utilisateur inexistant est bien détecté."""
        self.assertFalse(self.connector.user_exist("fake_user"))

    def test_get_user_hash(self):
        """Vérifie la récupération du hash du mot de passe."""
        self.assertEqual(self.connector.get_user_hash(self.username), "hashed_password")

    def test_add_user(self):
        """Teste l'ajout d'un nouvel utilisateur."""
        new_username = f"user_{uuid.uuid4().hex[:6]}"
        new_email = f"{new_username}@example.com"
        success = self.connector.add_user(new_username, "hashed_password", new_email, "user", "1234567890")
        self.assertTrue(success)

    #  Test de création de ticket
    def test_create_ticket(self):
        """Crée un ticket pour un utilisateur existant."""
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        success = self.connector.create_ticket("Connexion perdue", "Problème de connexion", user.user_id)
        self.assertTrue(success)

    #  Test de récupération des tickets
    def test_get_tickets_by_user(self):
        """Récupère les tickets d'un utilisateur."""
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        tickets = self.connector.get_tickets_by_user(user.user_id)
        self.assertTrue(isinstance(tickets, list))

    

    def test_get_ticket_summary(self):
        """Vérifie que la fonction retourne uniquement les informations essentielles des tickets."""
        tickets = self.connector.get_ticket_summary()

        self.assertGreater(len(tickets), 0)  # Vérifie qu'il y a au moins 1 ticket
        for ticket in tickets:
            self.assertEqual(len(ticket), 5)  # Vérifie qu'il y a 5 éléments par ticket

    def test_search_tickets_by_keyword(self):
        """Teste la recherche de tickets par mot-clé dans toute la base de données."""
        keyword = "Connexion perdue"  # Mot-clé à rechercher

        # Recherche par mot-clé dans toute la base de données
        tickets = self.connector.search_tickets_by_keyword(keyword)

        # Vérifie que le mot-clé est présent dans l'une des colonnes (titre, description, ou statut)
        self.assertGreater(len(tickets), 0)
        self.assertTrue(any(keyword.lower() in str(ticket[1:4]).lower() for ticket in tickets))

    def test_get_open_tickets(self):
        """Récupère les tickets ouverts/en cours."""
        tickets = self.connector.get_open_tickets()
        self.assertTrue(all(ticket[2] in ["ouvert", "en cours"] for ticket in tickets))

    def test_get_closed_tickets(self):
        """Récupère les tickets fermés."""
        tickets = self.connector.get_closed_tickets()
        self.assertTrue(all(ticket[2] == "fermé" for ticket in tickets))

    #  Test de tri des tickets
    def test_sort_tickets_by_date(self):
        """Vérifie que les tickets sont triés du plus récent au plus ancien."""
        tickets = self.connector.trier_ticket()
        for i in range(len(tickets) - 1):
            self.assertGreaterEqual(tickets[i].created_at, tickets[i + 1].created_at, "Les tickets ne sont pas triés correctement")

    #  Test de la gestion de l'état utilisateur (activation/inactivation)
    def test_user_active(self):
        """Teste la vérification si un utilisateur est actif."""
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        self.assertTrue(self.connector.user_active(user.user_id))

    def test_user_inactive(self):
        """Teste la désactivation d'un utilisateur."""
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        self.connector.user_inactive(user.user_id)
        self.assertFalse(self.connector.user_active(user.user_id))

    #  Test d'ajout de commentaire
    def test_add_comment(self):
        """Vérifie qu'on peut ajouter un commentaire à un ticket."""
        user = self.connector.session.query(User).filter_by(username=self.username).first()
        ticket = self.connector.session.query(Ticket).first()
        success = self.connector.add_comment(ticket.ticket_id, user.user_id, "Ceci est un commentaire de test.")
        self.assertTrue(success)

    # Tests manquants ajoutés :
    def test_create_tables(self):
        """Vérifie que les tables sont créées correctement."""
        self.connector.create_tables()  # Si ça fonctionne sans exception, le test passe
        self.assertTrue(True)

    def test_close(self):
        """Vérifie que la connexion est bien fermée."""
        self.connector.close()  # Si ça fonctionne sans exception, le test passe
        self.assertTrue(True)

    def test_find_user_id(self):
        """Vérifie que l'ID de l'utilisateur est récupéré correctement."""
        user_id = self.connector.find_user_id(self.username)
        self.assertIsNotNone(user_id)  # L'ID ne doit pas être None

    @classmethod
    def tearDownClass(cls):
        """Nettoie la base après les tests."""
        cls.connector.session.execute(text(f"DELETE FROM Users WHERE username = '{cls.username}'"))
        cls.connector.close()

if __name__ == '__main__':
    unittest.main()