# Plano de Testes (TDD First) - Sistema de Encomendas

Este documento descreve a estratégia de testes automatizados para o sistema, priorizando cenários críticos e seguindo o ciclo TDD (Red-Green-Refactor).

## 1. Estratégia de Testes

- **Framework:** `pytest`
- **Abordagem:** Testes de Unidade e Integração.
- **Isolamento:** Uso de banco de dados SQLite em memória para garantir rapidez e consistência.
- **Mocks:** Utilização de `pytest-mock` para simular dependências externas se necessário.

---

## 2. Cenários de Teste por Funcionalidade

### 2.1. Autenticação e Cadastro
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-01 | Cadastro de Novo Cliente | Integração | Alta | Validar se um usuário com role 'cliente' é criado corretamente no banco. |
| TC-02 | Login com Credenciais Válidas | Integração | Crítica | Verificar se o usuário é autenticado e redirecionado para a rota correta conforme seu papel. |
| TC-03 | Login com Senha Incorreta | Unidade | Alta | Garantir que o sistema rejeite credenciais inválidas e exiba mensagem de erro. |

### 2.2. Gestão de Pedidos (Cliente)
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-04 | Criação de Pedido | Integração | Crítica | Validar se um cliente autenticado pode registrar um pedido com detalhes e endereço. |
| TC-05 | Acesso Negado a Outras Roles | Segurança | Alta | Garantir que atendentes/admins não acessem a rota de criação de pedido de cliente (403). |

### 2.3. Gestão Operacional (Atendente)
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-06 | Iniciar Fabricação | Integração | Alta | Validar a transição de status do pedido de 'Pendente' para 'Em Fabricação Manual'. |
| TC-07 | Despachar Pedido com Rastreio | Integração | Alta | Verificar se o status muda para 'Enviado' e o código de rastreio é persistido. |

### 2.4. Administração (Admin)
| ID | Cenário | Tipo | Prioridade | Descrição |
|:---|:---|:---|:---|:---|
| TC-08 | Registro de Atendente | Integração | Alta | Validar que apenas o Admin pode criar usuários com a role 'atendente'. |
| TC-09 | Relatório Consolidado | Unidade | Média | Verificar se o cálculo de métricas (total, pendentes, etc.) está correto matematicamente. |

---

## 3. Estrutura do Ambiente de Teste

Os testes devem residir no diretório `/tests`. Cada arquivo de teste deve seguir o padrão `test_*.py`.

### 3.1. Configuração do Fixture (`tests/conftest.py`)
- Configurar o `app` em modo de teste (`TESTING=True`).
- Inicializar `db.create_all()` em um banco SQLite temporário.
- Limpar o banco após cada função de teste.

---

## 4. Ciclo TDD Sugerido
1. **RED:** Escrever o teste para o cenário crítico antes da implementação da rota/lógica.
2. **GREEN:** Implementar o código mínimo necessário para passar no teste.
3. **REFACTOR:** Melhorar a estrutura do código mantendo os testes passando.
