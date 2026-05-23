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
| TC-09 | Criação de Pedido | Integração | Crítica | Validar se o cliente pode criar um pedido e se ele aparece em sua lista. |
| TC-10 | Transição de Status (Fabricação) | Integração | Alta | Atendente altera pedido de 'Pendente' para 'Em Fabricação Manual'. |
| TC-11 | Finalização e Rastreio | Integração | Alta | Atendente insere código de rastreio e muda status para 'Enviado'. |

### 2.4. Administração
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-12 | CRUD de Atendentes | Integração | Alta | Admin cria e remove usuários com papel de 'atendente'. |
| TC-13 | Integridade do Relatório | Unidade | Média | Validar se a contagem de pedidos por status no relatório bate com o banco de dados. |

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
