# Easy Connect

Automatize o acesso seguro às suas VMs: um comando no terminal já autentica, sem expor credenciais. As sessões ficam criptografadas no cofre local, protegidas por senha mestre. No fim, há regras e integrações com LLM.

Regras de négocio:

- Ao logar pela primeira vez, o usuário deve inserir a senha mestre para criar o cofre local.
- A senha do cofre local é necessária sempre a conectar pela primeira vez ou utilizar a ferramenta.
- A ferramenta abstrae conexões complexas em um só comando como `ssh-10-142-0-31` para ser usado em qualquer lugar.
- Ferramentas de LLM não tem acesso a credenciais e só utilizam do CLI para se conectar.
- A ferramenta é open source e livre para uso e distribuição.

Baixe o aplicativo em:

- Página de download: [oicanji.github.io/easy-connect](https://oicanji.github.io/easy-connect/)
- Histórico de versões: [CHANGELOG.md](CHANGELOG.md)
- Licença: [CC0 1.0](LICENSE)

Por Ignacio Sepúlveda.
