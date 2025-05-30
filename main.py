import discord
from discord.ext import commands
from discord.ui import Button, View
import logging
import re
import asyncio
from collections import defaultdict
from datetime import datetime, timezone
import random
import json
import requests
import aiohttp
import os
import re
import time
from collections import defaultdict
from datetime import timedelta


with open("config.json", "r") as f:
    config = json.load(f)

BLACKLIST_FILE = "blacklist.json"
def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "w") as f:
            json.dump({"blacklisted_users": []}, f)

    with open(BLACKLIST_FILE, "r") as f:
        data = json.load(f)
        if isinstance(data, dict):
            return data.get("blacklisted_users", [])
        else:
            return []

    
def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump({"blacklisted_users": blacklist}, f, indent=4)


intents = discord.Intents.all()
async def get_prefix(bot, message):
    with open("config.json", "r") as f:
        data = json.load(f)
    return data["prefix"]

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)


status_map = {
    "online": discord.Status.online,
    "idle": discord.Status.idle,
    "dnd": discord.Status.dnd,
    "invisible": discord.Status.invisible
}



activity_type_map = {
    "playing": discord.Game,
    "watching": lambda name: discord.Activity(type=discord.ActivityType.watching, name=name),
    "listening": lambda name: discord.Activity(type=discord.ActivityType.listening, name=name),
    "streaming": lambda name: discord.Streaming(name=name, url="https://twitch.tv/ton_stream")  # Modifier l'URL si besoin
}

deleted_messages = {}

async def noperm():
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.channel.send("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

@bot.event
async def on_ready():
    activity_type_raw = config.get("activity_type", "playing").lower()
    activity_func = activity_type_map.get(activity_type_raw, lambda name: discord.Game(name))

    activity_obj = activity_func(config.get("activity", "Playing something"))
    status = status_map.get(config.get("status", "online").lower(), discord.Status.online)

    await bot.change_presence(status=status, activity=activity_obj)
    print(f"Connecté en tant que {bot.user}, dévlopper par 1901 (wssqdd)")

@bot.command()
async def nuke(ctx):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.channel.send("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return
    channel = ctx.channel
    position_channel = channel.position
    name_channel = channel.name  
    await channel.delete()
    overwrites = channel.overwrites 
    new_channel = await ctx.guild.create_text_channel(
        name=name_channel, 
        position=position_channel,  
        overwrites=overwrites  
    )
    await new_channel.send(f"`Nuke by {ctx.author}`")

@bot.event
async def on_message_delete(message):
    deleted_messages[message.guild.id] = message

@bot.command()
async def snipe(ctx):
    # Vérifie si un message a été supprimé dans ce serveur
    if ctx.guild.id in deleted_messages:
        msg = deleted_messages[ctx.guild.id]
        embed = discord.Embed(
            title="Dernier message supprimé",
            description=msg.content,
            color=config.get("color_embed")
        )
        embed.set_author(name=msg.author.name, icon_url=msg.author.avatar.url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Aucun message supprimé récemment.")

@bot.command()
async def say(ctx, message: str):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.channel.send("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return
    await ctx.channel.send(f"{message}")

@bot.command()
async def prefix(ctx, prefix:str):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.channel.send("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return
    config["prefix"]=prefix
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    await ctx.send(f"Le préfixe a été changé en `{prefix}`")

@bot.command()
async def clear(ctx, amount:int):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.channel.send("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return
    await ctx.channel.purge(limit=amount+1)
    conf = await ctx.channel.send(f"`{amount}` on été supprimer")
    await asyncio.sleep(4)
    await conf.delete()

@bot.command()
async def lock(ctx):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.channel.send("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return  # important !

    channel = ctx.channel
    everyone = ctx.guild.default_role

    await channel.set_permissions(everyone, send_messages=False)
    await ctx.send(f"Le salon {channel.mention} a été verrouillé.")

@bot.command()
async def unlock(ctx):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.channel.send("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return  # important !

    channel = ctx.channel
    everyone = ctx.guild.default_role

    await channel.set_permissions(everyone, send_messages=True)
    await ctx.send(f"Le salon {channel.mention} a été déverouiller")


@bot.command()
async def add_role(ctx, role: discord.Role, *members: discord.Member):
    if not members:
        await ctx.send("Erreur : Vous devez mentionner au moins un membre.")
        return

    for member in members:
        try:
            await member.add_roles(role)
            await ctx.send(f"Le rôle `{role.name}` a été ajouté à {member.mention}.")
        except Exception as e:
            await ctx.send(f"Erreur lors de l'ajout du rôle `{role.name}` à {member.mention} : {str(e)}")

@bot.command()
async def remove_role(ctx, role: discord.Role, *members: discord.Member):
    if not members:
        await ctx.send("Erreur : Vous devez mentionner au moins un membre.")
        return

    for member in members:
        try:
            await member.remove_roles(role)
            await ctx.send(f"Le rôle `{role.name}` a été retiré de {member.mention}.")
        except Exception as e:
            await ctx.send(f"Erreur lors du retrait du rôle `{role.name}` de {member.mention} : {str(e)}")


@bot.command()
async def vc(ctx):
    # Nombre de membres en vocal sur le serveur
    voice_members = len([m for m in ctx.guild.members if m.voice and m.voice.channel])

    # Nombre total de membres sur le serveur
    total_members = ctx.guild.member_count

    # Répondre avec le message
    await ctx.reply(f"🎙️ | Membre en vocal: **{voice_members}** (**{total_members} membres**)")


@bot.command()
async def gay(ctx, member: discord.Member = None):
    # Si aucun membre n'est mentionné, prendre l'auteur de la commande
    if not member:
        member = ctx.author

    # Liste des réponses avec des emojis
    replies = [
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0% !", "🏳️‍🌈⬛⬛⬛⬛⬛⬛⬛⬛⬛ 10%", "🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛⬛⬛⬛⬛ 20% !",
        "🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛⬛⬛⬛ 30%", "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛⬛⬛ 40% !", "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛⬛ 50%",
        "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛ 60% !", "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛ 70%",
        "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛ 80%", "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛ 90%",
        "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈 100%",
        "🏳️‍🌈⬛⬛⬛⬛⬛⬛⬛⬛⬛ 10%", "🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛⬛⬛⬛⬛ 20% !", "🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛⬛⬛⬛ 30%",
        "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛⬛⬛ 40% !", "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛⬛ 50%", "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛⬛ 60% !",
        "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛⬛ 70%", "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛⬛ 80%",
        "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈⬛ 90%", "🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈 100%"
    ]
    
    # Choisir une réponse aléatoire
    result = random.choice(replies)

    # Créer l'embed
    embed = discord.Embed(
        description=f"Niveau de **Gay** de __<@{member.id}>__ !",
        color=config.get("color_embed")
    )
    embed.add_field(name="**Gay à :**", value=result)
    embed.set_footer(text=f"Demandé par : {ctx.author}")
    
    await ctx.reply(embed=embed)

@bot.command()
async def member(ctx):
    # Récupérer le nombre de membres du serveur
    member_count = ctx.guild.member_count

    # Répondre avec un message
    await ctx.reply(f"Nous sommes __**{member_count}**__ sur le __serveur__ !\n\n**Merci à vous !**")


@bot.command()
async def ping(ctx):
    # Obtenir le ping du WebSocket du bot
    ping = bot.latency * 1000  # Latency est en secondes, donc on multiplie par 1000 pour obtenir le ping en millisecondes

    # Créer l'embed
    embed = discord.Embed(
        description=f"🏓 Mon ping est de : **{ping:.2f}ms**",
        color=config.get("color_embed")
    )
    embed.set_footer(text=f"Demandé par : {ctx.author}", icon_url=ctx.author.avatar.url)

    # Répondre avec l'embed
    await ctx.reply(embed=embed)

@bot.command()
async def serveurinfo(ctx):
    # Récupérer les informations du serveur
    guild = ctx.guild

    # Vérification de l'ID du canal AFK
    afk = guild.afk_channel
    if afk:
        afk = f"<#{afk.id}>"
    else:
        afk = "Aucun"

    # Vérification de l'ID du canal des règles
    rules = guild.rules_channel
    if rules:
        rules = f"<#{rules.id}>"
    else:
        rules = "Aucun"

    # Récupérer la description du serveur
    desc = guild.description if guild.description else "Aucune"

    # Créer l'embed
    embed = discord.Embed(
        color=config.get("color_embed"),
        description=f"**Informations sur le serveur**\n"
                    f"**Nom** : {guild.name}\n"
                    f"**Propriétaire** : <@{guild.owner_id}>\n"
                    f"**ID** : {guild.id}\n"
                    f"**Description** : {desc}\n"
                    f"**Boosts** : {guild.premium_subscription_count} ({guild.premium_tier})\n"
                    f"**Date de création** : <t:{int(guild.created_at.timestamp())}:F>\n\n"
                    f"**Informations sur les stats**\n"
                    f"**Salons** : {len(guild.channels)}\n"
                    f"**Rôles** : {len(guild.roles)}\n"
                    f"**Emojis** : {len(guild.emojis)}\n"
                    f"**Membres** : {guild.member_count}\n\n"
                    f"**Informations sur les salons spéciaux**\n"
                    f"**AFK** : {afk}\n"
                    f"**Règles** : {rules}"
    )
    
    # Définir le timestamp avec la bonne syntaxe
    embed.timestamp = discord.utils.utcnow()

    # Ajouter un footer avec l'avatar de l'auteur
    embed.set_footer(text=f"Demandé par : {ctx.author}", icon_url=ctx.author.avatar.url)

    # Ajouter une miniature si le serveur a une icône
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    # Répondre avec l'embed
    await ctx.reply(embed=embed)

@bot.command()
async def stat(ctx):
    # Créer l'embed
    embed = discord.Embed(
        description=f"Le bot est présent sur : **__{len(bot.guilds)} serveurs !__**",
        color=config.get("color_embed")
    )
    
    # Répondre avec l'embed
    await ctx.reply(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    robot = "Oui" if member.bot else "Non"
    
    # Récupération des badges (flags publics)
    badges = ", ".join([flag.name for flag in member.public_flags.all()]) if member.public_flags else "Aucun"

    nickname = member.nick if member.nick else "Aucun"

    embed = discord.Embed(title=f"Informations sur {member}", color=config.get("color_embed"))
    embed.add_field(name="Informations sur l'utilisateur :", value=f"""
**Pseudo** : {member.name}
**Tag** : {member.discriminator}
**Robot** : {robot}
**Badges** : {badges}
**Date de création du compte** : <t:{int(member.created_at.timestamp())}:F>
""", inline=False)

    embed.add_field(name="Informations sur le serveur :", value=f"""
**Surnom** : {nickname}
**Date d'arrivée sur le serveur** : <t:{int(member.joined_at.timestamp())}:F>
""", inline=False)

    embed.set_footer(text=f"Demandé par : {ctx.author.name}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()

    await ctx.reply(embed=embed)

@bot.command()
async def alladmin(ctx):
    if ctx.author.guild_permissions.administrator:
        admins = [
            member for member in ctx.guild.members 
            if member.guild_permissions.administrator and not member.bot
        ]

        description = ""
        for i, admin in enumerate(admins, start=1):
            description += f"[{i}] - **{admin.name}** : *({admin.id})*\n\n"

        embed = discord.Embed(
            title="**Liste des Admins du serveur :**",
            description=description or "Aucun administrateur trouvé.",
            color=config.get("color_embed")
        )
        embed.set_footer(text=f"Demandé par : {ctx.author.name}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await ctx.reply(embed=embed)
    else:
        await ctx.reply("❌ Vous devez avoir la permission **Administrateur** pour utiliser cette commande.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sondage(ctx, *, question: str = None):
    await ctx.message.delete()

    if not question:
        return await ctx.send("Veuillez fournir une question !")

    embed = discord.Embed(
        title=question,
        description="**Oui :** ✅\n\n**Non :** ❌",
        color=config.get("color_embed")
    )
    embed.set_footer(text=f"Sondage par : {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    embed.timestamp = discord.utils.utcnow()

    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

@bot.command()
async def youtube(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("❌ Tu dois être dans un salon vocal.")

    channel = ctx.author.voice.channel

    url = f"https://discord.com/api/v10/channels/{channel.id}/invites"
    headers = {
        "Authorization": f"Bot {bot.http.token}",
        "Content-Type": "application/json"
    }
    json_data = {
        "max_age": 86400,
        "max_uses": 0,
        "target_application_id": "880218394199220334",  # YouTube Together
        "target_type": 2,
        "temporary": False,
        "validate": None
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as response:
            data = await response.json()
            if "code" not in data:
                return await ctx.send("❌ Impossible de créer l'invitation.")
            
            invite_url = f"https://discord.gg/{data['code']}"
            embed = discord.Embed(
                title="🎬 YouTube Together",
                description=f"[Clique ici pour lancer l'activité !]({invite_url})",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)



@bot.command()
async def ask_away(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("❌ Tu dois être dans un salon vocal.")

    channel = ctx.author.voice.channel

    url = f"https://discord.com/api/v10/channels/{channel.id}/invites"
    headers = {
        "Authorization": f"Bot {bot.http.token}",
        "Content-Type": "application/json"
    }
    json_data = {
        "max_age": 86400,
        "max_uses": 0,
        "target_application_id": "976052223358406656",  # Ask Away
        "target_type": 2,
        "temporary": False,
        "validate": None
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as response:
            data = await response.json()
            if "code" not in data:
                return await ctx.send("❌ Impossible de créer l'invitation.")

            invite_url = f"https://discord.gg/{data['code']}"
            embed = discord.Embed(
                title="🎤 Ask Away",
                description=f"[Clique ici pour lancer l'activité !]({invite_url})",
                color=discord.Color.dark_purple()
            )
            await ctx.send(embed=embed)



@bot.command()
async def spellcast(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("❌ Tu dois être dans un salon vocal.")

    channel = ctx.author.voice.channel

    url = f"https://discord.com/api/v10/channels/{channel.id}/invites"
    headers = {
        "Authorization": f"Bot {bot.http.token}",
        "Content-Type": "application/json"
    }
    json_data = {
        "max_age": 86400,
        "max_uses": 0,
        "target_application_id": "852509694341283871",  # SpellCast
        "target_type": 2,
        "temporary": False,
        "validate": None
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as response:
            data = await response.json()
            if "code" not in data:
                return await ctx.send("❌ Impossible de créer l'invitation.")

            invite_url = f"https://discord.gg/{data['code']}"
            embed = discord.Embed(
                title="🧙 SpellCast",
                description=f"[Clique ici pour lancer l'activité !]({invite_url})",
                color=discord.Color.dark_blue()
            )
            await ctx.send(embed=embed)



@bot.command()
async def word_snack(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("❌ Tu dois être dans un salon vocal.")

    channel = ctx.author.voice.channel

    url = f"https://discord.com/api/v10/channels/{channel.id}/invites"
    headers = {
        "Authorization": f"Bot {bot.http.token}",
        "Content-Type": "application/json"
    }
    json_data = {
        "max_age": 86400,
        "max_uses": 0,
        "target_application_id": "879863976006127627",  # Word Snack ID
        "target_type": 2,
        "temporary": False,
        "validate": None
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as response:
            data = await response.json()
            if "code" not in data:
                return await ctx.send("❌ Impossible de créer l'invitation.")

            invite_url = f"https://discord.gg/{data['code']}"
            embed = discord.Embed(
                title="📝 Word Snacks",
                description=f"[Clique ici pour lancer l'activité !]({invite_url})",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


@bot.command()
async def help(ctx):
    # Récupérer dynamiquement le préfixe actuel
    with open("config.json", "r") as f:
        data = json.load(f)
    prefix = data["prefix"]

    embed = discord.Embed(
        title="Listes des commandes disponibles",
        description="Voici quelques commandes que vous pouvez utiliser avec ce bot :",
        color=config.get("color_embed")
    )
    
    embed.add_field(name=" ", value=f"""
**`{prefix}member`**
Affiche le nombre de membres présents sur le serveur

**`{prefix}snipe`**
Affiche le dernier message supprimé

**`{prefix}nuke`**
Réinitialise le salon choisi

**`{prefix}add_role [rôle] [utilisateur]`**
Ajoute un rôle à un utilisateur

**`{prefix}remove_role [rôle] [utilisateur]`**
Supprime un rôle d’un utilisateur

**`{prefix}lock`**
Verrouille un salon aux membres

**`{prefix}unlock`**
Déverrouille un salon aux membres

**`{prefix}serveurinfo`**
Affiche les informations du serveur

**`{prefix}userinfo [membre]`**
Affiche les informations d’un membre

**`{prefix}stat`**
Affiche les stats du serveur

**`{prefix}vc`**
Affiche le nombre de personnes en vocal

**`{prefix}sondage [question]`**
Lance un sondage

**`{prefix}alladmin`**
Affiche une liste des admin du serveurs

**`{prefix}ping`**
Affiche la latence du bot (ping)

**`{prefix}clear [amount]`**
Supprime un nombre de messages renseigner

**`{prefix}say [message]`**
Le bot envoie le messages qui suis la commandes

**`{prefix}prefix [prefix]`**
Change le préfixe du bot

**`{prefix}setup_logs`**
Setup les logs sur le serveur
""", inline=False)
    
    embed.set_footer(text=f"Préfix actuel: {prefix} | Demandé par {ctx.author}")
    
    await ctx.send(embed=embed)



LOG_CATEGORY_NAME = "Logs"
LOG_CHANNELS = {
    "message": "📁 · log-messages",
    "vocal": "📁 ·log-vocal",
    "boost": "📁 ·log-boost",
    "roles": "📁 ·log-roles",
    "blacklist": "📁 ·log-blacklist",
    "join_leave": "📁 ·log-join-leave"
}


log_channels_ids = {}  # Stocke les IDs pour accès rapide


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_logs(ctx):
    guild = ctx.guild

    # Créer la catégorie
    log_category = discord.utils.get(guild.categories, name=LOG_CATEGORY_NAME)
    if not log_category:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }
        log_category = await guild.create_category(LOG_CATEGORY_NAME, overwrites=overwrites)
        await ctx.send("Catégorie `Logs` créée.")

    # Créer les salons de logs avec permissions admin uniquement
    for key, channel_name in LOG_CHANNELS.items():
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if not channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
            # Donner l'accès aux rôles avec permission administrateur
            for role in guild.roles:
                if role.permissions.administrator:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True)

            new_channel = await guild.create_text_channel(channel_name, category=log_category, overwrites=overwrites)
            await ctx.send(f"Salon `{channel_name}` créé.")
            log_channels_ids[key] = new_channel.id
        else:
            log_channels_ids[key] = channel.id

    await ctx.send("Système de logs prêt avec accès restreint aux administrateurs !")

def make_embed(title, description):
    return discord.Embed(
        title=title,
        description=description,
        color=discord.Color.light_grey()
    )


def get_log_channel(guild, key):
    channel_id = log_channels_ids.get(key)
    if channel_id:
        return guild.get_channel(channel_id)
    return None

# ─────────────── LOG MESSAGE ───────────────

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    channel = get_log_channel(message.guild, "message")
    if channel:
        embed = make_embed("🗑️ Message supprimé",
            f"**Auteur :** {message.author.mention}\n"
            f"**Salon :** {message.channel.mention}\n"
            f"**Contenu :**\n```{message.content}```"
        )
        await channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    channel = get_log_channel(before.guild, "message")
    if channel:
        embed = make_embed("✏️ Message modifié",
            f"**Auteur :** {before.author.mention}\n"
            f"**Salon :** {before.channel.mention}\n"
            f"**Avant :**\n```{before.content}```\n"
            f"**Après :**\n```{after.content}```"
        )
        await channel.send(embed=embed)
# ─────────────── LOG VOCAL ───────────────

@bot.event
async def on_voice_state_update(member, before, after):
    channel = get_log_channel(member.guild, "vocal")
    if not channel:
        return

    if before.channel is None and after.channel is not None:
        embed = make_embed("🔊 Connexion vocale",
            f"{member.mention} est **entré** dans {after.channel.mention}")
        await channel.send(embed=embed)
    elif before.channel is not None and after.channel is None:
        embed = make_embed("🔇 Déconnexion vocale",
            f"{member.mention} est **sorti** de {before.channel.mention}")
        await channel.send(embed=embed)
    elif before.channel != after.channel:
        embed = make_embed("🔁 Changement de salon vocal",
            f"{member.mention} est passé de {before.channel.mention} à {after.channel.mention}")
        await channel.send(embed=embed)


# ─────────────── LOG BOOST ───────────────

@bot.event
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        channel = get_log_channel(after.guild, "boost")
        if channel:
            embed = make_embed("🚀 Boost serveur",
                f"{after.mention} a boosté le serveur !")
            await channel.send(embed=embed)


# ─────────────── LOG ROLES ───────────────

@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        channel = get_log_channel(after.guild, "roles")
        if channel:
            removed = [role.name for role in before.roles if role not in after.roles]
            added = [role.name for role in after.roles if role not in before.roles]
            content = ""
            if added:
                content += f"**Ajouté :** {', '.join(added)}\n"
            if removed:
                content += f"**Retiré :** {', '.join(removed)}\n"
            embed = make_embed("🎭 Mise à jour des rôles",
                f"{after.mention}\n{content}")
            await channel.send(embed=embed)

@bot.event
async def on_member_join(member):
    channel = get_log_channel(member.guild, "join_leave")
    if channel:
        embed = make_embed("✅ Nouveau membre",
            f"{member.mention} a rejoint le serveur.")
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = get_log_channel(member.guild, "join_leave")
    if channel:
        embed = make_embed("❌ Départ d'un membre",
            f"{member.mention} a quitté le serveur.")
        await channel.send(embed=embed)


blacklisted_users = load_blacklist()

@bot.command()
async def bl(ctx, id: int):
    blacklist = load_blacklist()

    if not ctx.author.guild_permissions.administrator:
        a = await ctx.reply("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    if id in blacklist:
        await ctx.reply("L'utilisateur est déjà blacklisté.")
        return

    ban_count = 0

    for guild in bot.guilds:
        member = guild.get_member(id)
        if member:
            try:
                await guild.ban(member, reason="Utilisateur blacklisté")
                ban_count += 1
            except discord.Forbidden:
                await ctx.send(f"Je n'ai pas la permission de bannir dans `{guild.name}`.")
            except discord.HTTPException:
                await ctx.send(f"Erreur lors du bannissement dans `{guild.name}`.")

    if ban_count == 0:
        await ctx.reply("Impossible de bannir l'utilisateur dans aucun serveur. Il n'a pas été blacklisté.")
    else:
        blacklist.append(id)
        save_blacklist(blacklist)

        log_channel = get_log_channel(ctx.guild, "blacklist")
        if log_channel:
            embed = make_embed("Utilisateur blacklisté",
            f"**ID :** `{id}`\n**Par :** {ctx.author.mention}\n**Serveurs bannis :** `{ban_count}`")
            await log_channel.send(embed=embed)


        await ctx.reply(f"L'utilisateur `{id}` a été blacklisté et banni de `{ban_count}` serveur(s).")


@bot.command()
async def unbl(ctx, id: int):

    if not ctx.author.guild_permissions.administrator:
        a = await ctx.reply("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    blacklist = load_blacklist()

    if id not in blacklist:
        await ctx.reply("L'utilisateur n'est pas dans la blacklist.")
        return

    blacklist.remove(id)
    save_blacklist(blacklist)

    unban_count = 0
    for guild in bot.guilds:
        try:
            async for entry in guild.bans():
                if entry.user.id == id:
                    await guild.unban(entry.user, reason="Retiré de la blacklist")
                    unban_count += 1
        except discord.Forbidden:
            await ctx.send(f"Pas la permission de débannir dans `{guild.name}`.")
        except discord.HTTPException:
            await ctx.send(f"Erreur lors du débannissement dans `{guild.name}`.")
    log_channel = get_log_channel(ctx.guild, "blacklist")
    if log_channel:
        embed = make_embed("✅ Utilisateur retiré de la blacklist",
        f"**ID :** `{id}`\n**Par :** {ctx.author.mention}\n**Serveurs débannis :** `{unban_count}`")
        await log_channel.send(embed=embed)

    await ctx.reply(f"L'utilisateur `{id}` a été retiré de la blacklist et débanni de `{unban_count}` serveur(s).")




@bot.event
async def on_member_join(member):
    blacklist = load_blacklist()
    if member.id in blacklist:
        try:
            await member.ban(reason="Utilisateur blacklisté (auto-ban)")
            print(f"Utilisateur {member.id} banni automatiquement de {member.guild.name}")
        except discord.Forbidden:
            print(f"Pas la permission de bannir {member.id} dans {member.guild.name}")
        except discord.HTTPException:
            print(f"Erreur HTTP en essayant de bannir {member.id} dans {member.guild.name}")



@bot.command(name="listbl")
async def listbl(ctx):

    if not ctx.author.guild_permissions.administrator:
        a = await ctx.reply("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    blacklist = load_blacklist()

    if not blacklist:
        await ctx.reply("📭 La blacklist est vide.")
        return

    lines = []
    for user_id in blacklist:
        user = bot.get_user(user_id)
        if not user:
            try:
                user = await bot.fetch_user(user_id)
            except discord.NotFound:
                name = "Inconnu"
            except discord.HTTPException:
                name = "Erreur API"
            else:
                name = f"{user.name}#{user.discriminator}"
        else:
            name = f"{user.name}#{user.discriminator}"

        lines.append(f"- `{user_id}` ({name})")

    formatted = "\n".join(lines)
    await ctx.reply(f"📄 **Utilisateurs blacklistés ({len(blacklist)}):**\n{formatted}")

@bot.command()
async def kick(ctx, membre: discord.Member = None, *, raison: str = "Aucune raison fournie"):

    if not ctx.author.guild_permissions.administrator:
        a = await ctx.reply("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    if membre is None:
        await ctx.reply("Merci de renseigner la personne à kick du serveur")
        return
    try:
        await membre.kick(reason=raison)
        await ctx.reply(f"Le membre `{membre}` à été kick du serveur")
    except discord.Forbidden:
        await ctx.reply("Je n'ai pas la permissions de kick la personne")
    except discord.HTTPException:
        ctx.reply("Une erreur est survenu lors du kick de la personne")

@bot.command()
async def ban(ctx, membre: discord.Member = None, *, raison: str = "Aucune raison fournie"):

    if not ctx.author.guild_permissions.administrator:
        a = await ctx.channel.send("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    if membre is None:
        await ctx.reply("Merci de renseigner la personne à ban du serveur")
        return
    try:
        await membre.ban(reason=raison)
        await ctx.reply(f"Le membre `{membre}` à été ban du serveur")
    except discord.Forbidden:
        await ctx.reply("Je n'ai pas la permissions de ban la personne")
    except discord.HTTPException:
        ctx.reply("Une erreur est survenu lors du ban de la personne")


    

@bot.command()
async def antilien(ctx, state: str):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.reply("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    state = state.lower()
    if state not in ["on", "off"]:
        return await ctx.reply("Utilisez `on` ou `off`.")

    with open("config.json", "r") as f:
        config = json.load(f)

    current = config.get("antilien", False)
    new = (state == "on")

    if current == new:
        return await ctx.reply(f"ℹL'antilien est déjà {'activé' if new else 'désactivé'}.")

    config["antilien"] = new
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    await ctx.reply(f"L'antilien a bien été {'activé' if new else 'désactivé'}.")



@bot.command()
async def antispam(ctx, mode: str = None, level: int = 1):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.reply("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    mode = mode.lower() if mode else None
    if mode not in ["on", "off"]:
        return await ctx.reply("Utilisez `.antispam on <niveau>` ou `.antispam off`.")

    with open("config.json", "r") as f:
        config = json.load(f)

    if mode == "on":
        if not (1 <= level <= 3):
            return await ctx.reply("Le niveau doit être entre 1 et 3.")
        config["antispam"] = level
        await ctx.reply(f"Antispam activé (niveau {level}).")
    else:
        config["antispam"] = 0
        await ctx.reply("Antispam désactivé.")

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)


user_message_times = defaultdict(list)
user_warnings = defaultdict(int)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    with open("config.json", "r") as f:
        config = json.load(f)

    level = config.get("antispam", 0)
    if level:
        settings = {
            1: {"interval": 10, "max_messages": 5},
            2: {"interval": 7, "max_messages": 4},
            3: {"interval": 5, "max_messages": 3}
        }.get(level, {"interval": 10, "max_messages": 5})

        now = time.time()
        user_id = message.author.id
        user_message_times[user_id].append(now)
        user_message_times[user_id] = [t for t in user_message_times[user_id] if now - t < settings["interval"]]

        if len(user_message_times[user_id]) > settings["max_messages"]:
            user_warnings[user_id] += 1
            await message.delete()

            if user_warnings[user_id] >= 3:
                try:
                    duration = timedelta(hours=1)
                    await message.author.timeout(duration, reason="Antispam : 3 avertissements")

                    await message.channel.send(
                        f"{message.author.mention} Tu as été mis en timeout pendant 1 heure pour spam.",
                        delete_after=5
                    )
                except Exception as e:
                    print(f"[ERREUR TIMEOUT] : {e}")
            else:
                await message.channel.send(
                    f"{message.author.mention} Merci de ne pas spammer ! (Avertissement {user_warnings[user_id]}/3)",
                    delete_after=5
                )
            return

    await bot.process_commands(message)




@bot.command()
async def antibot(ctx, state: str):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.reply("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    state = state.lower()
    if state not in ["on", "off"]:
        return await ctx.reply("Utilisez `on` ou `off`.")

    with open("config.json", "r") as f:
        config = json.load(f)

    current = config.get("antibot", False)
    if (state == "on" and current) or (state == "off" and not current):
        return await ctx.reply(f"L'antibot est déjà {'activé' if current else 'désactivé'}.")

    config["antibot"] = (state == "on")

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    await ctx.reply(f"L'antibot est maintenant {'activé' if state == 'on' else 'désactivé'}.")

@bot.command()
async def dmall(ctx, *, message: str):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.reply("Vous n'avez pas la permission d'effectuer cette commande.")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    await ctx.reply("Envoi des messages en cours...")

    for member in ctx.guild.members:
        if member.bot:
            continue  # On ignore les bots
        try:
            await member.send(message)
            await asyncio.sleep(1)  # Pour éviter le rate limit
        except Exception as e:
            print(f"Erreur d'envoi à {member}: {e}")
            try:
                await ctx.send(f"Erreur d'envoi à {member.display_name}")
            except:
                pass

@bot.event
async def on_member_join(member):
    with open("config.json", "r") as f:
        config = json.load(f)

    if config.get("antibot", False):
        if member.bot:
            try:
                await member.kick(reason="Antibot activé : tentative d'ajout d'un bot.")
                channel = discord.utils.get(member.guild.text_channels, name="📁-·log-join-leave")  # si tu veux log dans un salon
                if channel:
                    embed = make_embed(
                    "🛑 Bot expulsé automatiquement",
                    f"Le bot {member.mention} a été expulsé automatiquement en raison de la protection antibot activée."
                )
                await channel.send(embed=embed)
            except Exception as e:
                print(f"[ERREUR ANTIBOT] : {e}")


@bot.command()
async def antiinvitation(ctx, state: str):
    if not ctx.author.guild_permissions.administrator:
        a = await ctx.reply("Vous n'avez pas la permission d'effectuer cette commande")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await a.delete()
        return

    state = state.lower()
    if state not in ["on", "off"]:
        return await ctx.reply("Utilisez `on` ou `off`.")

    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    config["antiinvitation"] = (state == "on")

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    await ctx.reply(f"L'antiinvitation est maintenant {'activé' if state == 'on' else 'désactivé'}.")

    if state == "on":
        # Supprime toutes les invitations
        try:
            invites = await ctx.guild.invites()
            for invite in invites:
                await invite.delete()
        except Exception as e:
            print(f"[Erreur suppression d'invites] : {e}")

        # Bloque la création d'invitation
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(
                    ctx.guild.default_role,
                    create_instant_invite=False
                )
            except Exception as e:
                print(f"[Erreur permissions sur {channel.name}] : {e}")

    elif state == "off":
        # Réactive la création d'invitations
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(
                    ctx.guild.default_role,
                    create_instant_invite=None  # Réinitialise aux permissions par défaut
                )
            except Exception as e:
                print(f"[Erreur réactivation sur {channel.name}] : {e}")














token = config["token"]

bot.run(token=token)
