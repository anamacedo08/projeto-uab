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

### 2.6. Frontend, UX e Acessibilidade (E2E & Componentes)
Cenários focados na experiência do usuário, conformidade visual e acessibilidade.

| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-21 | Responsividade Mobile (360px) | Visual/E2E | Alta | Validar se o menu colapsa, botões ocupam 100% da largura e paddings são ajustados. |
| TC-22 | Responsividade Tablet (768px) | Visual/E2E | Média | Validar se o grid de produtos exibe exatamente 2 colunas. |
| TC-23 | Navegação por Teclado (A11y) | A11y | Crítica | Percorrer todo o fluxo de pedido usando apenas `Tab`/`Enter`. O foco deve ser visível (outline laranja). |
| TC-24 | Validação de Contraste (A11y) | A11y | Alta | Verificar se todos os textos (especialmente na navbar e botões) cumprem WCAG AA. |
| TC-25 | Atributos ARIA | A11y | Média | Validar presença de `aria-label` em botões de ícone e `aria-current` na navbar. |
| TC-26 | Feedback de Loading (Fix) | UX | Alta | Ao clicar em "Salvar" no modal, o botão deve mostrar spinner e desabilitar. Validar se a página recarrega após sucesso. |
| TC-27 | Recuperação de UI (Timeout) | UX | Média | Simular atraso na rede e garantir que a UI não fique travada permanentemente se a navegação falhar. |
| TC-28 | Mensagens de Erro Visual | UX | Alta | Submeter formulário inválido e validar se o campo ganha borda vermelha e foco. |
| TC-29 | Estados Vazios | UX | Média | Validar a renderização do componente de "Nenhum item encontrado" em todas as listagens. |
| TC-30 | Renderização Condicional (RBAC) | Funcional | Crítica | Garantir que o Cliente NÃO veja botões de Edição/Deleção nem links de Administração. |
| TC-31 | Estabilidade de Modal | UX | Alta | Abrir, fechar via "X", fechar via Backdrop e fechar via ESC. O foco deve retornar ao botão disparador. |
| TC-32 | Regressão Visual Navbar | Visual | Média | Validar se a Navbar mantém a cor `#1b5e20` e o efeito de blur ao rolar a página. |
| TC-33 | Fluxo de Edição de Produto | E2E | Crítica | Abrir modal -> Alterar Nome -> Salvar -> Verificar se o modal fecha e o novo nome aparece na lista. |
| TC-34 | Feedback de Flash Messages | UX | Alta | Validar se as mensagens de sucesso/erro aparecem no topo com botão de fechar funcional. |




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
