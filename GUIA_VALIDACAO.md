# 🧪 Guia de Validação - ToDoX

## Pré-requisitos

✅ Backend funcionando: http://127.0.0.1:8000/health  
✅ Frontend funcionando: http://localhost:3001  
✅ Janelas do navegador abertas

---

## 🎯 Checklist de Validação

### ✅ **PASSO 1: Criar projeto via interface web**

1. **Acesse**: http://localhost:3001
2. **Localize**: Campo "Nome do Projeto" no topo da página
3. **Digite**: "Projeto Teste Validação"
4. **Clique**: Botão "Criar Projeto" (ou pressione Enter)
5. **Verifique**:
   - ✅ Projeto aparece na lista
   - ✅ Não há erros no console (F12)
   - ✅ Mensagem de sucesso (se houver)

**❌ Se der erro**: Verifique console do navegador (F12 → Console)

---

### ✅ **PASSO 2: Adicionar tarefas ao projeto**

1. **Clique**: No projeto que você criou
2. **Você será redirecionado** para: `/project/[ID]`
3. **Localize**: Campo para adicionar tarefa
4. **Adicione estas tarefas**:
   - "Tarefa 1 - Teste básico"
   - "Tarefa 2 - Implementar feature X"
   - "Tarefa 3 - Revisar documentação"
5. **Verifique**:
   - ✅ Tarefas aparecem na lista
   - ✅ Cada tarefa tem um ID único
   - ✅ Não há erros no console

**📝 Dica**: Se tiver campo de prioridade, teste valores diferentes (1-5)

---

### ✅ **PASSO 3: Testar drag & drop no board**

1. **Navegue** para: http://localhost:3001/board
2. **Ou clique** na aba "Board" (se disponível)
3. **Teste drag & drop**:
   - 🖱️ Clique e arraste uma tarefa
   - 🔄 Mova para posição diferente
   - 📍 Solte em nova posição
4. **Verifique**:
   - ✅ Tarefa move visualmente
   - ✅ Nova posição é mantida ao recarregar página
   - ✅ Não há erros no console
   - ✅ Outras tarefas se reorganizam corretamente

**❌ Se não funcionar**:

- Verifique se há colunas de status (TODO, DOING, DONE)
- Tente mover entre colunas diferentes

---

### ✅ **PASSO 4: Verificar backlog e outras páginas**

#### 📋 **Backlog**

1. **Navegue**: http://localhost:3001/backlog
2. **Verifique**:
   - ✅ Lista de tarefas carrega
   - ✅ Tarefas são organizadas por prioridade
   - ✅ Informações básicas estão visíveis

#### 🏗️ **Scaffold**

1. **Navegue**: http://localhost:3001/scaffold
2. **Verifique**:
   - ✅ Página carrega sem erro
   - ✅ Interface de scaffolding aparece
   - ✅ (Teste se funcional)

#### 📄 **Pull Requests**

1. **Navegue**: http://localhost:3001/prs
2. **Verifique**:
   - ✅ Página carrega
   - ✅ Lista de PRs (pode estar vazia)

#### 📺 **YAML Studio**

1. **Navegue**: http://localhost:3001/yaml-studio
2. **Verifique**:
   - ✅ Interface YAML carrega
   - ✅ Editor funciona

---

### ✅ **PASSO 5: Confirmar que não há erros no console**

1. **Abra DevTools**: Pressione `F12`
2. **Vá para aba**: `Console`
3. **Verifique**:
   - ✅ Sem erros vermelhos
   - ✅ Máximo warnings amarelos (aceitável)
   - ✅ Logs de sucesso da API (🔄, 📡, ✅)

#### **Logs esperados (normais)**:

```
🔄 API Request: {url: "http://localhost:8000/projects", method: "GET"}
📡 API Response: {url: "http://localhost:8000/projects", status: 200, ok: true}
✅ API Success: {url: "http://localhost:8000/projects", result: [...]}
```

#### **❌ Erros para investigar**:

- `Failed to fetch`
- `Network Error`
- `500 Internal Server Error`
- `CORS error`

---

## 🔧 **Testes Extras (Opcionais)**

### **API Direta**

- **Acesse**: http://127.0.0.1:8000/docs
- **Teste**: GET /projects
- **Teste**: POST /projects com `{"name": "Teste API"}`

### **Debug Pages**

- **Debug**: http://localhost:3001/debug
- **Browser Test**: http://localhost:3001/browser-test

---

## 📊 **Relatório de Validação**

Após completar todos os passos, preencha:

- [ ] ✅ Projeto criado com sucesso
- [ ] ✅ Tarefas adicionadas corretamente
- [ ] ✅ Drag & drop funcionando
- [ ] ✅ Todas as páginas carregam
- [ ] ✅ Console sem erros críticos
- [ ] ✅ API responde corretamente

### **Issues encontrados:**

1. _Descreva qualquer problema..._
2. _Incluir screenshots se necessário..._
3. _Logs de erro do console..._

---

## 🆘 **Se algo não funcionar**

1. **Recarregue** a página (Ctrl+F5)
2. **Verifique** se backend está rodando: http://127.0.0.1:8000/health
3. **Reinicie** os serviços se necessário
4. **Confira** console para erros específicos
5. **Teste** pages de debug primeiro

---

**🎉 Sucesso completo = Sistema pronto para desenvolvimento!**
