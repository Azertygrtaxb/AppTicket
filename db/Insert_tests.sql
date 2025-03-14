USE TicketsSupport;

INSERT INTO Users (username, hashpassword, email, role, phone_number) 
VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin_glpi@example.com', 'admin', '7392518476');

INSERT INTO Users (username, hashpassword, email, role, phone_number) VALUES
('user1', 'e10adc3949ba59abbe56e057f20f883e', 'user1@example.com', 'user', '1234567890'),
('tech1', 'e10adc3949ba59abbe56e057f20f883e', 'tech1@example.com', 'technician', '0987654321');

INSERT INTO categories (name, description) VALUES
('Probleme acces', 'Difficulte pour se connecter a GLPI'),
('Materiel IT', 'Probleme avec un equipement informatique');

INSERT INTO tickets (title, description, status, priority, category_id, created_by, assigned_to) VALUES
('Connexion impossible', 'Mot de passe refuse sur GLPI.', 'ouvert', 'moyenne', 1, 1, 2),
('PC ne demarre pas', 'Aucun signal en appuyant sur le bouton.', 'ouvert', 'elevee', 2, 1, NULL);

INSERT INTO ticket_comments (ticket_id, user_id, comment) VALUES
(1, 2, 'Avez-vous essaye de reinitialiser votre mot de passe ?'),
(1, 1, 'Le probleme semble venir du compte utilisateur.'),
(2, 2, 'Je vais verifier l alimentation du PC.'),
(2, 1, 'Avez-vous essaye un autre chargeur ?');

INSERT INTO notifications (user_id, ticket_id, message) VALUES
(1, 1, 'Votre probleme de connexion GLPI est en cours.'),
(2, 2, 'Un technicien a repondu a votre ticket.');

INSERT INTO knowledge_base (title, content, keyword, category_id, source_ticket_id) VALUES
('Connexion GLPI', 'Verifier les identifiants et essayer de reinitialiser.', 'connexion, GLPI, mot de passe', 1, 1),
('PC qui ne demarre pas', 'Verifier le chargeur et essayer un autre adaptateur.', 'ordinateur, demarrage, alimentation', 2, 2);

INSERT INTO ticket_dependencies (parent_ticket_id, child_ticket_id) VALUES
(1, 2);
