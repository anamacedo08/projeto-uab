# Plano de Testes (TDD First) - Sistema de Encomendas

Este documento detalha o planejamento de testes automatizados, seguindo a metodologia **TDD (Test Driven Development)**. O foco está na garantia da integridade das regras de negócio, segurança de acesso (RBAC - Role Based Access Control) e estabilidade do sistema.

## 1. Estratégia de Testes

### 1.1. Framework e Ferramentas
- **Base:** `pytest` para execução e organização dos testes.
- **Integração Web:** `pytest-flask` para simular requisições HTTP e interagir com o contexto da aplicação.
- **Banco de Dados:** SQLite em memória (`sqlite:///:memory:`) para garantir que cada teste comece em um estado limpo e seja executado rapidamente.
- **Cobertura:** `pytest-cov` para monitorar a porcentagem de código testado.
- **Dados Sintéticos:** `Faker` para geração de dados aleatórios e realistas (nomes, e-mails, senhas).

### 1.2. Abordagem TDD
O ciclo de desenvolvimento deve seguir rigorosamente:
1.  **RED:** Criar o teste que falha para a nova funcionalidade ou correção.
2.  **GREEN:** Implementar o código mínimo necessário para o teste passar.
3.  **REFACTOR:** Melhorar a implementação garantindo que todos os testes continuem passando.

---

## 2. Cenários de Teste

### 2.1. Autenticação e Controle de Sessão
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-01 | Cadastro de Cliente | Unidade | Alta | Validar se um novo usuário com `role='cliente'` é criado com hash de senha. |
| TC-02 | Login de Usuário | Integração | Crítica | Verificar redirecionamento correto pós-login para Admin, Atendente e Cliente. |
| TC-03 | Logout | Integração | Média | Garantir que a sessão seja encerrada e o usuário redirecionado para o login. |
| TC-04 | Acesso Não Autenticado | Segurança | Crítica | Tentar acessar `/clientes/pedidos` sem login e esperar redirecionamento (302) para `/login`. |

### 2.2. Segurança e Autorização (RBAC)
Cenários focados em impedir o acesso indevido entre diferentes perfis de usuário.

| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-05 | Cliente -> Painel Atendente | Segurança | Crítica | Cliente autenticado tenta acessar `/atendente/painel`. **Esperado: 403 Forbidden**. |
| TC-06 | Cliente -> Gestão Admin | Segurança | Crítica | Cliente autenticado tenta acessar `/admin/atendentes`. **Esperado: 403 Forbidden**. |
| TC-07 | Cliente -> Relatórios Admin | Segurança | Crítica | Cliente autenticado tenta acessar `/admin/relatorios`. **Esperado: 403 Forbidden**. |
| TC-08 | Atendente -> Gestão Admin | Segurança | Alta | Atendente tenta acessar rotas exclusivas do administrador. **Esperado: 403 Forbidden**. |

### 2.3. Gestão de Pedidos (Fluxo Operacional)
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-09 | Criação de Pedido | Integração | Crítica | Validar se o cliente pode criar um pedido informando telefone e endereço detalhado (CEP, Estado, Cidade, Endereço, Número). |
| TC-10 | Transição de Status (Fabricação) | Integração | Alta | Atendente altera pedido de 'Pendente' para 'Em Fabricação Manual'. |
| TC-11 | Finalização e Rastreio | Integração | Alta | Atendente insere código de rastreio e muda status para 'Enviado'. |

### 2.4. Gestão de Pedidos e Produtos (Novos Requisitos)
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-12 | Edição de Pedido Pendente | Integração | Alta | Cliente edita detalhes de um pedido com status 'Pendente'. |
| TC-13 | Deleção de Pedido Pendente | Integração | Alta | Cliente remove um pedido com status 'Pendente'. |
| TC-14 | Bloqueio de Edição/Deleção | Segurança | Alta | Tentar editar ou deletar pedido com status 'Em Fabricação Manual'. **Esperado: Erro ou bloqueio**. |
| TC-15 | Edição de Produto (Admin) | Integração | Média | Administrador altera nome e descrição de um produto existente. |
| TC-16 | Pré-cadastro de Produtos | Sistema | Média | Verificar se ao iniciar o sistema pela primeira vez, 5 produtos são criados. |
| TC-17 | Lista Detalhada em Relatórios | Funcional | Média | Verificar se a tela de relatórios lista os pedidos com descrição, status e nome do usuário. |

### 2.5. Otimização e Desempenho
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-17 | Cache de Produtos | Performance | Média | Validar se a segunda chamada à lista de produtos não executa query no banco. |
| TC-18 | Invalidação de Cache | Performance | Média | Garantir que ao criar um produto, o cache 'all_products' seja removido. |
| TC-19 | Background Notification | Assíncrono | Alta | Verificar se a função de notificação é disparada sem bloquear a resposta HTTP. |
| TC-20 | Cache de Relatórios | Performance | Média | Validar persistência do cache de métricas por 120 segundos. |

### 2.6. Frontend e Experiência do Usuário (UX)
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-21 | Responsividade de Tabelas | Visual | Média | Verificar se as tabelas de pedidos e produtos possuem `.table-responsive`. |
| TC-22 | Cores de Status de Pedido | Visual | Alta | Garantir que o status 'Enviado' exiba badge verde e 'Pendente' exiba badge amarelo. |
| TC-23 | Acessibilidade: Navegação | A11y | Alta | Validar se o link da página atual no navbar possui `aria-current="page"`. |
| TC-24 | Acessibilidade: Formulários | A11y | Crítica | Verificar se todos os inputs nos formulários de Pedido e Cadastro possuem labels associados. |
| TC-25 | Validação de CEP | Funcional | Alta | Tentar enviar CEP inválido e verificar se a validação HTML5 bloqueia o envio. |
| TC-26 | Estado Vazio: Vitrine | Visual | Baixa | Garantir exibição de mensagem "Nenhum produto encontrado" quando a lista estiver vazia. |
| TC-27 | Feedback de Loading | Visual | Média | Verificar se botões de submit mostram spinner visual após o clique. |

---

## 3. Ambiente e Execução

### 3.1. Configuração de Fixtures (`tests/conftest.py`)
Para que o TDD seja efetivo, o ambiente deve ser automatizado:
- `app()`: Retorna a instância da aplicação configurada para testes.
- `client()`: Retorna o cliente de teste do Flask.
- `db_session()`: Gerencia o ciclo de vida do banco de dados (setup/teardown) para cada teste.
- `auth_client(role)`: Helper para retornar um cliente já autenticado com o papel especificado.

### 3.2. Comandos de Execução
```bash
# Executar todos os testes
pytest

# Executar com relatório de cobertura
pytest --cov=app tests/

# Executar um cenário específico (ex: TC-05)
pytest tests/test_security.py -k "test_cliente_access_atendente_panel"
```

---

## 4. Manutenção do Plano
Este plano deve ser atualizado sempre que uma nova especificação técnica (como a `03-especs.md`) for alterada ou novas funcionalidades forem introduzidas no roteiro de desenvolvimento.
