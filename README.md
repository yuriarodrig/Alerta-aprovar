# Sistema de Alerta para Pedidos em Atraso

## Descrição do Projeto

Meu projeto é um aplicativo que alerta gestores sobre pedidos de compra pendentes. Ele monitora os pedidos e envia alertas por email e WhatsApp para garantir que as pendências sejam tratadas de forma eficiente.

O aplicativo utiliza diversas tecnologias para fornecer funcionalidades robustas. O desenvolvimento foi realizado em Python, aproveitando as bibliotecas e frameworks como Twilio, Pandas, Datetime, os, dotenv, aws. 

A escolha do Python como linguagem principal se deve à sua facilidade de uso, versatilidade e ampla comunidade de suporte. O Twilio foi utilizado para integrar a funcionalidade de envio de mensagens automatizadas via WhatsApp, proporcionando uma comunicação direta e eficiente com os gestores. A biblioteca Pandas foi utilizada para processar e analisar os dados dos pedidos de compra, enquanto o módulo Datetime permitiu o cálculo preciso dos dias pendentes.

Além disso, utilizei os módulos os-getenv, dotenv-find_dotenv e load_dotenv para gerenciar as variáveis de ambiente e garantir a segurança das informações sensíveis.

Com esse projeto, meu objetivo foi fornecer uma solução que ajude os gestores a gerenciar e tratar de forma proativa os pedidos de compra pendentes, aumentando a eficiência operacional e evitando atrasos desnecessários.


## Bibliotecas Utilizadas

O projeto utiliza as seguintes bibliotecas:

- pandas
- pyodbc
- os
- boto3
- emoji
- python.dotenv
- time
- datetime
- twilio
- pretty_html_table
- email




### Enviador de Mensagens para Aprovação de Pedidos
Este script em Python permite enviar mensagens por WhatsApp e e-mails para aprovação de pedidos de compra. Ele se conecta a um banco de dados SQL Server e busca os pedidos pendentes de aprovação. Em seguida, envia notificações aos responsáveis por meio do WhatsApp e e-mail.

### Pré-requisitos
Antes de executar o script, certifique-se de ter os seguintes requisitos instalados/configurados:
-Python 3.x
-Contas ativas no Twilio e na AWS com as credenciais necessárias
-Banco de dados SQL Server com as informações dos pedidos
-Configuração
-Antes de executar o script, é necessário configurar as seguintes variáveis de ambiente no arquivo .env:

![image](https://github.com/yuriarodrig/Alerta-aprovar/assets/122099448/db2c1bc7-7fd9-41b6-882f-57c0fb576b35)

Além disso, é necessário adaptar o dicionário dicionario para mapear os telefones dos aprovadores de acordo com seus nomes.

## Utilização
Após configurar as variáveis de ambiente, execute o script em um ambiente Python compatível. Ele buscará os pedidos pendentes de aprovação e enviará mensagens para os aprovadores por meio do WhatsApp e e-mails.

## Personalização
Certifique-se de adaptar o código para atender às suas necessidades específicas. Você pode modificar a consulta SQL para buscar informações adicionais dos pedidos ou alterar a formatação das mensagens enviadas por WhatsApp e e-mail.

Também é importante lembrar de personalizar o dicionário dicionario com os telefones corretos dos aprovadores, além de fazer quaisquer outras alterações necessárias no código para se adequar ao seu ambiente.

## Limitações
Este script foi desenvolvido com base em informações fornecidas e pode não abranger todos os casos de uso ou situações específicas. É importante analisar o código e adaptá-lo conforme necessário para atender às suas necessidades.

## Imagens Exemplos:
Whatsapp:

![image](https://github.com/yuriarodrig/Alerta-aprovar/assets/122099448/3e09e8e9-aaea-45f8-a7c7-8b716d48ab37)

Email:

![image](https://github.com/yuriarodrig/Alerta-aprovar/assets/122099448/d2e86008-a1d5-4935-9f43-28a885e3e25d)



