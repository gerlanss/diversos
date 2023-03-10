from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

# API Key da API de Futebol
API_KEY = 'cb174b53992da29dc4d66044bc7d8ccb53d202a219a830b19e2c409b30fda6a8'
# Token do Bot do Telegram
BOT_TOKEN = '6184223447:AAE8H4v3p4oMRukQmknBDGZ-FNHtzze51gQ'

# Função para iniciar o bot
def start(update: Update, context: CallbackContext) -> None:
    # Envia mensagem de confirmação que o bot foi iniciado
    update.message.reply_text('Bot iniciado. Procurando por jogos ao vivo com alta probabilidade de ter 2 escanteios a partir do minuto 45 e a partir do minuto 85.')
    # Envia mensagem de confirmação que o bot foi iniciado para o chat
    context.bot.send_message(chat_id=update.effective_chat.id, text='Bot iniciado.')
# Função para parar o bot
def stop(update: Update, context: CallbackContext) -> None:
    # Envia mensagem de confirmação que o bot foi parado
    update.message.reply_text('Bot parado.')
    # Envia mensagem de confirmação que o bot foi parado para o chat
    context.bot.send_message(chat_id=update.effective_chat.id, text='Bot parado.')
    # Para o updater
    updater.stop()
# Função para buscar jogos com alta probabilidade de ter 2 escanteios a partir do minuto 45 e a partir do minuto 85
def search_games(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo está no segundo tempo (minuto 45 a 90)
        if int(game['match_status']) >= 43 and int(game['match_status']) <= 45 or int(game['match_status']) >= 83:
            # Verifica se ambos os times já marcaram pelo menos 2 gols
            if game['match_hometeam_score'] >= 2 and game['match_awayteam_score'] >= 2:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} vs {away_team_name}")
def main() -> None:
    global updater
    # Inicia o updater com o token do bot
    updater = Updater(BOT_TOKEN)

    # Obtém o dispatcher do updater
    dispatcher = updater.dispatcher

    # Adiciona os handlers de comando
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("search", search_games))

    # Inicia o polling do bot
    updater.start_polling()

    # Fica aguardando novas mensagens
    updater.idle()
if __name__ == '__main__':
    main()
# Função para buscar jogos com alta probabilidade de ter 3 ou mais gols
def search_high_score_games(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo terminou e se teve pelo menos 3 gols marcados
        if int(game['match_status']) == 90 and game['match_hometeam_score'] + game['match_awayteam_score'] >= 3:
            # Envia mensagem de confirmação que o jogo foi encontrado
            update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_score']} x {game['match_awayteam_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter um gol no segundo tempo
def search_second_half_goals(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo está no segundo tempo (minuto 45 a 90)
        if int(game['match_status']) >= 43 and int(game['match_status']) <= 90:
            # Verifica se pelo menos 1 gol foi marcado no segundo tempo
            if game['match_hometeam_score'] + game['match_awayteam_score'] > game['match_hometeam_ht_score'] + game['match_awayteam_ht_score']:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_score']} x {game['match_awayteam_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter um gol nos primeiros 15 minutos
def search_first_half_goals(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo está no primeiro tempo (minuto 1 a 45)
        if int(game['match_status']) >= 1 and int(game['match_status']) <= 43:
            # Verifica se pelo menos 1 gol foi marcado nos primeiros 15 minutos
            if game['match_hometeam_score'] + game['match_awayteam_score'] > 0 and game['match_time'] <= 15:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_score']} x {game['match_awayteam_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter um gol nos últimos 15 minutos
def search_last_minute_goals(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo está no segundo tempo (minuto 45 a 90)
        if int(game['match_status']) >= 43 and int(game['match_status']) <= 90:
            # Verifica se pelo menos 1 gol foi marcado nos últimos 15 minutos
            if game['match_hometeam_score'] + game['match_awayteam_score'] > 0 and game['match_time'] >= 75:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_score']} x {game['match_awayteam_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter um gol antes dos 30 minutos
def search_early_goals(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo está no primeiro tempo (minuto 1 a 45)
        if int(game['match_status']) >= 1 and int(game['match_status']) <= 43:
            # Verifica se pelo menos 1 gol foi marcado antes dos 30 minutos
            if game['match_hometeam_score'] + game['match_awayteam_score'] > 0 and game['match_time'] < 30:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_score']} x {game['match_awayteam_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter mais de 1 gol no primeiro tempo
def search_first_half_over_1_5_goals(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo está no primeiro tempo (minuto 1 a 45)
        if int(game['match_status']) >= 1 and int(game['match_status']) <= 43:
            # Verifica se já foram marcados 2 ou mais gols no primeiro tempo
            if game['match_hometeam_ht_score'] + game['match_awayteam_ht_score'] > 1:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_ht_score']} x {game['match_awayteam_ht_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter mais de 1 gol no segundo tempo
def search_second_half_over_1_5_goals(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo está no segundo tempo (minuto 45 a 90)
        if int(game['match_status']) >= 43 and int(game['match_status']) <= 90:
            # Verifica se já foram marcados 2 ou mais gols no segundo tempo
            if game['match_hometeam_ft_score'] + game['match_awayteam_ft_score'] - game['match_hometeam_ht_score'] - game['match_awayteam_ht_score'] > 1:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_ft_score']} x {game['match_awayteam_ft_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter um gol nos primeiros 10 minutos
def search_early_goal(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo está no primeiro tempo (minuto 1 a 45)
        if int(game['match_status']) >= 1 and int(game['match_status']) <= 43:
            # Verifica se pelo menos 1 gol foi marcado nos primeiros 10 minutos
            if game['match_hometeam_score'] + game['match_awayteam_score'] > 0 and game['match_time'] < 10:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_score']} x {game['match_awayteam_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter um gol nos últimos 10 minutos
def search_late_goal(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo está no segundo tempo (minuto 45 a 90)
        if int(game['match_status']) >= 43 and int(game['match_status']) <= 90:
            # Verifica se pelo menos 1 gol foi marcado nos últimos 10 minutos
            if game['match_hometeam_score'] + game['match_awayteam_score'] > 0 and game['match_time'] > 80:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_score']} x {game['match_awayteam_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter menos de 2.5 gols
def search_under_2_5_goals(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se a partida já acabou
        if int(game['match_status']) == 90:
            # Verifica se houve menos de 2.5 gols na partida
            if game['match_hometeam_ft_score'] + game['match_awayteam_ft_score'] < 2.5:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_ft_score']} x {game['match_awayteam_ft_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter mais de 2.5 gols
def search_over_2_5_goals(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se a partida já acabou
        if int(game['match_status']) == 90:
            # Verifica se houve mais de 2.5 gols na partida
            if game['match_hometeam_ft_score'] + game['match_awayteam_ft_score'] > 2.5:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_ft_score']} x {game['match_awayteam_ft_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter um pênalti marcado
def search_penalty(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo já terminou
        if int(game['match_status']) == 90:
            # Verifica se houve um pênalti na partida
            if 'Penalty' in game['match_status']:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_ft_score']} x {game['match_awayteam_ft_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter um cartão vermelho
def search_red_card(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo já terminou
        if int(game['match_status']) == 90:
            # Verifica se houve um cartão vermelho na partida
            if 'Red Card' in game['match_status']:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_ft_score']} x {game['match_awayteam_ft_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter um cartão amarelo
def search_yellow_card(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo já terminou
        if int(game['match_status']) == 90:
            # Verifica se houve um cartão amarelo na partida
            if 'Yellow Card' in game['match_status']:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_ft_score']} x {game['match_awayteam_ft_score']} {away_team_name}")
# Função para buscar jogos com alta probabilidade de ter uma virada no placar
def search_comeback(update: Update, context: CallbackContext) -> None:
    # Recebe a data do usuário
    date = context.args[0]
    # Cria a URL da API de Futebol
    url = f'https://apifootball.com/api/?action=get_events&from={date}&to={date}&match_live=1&APIkey=' + API_KEY
    # Faz a requisição à API
    response = requests.get(url)
    # Converte a resposta em JSON
    data = response.json()

    # Itera sobre os jogos encontrados
    for game in data:
        home_team_name = game['match_hometeam_name']
        away_team_name = game['match_awayteam_name']

        # Verifica se o jogo já terminou
        if int(game['match_status']) == 90:
            # Verifica se houve uma virada no placar
            if game['match_hometeam_score'] != game['match_awayteam_score']:
                # Envia mensagem de confirmação que o jogo foi encontrado
                update.message.reply_text(f"Jogo encontrado: {home_team_name} {game['match_hometeam_ft_score']} x {game['match_awayteam_ft_score']} {away_team_name}")
