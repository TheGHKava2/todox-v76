# 🚀 DEPLOY RENDER - INSTRUÇÕES COMPLETAS

## 📋 PRÉ-REQUISITOS:

- ✅ **Conta Render**: Criada
- ✅ **Repositório**: todox-v76 no GitHub
- ✅ **Código**: Backend simplificado pronto

## 🔧 PASSO A PASSO NO RENDER:

### **1. Conectar GitHub:**

1. Acesse: https://dashboard.render.com
2. Clique: **"New +"** → **"Web Service"**
3. Conecte sua conta GitHub
4. Selecione repositório: **"todox-v76"**

### **2. Configurar Serviço:**

```
Name: todox-backend
Environment: Python 3
Branch: main
Root Directory: backend
Build Command: pip install -r requirements_simple.txt
Start Command: python main_simple.py
```

### **3. Configurações Avançadas:**

```
Instance Type: Free
Environment Variables:
- PORT: (deixar em branco - Render define automaticamente)
- CORS_ORIGINS: https://todox-ps7kl945j-gustavos-projects-f036da2e.vercel.app,http://localhost:3000
```

### **4. Deploy:**

- Clique: **"Create Web Service"**
- Aguardar: 5-10 minutos para build
- URL será: `https://todox-backend-[random].onrender.com`

## 📝 CHECKLIST:

- [ ] Conectar GitHub
- [ ] Configurar build commands
- [ ] Definir environment variables
- [ ] Iniciar deploy
- [ ] Copiar URL final
- [ ] Atualizar frontend

---

**🎯 PRÓXIMO:** Após deploy, atualizaremos o frontend para usar a nova URL!
