import pandas as pd
import pyodbc
from os import getenv
import boto3
import emoji
from dotenv import find_dotenv, load_dotenv
from time import sleep
from datetime import date
from twilio.rest import Client
from pretty_html_table import build_table
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

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

#query de pedidos pendentes de aprovação
query = pd.read_sql('''SELECT 
		--SC7.,SCH.
		    C7_EMISSAO AS EMISSAO, C7_NUM AS NUMERO, C7_FORNECE AS FORNECEDOR, C7_ITEM AS ITEM, 
		(CASE
			WHEN C7_CC = '' THEN CH_CC
			ELSE C7_CC
		END) AS CENTRO_CUSTO, CR_USER COD_USER, USR_CODIGO NOME, USR_EMAIL EMAIL, CR_STATUS STATUS, C7_DESCRI AS DESCRICAO
		FROM SC7010 SC7
		
		INNER JOIN SCR010 SCR ON SCR.D_E_L_E_T_ = '' AND CR_NUM = C7_NUM 
		INNER JOIN SYS_USR SYS ON SYS.D_E_L_E_T_ = '' AND USR_ID = CR_USER 
        left join SCH010 SCH ON CH_FILIAL = C7_FILIAL AND CH_PEDIDO = C7_NUM AND CH_ITEMPD = C7_ITEM
		WHERE
        SC7.D_E_L_E_T_ = ''
        AND C7_RESIDUO = ' '
        AND C7_ACCPROC =  '2'
        AND C7_CONAPRO = 'B'
        AND C7_QUJE < C7_QUANT
        ORDER BY C7_EMISSAO, C7_ITEM, C7_FORNECE''', conn)

def send_Whats(query, periodo):
    cont = 0
    user_cont = 0
    df = query
    
    #Removendo e tratando colunas
    df = df.drop(['COD_USER', 'ITEM', 'EMAIL', 'DESCRIÇÃO', 'FORNECEDOR'], axis=1)
    df = df.sort_values(['NUMERO', 'CENTRO_CUSTO'])
    df = df.drop(['EMISSAO'], axis=1)
    lista_num = list(dict.fromkeys(df['NUMERO']))
    
    while cont <= (len(lista_num)-1):
        group = df.groupby(['NUMERO'])
        group = group.get_group(lista_num[cont])
        
        if '04' in group['STATUS'].values or '06' in group['STATUS'].values:
            df = df.drop(group.index)
            cont += 1
        else:
            cont += 1
    df = df.loc[(df['STATUS'] == '02')]    
    df = df.drop(['STATUS', 'CENTRO_CUSTO'], axis=1) 
    list_users = list(dict.fromkeys(df['NOME']))
    
    while user_cont <= (len(list_users)- 1):
        filter_group = df.groupby(['NOME'])
        filter_group = filter_group.get_group(list_users[user_cont])
        numero = list(dict.fromkeys(filter_group['NUMERO']))
        for i in numero:
            user = list_users[user_cont]
            message = client.messages \
                            .create(          
                                    body=f'Olá, {user}! O pedido de compra {i} está pendente de aprovação há {periodo} dias',
                                    from_='whatsapp:+552732056730',
                                    #to=f'whatsapp:+55{dicionario[user]}',
                                    to=f'whatsapp:+552732056733',    
                                )
        print(f'Mensagem enviada para {user} com os pedidos {numero}')
        user_cont += 1
    return


def send_Email(query, periodo):
    cont = 0
    user = 0
    df = query
    
    df['EMISSAO'] = df['EMISSAO'].dt.strftime('%d/%m/%Y')
    df = df.sort_values(['NUMERO', 'CENTRO_CUSTO'])
    lista_numero = list(dict.fromkeys(df['NUMERO']))
    
    while cont <= (len(lista_numero) -1):
        remove = df.groupby(['NUMERO'])
        remove = remove.get_group(lista_numero[cont])
        
        if '04' in remove['STATUS'].values or '06' in remove['STATUS'].values:
            df = df.drop(remove.index)
            cont +=1
        else:
            cont +=1
            
    filter_group = df.loc[(df['STATUS'] == '02')]
    list_user = list(dict.fromkeys(filter_group['NOME']))
    
    while user <= (len(list_user) -1):
        save_old = filter_group
        filter_group = filter_group.groupby('NOME')
        filter_group = filter_group.get_group(list_user[user])
        email = list(dict.fromkeys(filter_group['EMAIL']))
        email = email[0]
        email
        #Removendo colunas para não exibir no e-mail
        filter_group = filter_group.drop(['NOME'], axis=1)
        filter_group = filter_group.drop(['STATUS'], axis=1)
        filter_group = filter_group.drop(['EMAIL'], axis=1)
        filter_group = filter_group.drop(['ITEM'], axis=1)
        filter_group = filter_group.drop(['FORNECEDOR'], axis=1)
        filter_group = filter_group.drop(['CENTRO_CUSTO'], axis=1)
        filter_group = filter_group.drop(['COD_USER'], axis=1)
        filter_group = filter_group.drop_duplicates()
        
        html_tabela = build_table(filter_group, 'grey_light', font_family='sans-serif',padding='3px', font_size='13.5px')
        index = filter_group
        
        grupo_email = [email]
        titulo = emoji.emojize(':warning: Solicitações de compras a vencer: ', variant="emoji_type")
        SENDER = "Send <send@gmail..com.br>"
        SUBJECT = titulo
        BODY_HTML = index
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
                    'Data':msg.as_string(),
            },)
        user +=1
        filter_group = save_old
        print(f'email enviado para {email}')
        sleep(1)
    return print('''emails enviado---------------------''')


#Tratando colunas
query = query.rename({'DESCRICAO': 'DESCRIÇÃO'},        axis = 1)
query['CENTRO_CUSTO'] = query['CENTRO_CUSTO'].str.strip()
query['DESCRIÇÃO'] = query['DESCRIÇÃO'].str.strip()
query['NOME'] = query['NOME'].str.strip()
    
    
#Tratando Datas da tabela e data hoje
hoje = date.today()
data = pd.to_datetime(hoje)
query['EMISSAO'] = pd.to_datetime(query['EMISSAO'])
query['Diferença de dias'] = data - query['EMISSAO']
periodo = ['10', '20', '30']    

for i in periodo:
    old_query = query
    query = (query.loc[(query["Diferença de dias"] == f'{i} days')])
    #print(query)
    if not query.index.empty == True:
        query = query.drop(['Diferença de dias'], axis = 1)
        g = query.groupby('CENTRO_CUSTO')
        cc = (query['CENTRO_CUSTO'])
        send_Email(query=query, periodo=i)
        #send_Whats(query=query, periodo=i)
    query = old_query
