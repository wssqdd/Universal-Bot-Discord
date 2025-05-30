# Bot Discord - Commandes Utiles et Modération

Ce bot Discord propose un ensemble de commandes pratiques pour la gestion de serveur, la modération, et la récupération d'informations utiles sur les utilisateurs ou le serveur.

---

## Commandes disponibles

### Informations

| Commande | Description |
|---------|-------------|
| `!member` | Affiche le nombre de membres du serveur. |
| `!serveurinfo` | Affiche les informations du serveur. |
| `!userinfo [membre]` | Affiche les informations sur un membre. |
| `!stat` | Affiche les statistiques du serveur. |
| `!vc` | Affiche le nombre de membres actuellement en vocal. |
| `!ping` | Affiche la latence (ping) du bot. |
| `!alladmin` | Affiche la liste des administrateurs du serveur. |

### Modération

| Commande | Description |
|---------|-------------|
| `!clear [nombre]` | Supprime un nombre défini de messages dans un salon. |
| `!nuke` | Réinitialise un salon (supprime et recrée). |
| `!lock` | Verrouille un salon pour les membres. |
| `!unlock` | Déverrouille un salon pour les membres. |
| `!add_role [rôle] [utilisateur]` | Attribue un rôle à un membre. |
| `!remove_role [rôle] [utilisateur]` | Retire un rôle à un membre. |
| `!setup_logs` | Configure le système de logs du serveur. |

### Divers / Utilitaires

| Commande | Description |
|---------|-------------|
| `!snipe` | Affiche le dernier message supprimé. |
| `!sondage [question]` | Lance un sondage avec des réactions. |
| `!say [message]` | Le bot répète le message donné. |
| `!prefix [nouveau préfixe]` | Change le préfixe du bot. |
| `!help` | Affiche la liste des commandes. |

> Le préfixe utilisé peut être personnalisé dynamiquement via `config.json`.

---

## Exemple de config.json

```json
{
  "prefix": "!",
  "color_embed": 3447003
}
````

---

## Installation

1. Clonez ce dépôt :

   ```bash
   git clone https://github.com/votre-utilisateur/nom-du-repo.git
   ```

2. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

3. Lancez le bot :

   ```bash
   python bot.py
   ```

---

## Auteurs

* Développé par 1901 (wssqdd)

---

## Licence

Ce projet est sous licence MIT. Libre à vous de l'utiliser et de le modifier.
