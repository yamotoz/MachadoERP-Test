

Comando para iniciar:

.\odoo-venv\Scripts\python.exe odoo-19.0\odoo-bin -r odoo -w odoo --db_host 127.0.0.1 --db_port 5432 --addons-path odoo-19.0\addons,controle_combustivel\.. -d erp_final --limit-time-real=3600


Página para vizualizar: http://127.0.0.1:8069/web/login?db=erp_final






**Problemas que eu tive de maneira geral(manual de bordo):**



1-problemas que eu tive inicialmente, na hora de subir pro ar como o banco estava em portugues e o odoo em ingles, deu conflito e nao subiu, 

2-outro problema foi a aquestão da vasta instalacao do odoo, que pude ver que é bem complexo o sistema, precisando em si de muita atenção e estudo.

3-outro problema que tive foi quando subiu no ar e deu problema de acesso negado, forcei um reset da sejha do admin para admin via terminal.

4-conseguir acessar o painel de login depois de muito acesso negado e entre no manager para vizualizar mais uma crição de database, consegui criar lá dentro, porém deu erro de collate e ctype, eles parecem não ser suportados. (erro aconteceu devido a rigosidade do windows em relação ao postgres)

5-para fins de intalação de alguns modulos do oddo ultilizei para tentar corrigir o problema:
.\odoo-venv\Scripts\python.exe odoo-19.0\odoo-bin -r odoo -w odoo --db_host 127.0.0.1 --db_port 5432 --addons-path odoo-19.0\addons,controle_combustivel\.. -d erp_final -i base,web


6-erro mais violento que passei, um bug no odoo 19
deu erro pois o odoo buscava uma variavel que não estava definida e ai dava curto circuito e acess denied mesmo com a senha certa. pra resolver eu instalei a biblioteca geoip2 e fiz de uma forma que ele ignorasse caso ele não conseguisse minha localidade que era o problema central e em relação ao banco de dados um dos grandes problemas foi a sintaxe que resolvi colocando um template0


problemas quanto a ativação do modulo de combustivel devido a erros relacionados a modernização de alguns componentes chatter e seach view e usei alguns parametros ultrapassados me resultando nessa dor de cabeça que tive, coisas que achava que dava pra usar mais não deram certo.

consegui entrar no sistema e instalar o modulo de combustivel, estou feliz kakakakak pense numa luta, agora to confirgurando meu usuario pois nãoe stava aprecendo na grade o combustivel, agora vou me colocar como administrador e seguir em frente pra testar o sistema.

consegui fazer aparecer, porém tive um problema por falta de key, vou resolver aqui, após alguns minutos, consegui resolver, deu certo, agora vou testar o sistema. o problema foi que o odoo procurava uma chave de registro que não existia que nem a da localização kkkkkkk

esta dando certo, já estou cadastrando veiculos e tanques, agora vou cadastrar abastecimentos e já fazer os testes do sistema, ta bem interessante







