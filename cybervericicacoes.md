# Inspeção de Cibersegurança - Sistema de Encomendas

## Resumo Executivo

Esta inspeção detalhada de cibersegurança foi realizada na pasta `app` do projeto, seguindo as diretrizes do OWASP Top 10 e boas práticas de desenvolvimento seguro. Foram identificadas vulnerabilidades que variam de nível Crítico a Baixo.

### Contagem de Achados por Severidade
- **Crítica:** 1 (Falta de Proteção CSRF)
- **Alta:** 3 (Debug Mode habilitado, Secret Key padrão, Dependências Vulneráveis)
- **Média:** 2 (Falta de Rate Limiting, Falta de Validação de Entradas/XSS)
- **Baixa:** 2 (Política de Senha Fraca, Falha em Logging e Monitoramento)

### 5 Ações Mais Urgentes
1. **Implementar Proteção CSRF:** Adicionar `Flask-WTF` e tokens CSRF em todos os formulários (`POST`, `PUT`, `DELETE`).
2. **Desabilitar Debug Mode em Produção:** Garantir que `debug=False` seja utilizado em ambientes reais.
3. **Atualizar Dependências:** Atualizar `Flask`, `Werkzeug` e outras bibliotecas para as versões mais recentes para corrigir CVEs conhecidos.
4. **Alterar SECRET_KEY:** Configurar uma chave secreta forte e única via variáveis de ambiente.
5. **Implementar Rate Limiting:** Adicionar proteção contra brute force na rota de login.

---

## Vulnerabilidades Identificadas

### 1. Falta de Proteção CSRF (Cross-Site Request Forgery)
- **Localização:** `app/templates/*.html` e todas as rotas `POST`.
- **Descrição:** O sistema não utiliza tokens CSRF em seus formulários. Isso permite que um atacante induza um usuário autenticado a realizar ações indesejadas (como deletar produtos ou usuários) simplesmente ao visitar um site malicioso.
- **Evidência:** 
  ```html
  <!-- app/templates/crud_produtos.html:43 -->
  <form action="{{ url_for('admin.deletar_produto', produto_id=produto.id) }}" method="POST">
      <button type="submit" class="btn btn-sm btn-outline-danger shadow-sm">Excluir</button>
  </form>
  ```
- **Impacto Potencial:** Exclusão acidental ou maliciosa de dados, criação de usuários administradores falsos, alteração de status de pedidos por terceiros.
- **Nível de Severidade:** **Crítica**
- **Recomendação de Correção:** Utilize a extensão `Flask-WTF`. No formulário HTML, adicione `{{ form.csrf_token }}`. No backend, inicialize o `CSRFProtect`.
- **Referências:** CWE-352, OWASP A01:2021-Broken Access Control.

### 2. Debug Mode Habilitado em Produção
- **Localização:** `run.py`, linha 6.
- **Descrição:** O aplicativo está configurado para rodar com `debug=True`. Em um ambiente de produção, isso expõe o depurador interativo, permitindo execução remota de código (RCE) em caso de erro.
- **Evidência:** 
  ```python
  # run.py:6
  app.run(host="0.0.0.0", port=5000, debug=True)
  ```
- **Impacto Potencial:** Execução de comandos arbitrários no servidor, exposição total do código-fonte e variáveis de ambiente (incluindo credenciais).
- **Nível de Severidade:** **Alta**
- **Recomendação de Correção:** Altere para `debug=False` ou utilize uma variável de ambiente para controlar o modo de depuração.
- **Referências:** CWE-489, OWASP A02:2021-Security Misconfiguration.

### 3. Uso de Secret Key Padrão/Exposta
- **Localização:** `app/__init__.py`, linha 21.
- **Descrição:** O sistema utiliza uma `SECRET_KEY` padrão ('default-key') caso a variável de ambiente não esteja configurada. Chaves padrão são facilmente adivinhadas.
- **Evidência:** 
  ```python
  # app/__init__.py:21
  app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-key')
  ```
- **Impacto Potencial:** Falsificação de cookies de sessão, permitindo que um atacante se passe por qualquer usuário (incluindo admins).
- **Nível de Severidade:** **Alta**
- **Recomendação de Correção:** Remova o valor padrão e exija que a `SECRET_KEY` seja fornecida via ambiente. Se não fornecida, o app deve falhar ao iniciar.
- **Referências:** CWE-798, OWASP A02:2021-Security Misconfiguration.

### 4. Uso de Dependências Vulneráveis / Desatualizadas
- **Localização:** `requirements.txt`.
- **Descrição:** O projeto utiliza versões antigas do `Flask` (2.3.3) e `Werkzeug` (2.3.7). Versões do Werkzeug anteriores a 3.0.1 possuem vulnerabilidades conhecidas relacionadas a parsing de cabeçalhos e negação de serviço (DoS).
- **Evidência:** 
  ```text
  Flask==2.3.3
  Werkzeug==2.3.7
  ```
- **Impacto Potencial:** Exploração de vulnerabilidades conhecidas no framework e servidor web, podendo levar a DoS ou bypass de segurança.
- **Nível de Severidade:** **Alta**
- **Recomendação de Correção:** Atualizar as dependências no `requirements.txt` (ex: `Flask>=3.0.0`, `Werkzeug>=3.0.1`).
- **Referências:** CVE-2023-46136, CVE-2024-34069, OWASP A03:2021-Software and Data Integrity Failures.

### 5. Ausência de Rate Limiting no Login
- **Localização:** `app/routes/auth.py`, função `login`.
- **Descrição:** Não há limite para tentativas de login, facilitando ataques de força bruta.
- **Evidência:** A função `login` processa requisições `POST` sem qualquer controle de frequência.
- **Impacto Potencial:** Comprometimento de contas de usuários através de ataques de dicionário ou força bruta.
- **Nível de Severidade:** **Média**
- **Recomendação de Correção:** Utilize `Flask-Limiter` para restringir o número de tentativas de login por IP ou usuário.
- **Referências:** CWE-307, OWASP A07:2021-Authentication Failures.

### 6. Falta de Validação de Entradas e Risco de XSS
- **Localização:** `app/services/product_service.py`, `app/services/order_service.py`.
- **Descrição:** Os dados recebidos dos usuários (como URLs de imagens e descrições) são salvos diretamente no banco de dados sem validação rigorosa. Embora o Jinja2 use autoescaping, atributos HTML como `src` ou `href` podem ser explorados se contiverem `javascript:`.
- **Evidência:** 
  ```python
  # app/services/product_service.py:12
  novo_produto = Produto(nome=nome, descricao=descricao, imagem_url=imagem_url)
  ```
- **Impacto Potencial:** Cross-Site Scripting (XSS) armazenado, redirecionamentos maliciosos.
- **Nível de Severidade:** **Média**
- **Recomendação de Correção:** Implementar validação de tipo e formato no lado do servidor (ex: verificar se `imagem_url` começa com `http` e termina com extensão de imagem).
- **Referências:** CWE-79, CWE-20, OWASP A05:2021-Injection.

### 7. Política de Senhas Fraca
- **Localização:** `app/routes/auth.py`, função `cadastro`.
- **Descrição:** O cadastro de novos usuários não impõe critérios de complexidade para senhas (comprimento mínimo, caracteres especiais, etc.).
- **Evidência:** O código apenas recebe a senha e gera o hash, sem validação prévia.
- **Impacto Potencial:** Uso de senhas triviais que são facilmente quebradas.
- **Nível de Severidade:** **Baixa**
- **Recomendação de Correção:** Adicionar verificações de força de senha no momento do cadastro.
- **Referências:** CWE-521, OWASP A07:2021-Authentication Failures.

### 8. Falta de Registro de Eventos de Segurança (Logging)
- **Localização:** Todo o projeto.
- **Descrição:** Não há logs para tentativas de login falhas, acesso negado a rotas administrativas ou alterações críticas no banco de dados.
- **Evidência:** Ausência de chamadas a `logging.warning` ou similares em pontos críticos de decisão de segurança.
- **Impacto Potencial:** Dificuldade em detectar ataques em andamento ou realizar perícia pós-incidente.
- **Nível de Severidade:** **Baixa**
- **Recomendação de Correção:** Implementar um sistema de logging que registre eventos significativos de segurança.
- **Referências:** CWE-778, OWASP A09:2021-Security Logging and Alerting Failures.
