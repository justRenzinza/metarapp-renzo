# 🚀 Gerador de Arquivos CALPUFF (.NET MAUI)

App desktop que converte dados meteorológicos METAR + INMET + UpperAir → arquivos prontos para CALPUFF em **1 clique**.

**Saída (4 arquivos):**
- ✅ `radiacao_tratada.csv`
- ✅ `teste2.csv`
- ✅ `upperair_tratado.csv`
- ✅ `UpperAir_2024_Gerado.DAT` (formato CALPUFF)

---

## ⚙️ **PRÉ-REQUISITOS (Instalar Primeiro)**

### **1. Python 3.10+ (OBRIGATÓRIO)**
O projeto usa Python para processar dados. Instale primeiro:

**Windows:**
1. Acesse [python.org](https://www.python.org/downloads/)
2. Baixe "Python 3.10" ou superior
3. Na instalação, **marque "Add Python to PATH"** ✅
4. Clique "Install Now"

**Verificar instalação:**
```bash
python --version
```

### **2. .NET 9 SDK (OBRIGATÓRIO)**
Para compilar e rodar a aplicação:

1. Acesse [dotnet.microsoft.com/download/dotnet/9.0](https://dotnet.microsoft.com/download/dotnet/9.0)
2. Baixe ".NET 9 SDK"
3. Instale normalmente

**Verificar instalação:**
```bash
dotnet --version
```

### **3. Dependências Python**
Abra **CMD** ou **PowerShell** e instale as bibliotecas necessárias:

```bash
pip install netCDF4
pip install pandas
pip install numpy
```

---

## 📥 **COMO BAIXAR E RODAR**

### **Opção A: Código Fonte (.NET MAUI - Desenvolvimento)**

```bash
1. git clone https://github.com/justRenzinza/metarapp-renzo.git
2. cd metarapp-renzo
3. dotnet restore
4. dotnet run
```

**Resultado:** Abre a aplicação desktop.

### **Opção B: Executável Pronto (SEM instalar .NET)**

1. Baixe o arquivo `metarapp.exe` do [GitHub Releases](https://github.com/justRenzinza/metarapp-renzo/releases)
2. **Duplo clique** no `.exe`
3. Pronto! A aplicação abre.

⚠️ **Requisito:** Python + dependências ainda precisam estar instaladas.

---

## 🎯 **COMO USAR O APP (5 minutos)**

### **Passo 1: Preparar Dados**
Tenha 3 arquivos prontos:

```
📁 SBVT.csv           ← Dados METAR (estação 83649)
📁 dados_A612_H_*.txt ← Radiação Solar (INMET)
📁 upperair.csv       ← Dados de altura
```

### **Passo 2: Abrir o App**
- **Desenvolvimento:** `dotnet run`
- **Executável:** Duplo clique no `metarapp.exe`

### **Passo 3: Selecionar Arquivos**

Na interface do app:

```
1️⃣  Clique "Selecionar Arquivo SBVT.csv"
    └─ Escolha seu arquivo SBVT.csv

2️⃣  Clique "Selecionar Arquivo INMET"
    └─ Escolha seu arquivo dados_A612_H_*.txt

3️⃣  Clique "Selecionar Arquivo UpperAir"
    └─ Escolha seu arquivo upperair.csv

4️⃣  Clique "Selecionar Pasta de Destino"
    └─ Escolha onde salvar os resultados

5️⃣  Clique 🚀 "PROCESSAR"
    └─ Aguarde a mensagem ✅ "Sucesso!"
```

### **Passo 4: Verificar Resultado**
Na pasta de destino que você escolheu:

```
✅ radiacao_tratada.csv
✅ teste2.csv
✅ upperair_tratado.csv
✅ UpperAir_2024_Gerado.DAT  ← Pronto pro CALPUFF!
```

---

## 🛠️ **INSTALAÇÃO DETALHADA (Passo a Passo)**

### **Windows 10/11 - Instalar Python**

**1. Abrir CMD:**
- Pressione `Win + R`
- Digite `cmd`
- Pressione `Enter`

**2. Instalar Dependências:**
```bash
pip install netCDF4
pip install pandas
pip install numpy
```

**Resultado esperado:**
```
Successfully installed netCDF4-1.6.x
Successfully installed pandas-2.x.x
Successfully installed numpy-1.x.x
```

---

## 🐛 **Solução de Problemas**

### **Erro: "Python não reconhecido"**
```bash
# Verifique a instalação:
python --version

# Se não funcionar, reinstale Python marcando "Add to PATH"
```

### **Erro: "netCDF4 not found"**
```bash
# Reinstale:
pip install --upgrade netCDF4
```

### **Erro: "netCoreApp.dll not found"** (ao rodar .exe)
- Instale .NET 9 SDK
- OU use a versão "self-contained" do executável (já inclui .NET)

### **App não encontra o script.py**
```bash
# Certifique-se de que script.py está na pasta:
C:\Users\...\metarapp-renzo\script.py
```

---

## 📊 **Arquivos Gerados - Explicação**

| Arquivo | Descrição |
|---------|-----------|
| `radiacao_tratada.csv` | Dados de radiação solar processados |
| `teste2.csv` | Dados de superfície processados |
| `upperair_tratado.csv` | Dados de altura atmosférica processados |
| `UpperAir_YYYY_Gerado.DAT` | **Formato CALPUFF** - pronto pra usar! |

---

## 🚀 **Compilar Executável (Opcional)**

Para criar seu próprio `.exe` de 250MB (self-contained):

```bash
dotnet publish -c Release -r win-x64 --self-contained -p:PublishSingleFile=true
```

Resultado em: `bin/Release/net9.0-windows.../win-x64/publish/metarapp.exe`

---

## 💻 **Tecnologias**

- **Frontend:** .NET MAUI (C#, XAML)
- **Backend:** Python (netCDF4, pandas, numpy)
- **Platform:** Windows 10/11 x64

---

## 🤝 **Contribuições**

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nome`
3. Commit: `git commit -m "Descrição"`
4. Push: `git push origin feature/nome`
5. Pull Request

---

## 📞 **Dúvidas?**

- [GitHub Issues](https://github.com/justRenzinza/metarapp-renzo/issues)
- Desenvolvedor: @justRenzinza

---

**Feito com ❤️ para modelagem de dispersão atmosférica** | MIT License