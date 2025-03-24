# Linux Customizer

![Linux Customizer](https://img.shields.io/badge/Linux-Customizer-brightgreen)
![Python](https://img.shields.io/badge/Python-3.6+-blue)

## Visão Geral

O Linux Customizer é uma ferramenta de personalização completa que permite aos usuários modificar vários aspectos de seu ambiente Linux através de uma interface de linha de comando amigável. A ferramenta utiliza arte ASCII colorida para melhorar a experiência visual e oferece uma ampla gama de opções de personalização.

## Características

- **Interface ASCII-art** - Banners e menus visualmente atraentes
- **Personalização do Ambiente de Desktop** - Altere fundos de tela, temas, ícones e cursores
- **Personalização de Shell** - Configure prompts, aliases e variáveis de ambiente
- **Esquemas de Cores** - Modifique as cores do sistema e alterne entre modos claro/escuro
- **Aparência do Terminal** - Altere fontes, cores e transparência do terminal
- **Gerenciamento de Fontes** - Configure fontes do sistema, documentos e monoespaçadas
- **Gerenciamento de Temas** - Salve, carregue e compartilhe suas configurações personalizadas
- **Feedback em Tempo Real** - Veja as alterações aplicadas imediatamente quando possível

## Requisitos

- Python 3.6 ou superior
- Sistema operacional Linux
- Bibliotecas Python:
  - colorama
  - pyfiglet
  - configparser

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/poyws/LinuxCostumizer/new/main
   cd linux-customizer
   ```

2. Instale as dependências:
   ```bash
   pip install colorama pyfiglet configparser
   ```

3. Execute o programa:
   ```bash
   python linux_customizer.py
   ```

## Estrutura do Projeto

```
├── modules/
│   ├── __init__.py
│   ├── ascii_art.py         # Funções para renderização de arte ASCII
│   ├── color_customizer.py  # Personalização de esquemas de cores
│   ├── config_manager.py    # Gerenciador de configurações
│   ├── desktop_customizer.py # Personalização de ambiente desktop
│   ├── font_customizer.py   # Personalização de fontes
│   ├── shell_customizer.py  # Personalização de shell
│   ├── terminal_customizer.py # Personalização de terminal
│   ├── theme_manager.py     # Gerenciador de temas
│   └── utils.py             # Funções utilitárias
└── linux_customizer.py      # Ponto de entrada principal
```

## Como Usar

1. Execute o programa:
   ```bash
   python linux_customizer.py
   ```

2. Navegue pelos menus usando o teclado numérico:
   - Digite o número da opção desejada e pressione Enter
   - Use a opção 0 para voltar ao menu anterior ou sair

3. Aplique as configurações:
   - A maioria das alterações pode ser aplicada imediatamente
   - Use a opção "Apply Current Settings" no menu principal para aplicar todas as alterações

4. Gerenciamento de temas:
   - Salve suas configurações personalizadas como um tema
   - Carregue temas existentes para aplicar configurações rapidamente
   - Exporte e importe temas para compartilhar com outros

## Limitações

- Algumas funcionalidades podem estar limitadas dependendo do ambiente de desktop específico
- Certas personalizações podem exigir direitos de administrador
- O suporte a alguns terminais e shells menos comuns pode ser limitado

## Solução de Problemas

Se você encontrar problemas:

1. Verifique se todas as dependências estão instaladas
2. Certifique-se de que está executando em um sistema Linux suportado
3. Algumas personalizações podem exigir pacotes adicionais do sistema

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests ou abrir issues para melhorias, correções de bugs ou novas funcionalidades.
