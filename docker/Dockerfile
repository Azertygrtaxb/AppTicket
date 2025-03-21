# Utilise une image officielle de Python
FROM python:latest

# Définit le répertoire de travail
WORKDIR /app

# Copier les fichiers à partir du contexte de build fourni par docker-compose
COPY requirements.txt requirements.txt
COPY app/ app/
COPY run.py run.py

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port 5000 pour Flask
EXPOSE 5000

# Commande pour lancer l'application
CMD ["python", "run.py"]