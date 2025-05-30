# Bot Discord Universel (Python)

Bienvenue dans le **Bot Discord Universel** !  
Ce bot est conçu pour être simple, polyvalent et facilement personnalisable afin de répondre à la plupart des besoins d’un serveur Discord, écrit en Python avec `discord.py`.

---

## Fonctionnalités principales

- Gestion des commandes simples et modulables  
- Commandes de modération (kick, ban, mute)  
- Commandes fun (ping, avatar, lancer de dés)  
- Système de logs  
- Réponses automatisées  
- Support multi-langues (optionnel)  
- Configuration facile via fichier `.env`

---

## Installation

1. **Cloner le dépôt**  
```bash
git clone https://github.com/tonutilisateur/discord-bot-universel.git
cd discord-bot-universel
````

2. **Créer un environnement virtuel (optionnel mais recommandé)**

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Créer un fichier `.env`** avec les variables suivantes :

```env
DISCORD_TOKEN=ton_token_de_bot_ici
PREFIX=!
```

5. **Lancer le bot**

```bash
python bot.py
```

---

## Utilisation

### Commandes basiques

| Commande                 | Description                                    |
| ------------------------ | ---------------------------------------------- |
| `!ping`                  | Teste la latence du bot                        |
| `!avatar [@utilisateur]` | Affiche l’avatar d’un utilisateur              |
| `!kick @utilisateur`     | Expulse un utilisateur du serveur (modération) |
| `!ban @utilisateur`      | Bannit un utilisateur (modération)             |
| `!mute @utilisateur`     | Rend un utilisateur muet (modération)          |

---

## Personnalisation

* Modifie le préfixe de commande dans le fichier `.env`
* Ajoute ou modifie les commandes dans le dossier `commands/` (ou directement dans `bot.py`)
* Configure les permissions dans le code pour restreindre certaines commandes aux rôles spécifiques

---

## Contribution

Les contributions sont les bienvenues !
N’hésitez pas à ouvrir une issue ou une pull request.

---

## Licence

MIT License © TonNom

---

## Contact

Pour toute question, contacte-moi sur Discord : `wssqdd (1901)`

