import pandas as pd
import pyodbc
from os import getenv
import boto3
import emoji
from dotenv import find_dotenv, load_dotenv
from datetime import date
from twilio.rest import Client
from pretty_html_table import build_table
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv(find_dotenv(), override=True)
SERVER = getenv("server")
DATABASE = getenv("database")
USERNAME = getenv("user")
PASSWORD = getenv("password")
TWILIO_SID = getenv('twilio_sid')
TWILIO_TOKEN = getenv('twilio_token')
ACCESS_ID = getenv('aws_id')
ACCESS_KEY = getenv('aws_key')
AWS_REGION = "region"

client = Client(TWILIO_SID, TWILIO_TOKEN)
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+SERVER+';DATABASE='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)
cursor = conn.cursor()

dicionario = {
    #Telefones de cada Aprovadores Caso mudar o user(registro de user pego protheus) ou o telefone deve ser alterado aqui.
    'yuri': '27123456789'
}

class Send_message(object):
    def __init__(self) -> None:
        pass

    def Rec_log(self, periodo, numero, email = None, name = None):
        lista = [periodo, numero, email, name]
        with open('log_registro.txt', 'a') as file:
            file.write(f"{date.today().strftime('%d/%m/%Y %H:%M')} - {lista}\n")
            
            
    def Whatsapp(self, query, periodo):
        query = query[['NUMERO', 'NOME']].drop_duplicates('NUMERO')
        number, name = query['NUMERO'].values, query['NOME'].values
        
        for num, user in zip(number, name):
            client.messages.create(
                body=f'{user}, pedido de compra {num} está pendente',
                from_='whatsapp',
                to=f'whatsapp:+55{dicionario[user]}')
            self.Rec_log(periodo, name=user, numero=num)
    
    
    def Email(self, query, periodo):
        query = query.sort_values(by=['CENTRO_CUSTO', 'NUMERO'])
        email = query['EMAIL'].unique()[0]
        query = query[['EMISSAO', 'NUMERO', 'FORNECEDOR', 'CENTRO_CUSTO', 'DESCRICAO_CC', 'DESCRICAO']]
        list_pedidos = query['NUMERO'].drop_duplicates().to_list()

        html_table = build_table(query, 'grey_light', font_family='sans-serif', padding='3px', font_size='13.5px')
        grupo_email = [email]
        titulo = emoji.emojize(':warning: Solicitações de compras a vencer: ', variant="emoji_type")
        SENDER = "Send <send@gmail..com.br>"
        SUBJECT = titulo
        BODY_HTML = html_table
        CHARSET = "UTF-8"
        
        client = boto3.client('ses',region_name=AWS_REGION,
                        aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key= ACCESS_KEY)
        
        msg = MIMEMultipart('mixed')
        msg['Subject'] = SUBJECT 
        msg['From'] = SENDER 
        msg['To'] = ', '.join(grupo_email)
        msg_body = MIMEMultipart('alternative')
        htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
        msg_body.attach(htmlpart)
        msg.attach(msg_body)
            
        response = client.send_raw_email(
                Source=SENDER,
                Destinations=grupo_email,
                RawMessage={ 
                    'Data':msg.as_string(),},)
    
query = pd.read_sql('''SELECT 
            --SC7.,SCH.
                C7_EMISSAO AS EMISSAO, C7_NUM AS NUMERO, C7_FORNECE AS FORNECEDOR, 
            (CASE
                WHEN C7_CC = '' THEN CH_CC
                ELSE C7_CC
            END) AS CENTRO_CUSTO, CTT.CTT_DESC01 AS DESCRICAO_CC,CR_USER COD_USER, USR_CODIGO NOME, USR_EMAIL EMAIL, CR_STATUS STATUS, C7_DESCRI AS DESCRICAO
            FROM SC7010 SC7

            INNER JOIN SCR010 SCR ON SCR.D_E_L_E_T_ = '' AND CR_NUM = C7_NUM 
			INNER JOIN SYS_USR SYS ON SYS.D_E_L_E_T_ = '' AND USR_ID = CR_USER 
			LEFT JOIN SCH010 SCH ON SCH.CH_FILIAL = C7_FILIAL AND SCH.CH_PEDIDO = C7_NUM AND SCH.CH_ITEMPD = C7_ITEM 
			INNER JOIN CTT010 CTT ON CTT.CTT_CUSTO = (CASE
                										WHEN C7_CC = '' THEN CH_CC
               											ELSE C7_CC
                                        			END)
            
            WHERE
            SC7.D_E_L_E_T_ = ''
            AND C7_RESIDUO = ' '
            AND C7_ACCPROC =  '2'
            AND C7_CONAPRO = 'B'
            AND C7_QUJE < C7_QUANT
            AND C7_FILIAL = 'AF01'
            AND C7_EMISSAO > '20230424'
            ORDER BY C7_EMISSAO, C7_ITEM, C7_FORNECE''', conn)

periodos = [10, 20, 30]

for periodo in periodos:

    query['EMAIL'] = query['EMAIL'].str.strip()
    query['NOME'] = query['NOME'].str.strip()
    data_now = date.today()
    data_now = pd.to_datetime(data_now)
    query['EMISSAO'] = pd.to_datetime(query['EMISSAO'])

    query['Dias'] = data_now - query['EMISSAO']
    query['Dias'] = query['Dias'].dt.days
    query = query.loc[(query['Dias'] == periodos)]
    query = query.drop('Dias', axis=1)
    query['EMISSAO'] = query['EMISSAO'].dt.strftime('%d/%m/%Y')

    query = query.drop('COD_USER', axis=1)
    chave_numero = query['NUMERO'].drop_duplicates().to_list()

    for key_n in range(len(chave_numero)):
        group = query.loc[(query['NUMERO'] == chave_numero[key_n])]
        if '04' in group['STATUS'].values or '06' in group['STATUS'].values:
            query = query.drop(group.index, axis=0)

    query = query.loc[(query['STATUS'] == '02')]

    chave_user = query['NOME'].drop_duplicates().to_list()
    query = query.groupby('NOME')

    for key_u in range(len(chave_user)):
        group = query.get_group(chave_user[key_u])
        envio = Send_message()
        envio.Whatsapp(group, periodos)
        envio.Email(group, periodos)