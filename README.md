# Miku - Telegram Bot

<div align="center">
  <img src="miku.png" alt="Miku Icon" width="300">
  <br>
  <h3>Um bot de Telegram versátil, personalizável e feito com Java</h3>
  <p>
    <img src="https://img.shields.io/badge/Java-17+-007396?style=for-the-badge&logo=java&logoColor=white" alt="Java">
    <img src="https://img.shields.io/badge/Telegram%20Bot%20API-Suportado-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Bot API">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License: MIT">
  </p>
</div>

<br>

## 📋 Índice

- [📌 Sobre](#-sobre)
- [✨ Funcionalidades](#-funcionalidades)
- [🧰 Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [🚀 Como Usar](#-como-usar)
- [🤝 Como Contribuir](#-como-contribuir)
- [📜 Licença](#-licença)

<br>

## 📌 Sobre

**Miku** é um bot de Telegram de propósito geral desenvolvido em Java. Simples, rápido e modular, ele foi criado para facilitar o gerenciamento de grupos, automatizar tarefas e se integrar a diversos serviços via API.

Ideal para:
- Administradores de grupos que precisam de um assistente confiável
- Desenvolvedores que desejam expandir com comandos próprios
- Qualquer pessoa que queira um bot leve e eficiente para seu Telegram

<br>

## ✨ Funcionalidades

### 💬 Comandos Gerais
- Respostas personalizadas a comandos do chat
- Detecção de mensagens específicas com respostas automáticas

### 🛠️ Gerenciamento
- Comandos para admins (silenciar, expulsar, etc.)
- Logs de ações administrativas

### 🌐 Integrações
- Suporte a chamadas de APIs externas (ex: clima, dicionários, moedas)
- Sistema de plugins para adicionar comandos personalizados facilmente

### ⚙️ Personalização
- Configuração por chat
- Arquivo de propriedades para definir prefixos, tokens e regras

<br>

## 🧰 Tecnologias Utilizadas

- **Java 17+** – Linguagem principal
- **Telegram Bot API** – Comunicação com o Telegram
- **Gson / Jackson** – Manipulação de JSON (para integrações)
- **Apache HttpClient / OkHttp** – Requisições HTTP (APIs externas)

<br>

## 🚀 Como Usar

### Pré-requisitos

- Java 17 ou superior
- Token do bot obtido com o [BotFather](https://t.me/BotFather)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/tonhowtf/miku.git
cd miku
```

### Compilação

```bash
javac -d bin src/*.java
```

### Execução

```bash
java -cp bin Main
```

> 💡 Configure o token e outras opções no arquivo `config.properties`.

<br>

## 🤝 Como Contribuir

Contribuições são super bem-vindas! Aqui está como você pode ajudar:

1. Faça um **fork** do repositório.
2. Crie uma **branch** para sua feature ou correção:
   ```bash
   git checkout -b minha-feature
   ```
3. Commit suas alterações:
   ```bash
   git commit -m "Adiciona nova funcionalidade"
   ```
4. Envie para seu fork:
   ```bash
   git push origin minha-feature
   ```
5. Abra um **Pull Request**.

<br>

## 📜 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

---

<div align="center">
  <p>
    Feito com ❤️ para a 25
  </p>
</div>
