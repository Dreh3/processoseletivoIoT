
# Projeto — Sistema de Monitoramento de Temperatura e Abertura de Porta

> **Processo Seletivo – Etapa LabMaker**
>
> **Nome:** Andressa Sousa Fonseca
>
> **GitHub:** https://github.com/Dreh3

---

# Objetivo

Desenvolver um firmware para monitoramento contínuo da abertura de uma porta e da temperatura ambiente utilizando um ESP32, um sensor MPU6050 e um botão simulando o estado da porta.

O sistema detecta automaticamente duas condições de risco, emitindo alertas via comunicação serial. As condições são:

- a porta permanece aberta por tempo superior ao limite configurado, 5000ms;
- ocorre uma variação abrupta de temperatura, maior ou igual a 3.0°C.

Quando ambas as condições são revertidas, o sistema informa a normalização.

---

# Arquitetura da Solução

## Hardware utilizado

| Componente | Função |
|------------|---------|
| ESP32 DevKit | Processamento |
| MPU6050 | Leitura da temperatura |
| Botão (`btn1`) | Simulação da porta: 1 - aberta e 0 - fechada |
| UART | Envio dos logs |

---

## Estratégia Implementada

A solução foi dividida em dois processos independentes:

### Monitoramento da porta

- leitura contínua do estado do botão;
- utilização de um **Timer ONE_SHOT** para contar o tempo de abertura da porta;
- emissão do alerta caso o timer dispare e a porta continue aberta.

### Monitoramento térmico

- armazenamento de uma temperatura de referência inicial;
- cálculo contínuo do gradiente térmico e atualização da referência quando em ambiente seguro;
- emissão do alerta quando a variação ultrapassa o limite definido.

Os dois monitoramentos executam simultaneamente durante todo o funcionamento do sistema, com um pequeno delay de 100ms.

---

# Estrutura do Código

O projeto foi organizado em quatro partes principais:

| Seção | Responsabilidade |
|--------|------------------|
| Driver MPU6050 | Comunicação I²C e leitura da temperatura |
| Configuração | Inicialização dos periféricos e valores de referência |
| Callback do Timer | Verificação do tempo máximo de porta aberta |
| Loop Principal | Controle dos estados e emissão dos eventos |

---

# Fluxo de Funcionamento

```text
Inicialização
      │
      ▼
Leitura da Porta
      │
      ├────────► Porta aberta?
      │               │
      │               ▼
      │          Inicia Timer    ├────────► Timer dispara?
      │                                         │   
      │                                         ▼
      │                                    Emite Alerta 
      │
      ├────────► Porta fechada?
      │               │
      │               ▼
      │           Para Timer
      │
      ▼
Leitura da Temperatura
      │
      ▼
 Calcula ΔT
      │
      ├────────►  ΔT ≥ limite?
      │               │
      │               ▼
      │               │
      |          ┌────┴─────┐
      |          │          │
      |         Sim        Não
      |          │          │
      |          ▼          ▼
      |         Envia     Estado 
      |        Mensagem  Preservado
      |
Verifica Normalização
```

---


# Principais Decisões de Projeto

### Uso de Timer ao invés de delay

Foi utilizado um **Timer em modo ONE_SHOT** para controlar o tempo de porta aberta.

Essa abordagem foi escolhida porque reduz o trabalho do processamento de ter que verificar constantemente se o tempo foi atingido e permite um acionamento pontual, evitando exceder o tempo estabelecido. Além disso, se a porta é fechada antes, o timer é parado para evitar execuções desnecessárias da função de callback.

---

### Driver simplificado do MPU6050

Como apenas a temperatura era necessária para este desafio, foi implementado o conjunto essencial de funções para comunicação I²C e leitura do registrador de temperatura.

Essa escolha reduz a complexidade do código sem comprometer os requisitos do projeto, deixando-o objetivo e bem direcionado à proposta.

---

### Constantes de configuração

Todos os parâmetros do sistema foram declarados como constantes.

| Constante | Valor |
|-----------|------:|
| LIMITE_TEMPO | 5000 ms |
| LIMITE_VARIACAO | 3.0 °C |

Essa abordagem facilita futuras alterações sem modificar a lógica do programa. Variáveis de controle também foram utilizadas para monitorar os estados do sistema, a fim de emitir os alertas corretamente.

---

# Mensagens Emitidas

| Evento | Mensagem |
|---------|----------|
| Inicialização | Sistema de Monitoramento Inicializado |
| Porta aberta | ALERTA: Porta aberta por muito tempo! |
| Temperatura | ALERTA: Degradacao termica detectada! |
| Normalização | Status: Sistema Normalizado. |

---

# Resultado da Simulação

O ponto crucial do projeto era identificar os estados de alerta corretamente para emitir as mensagens esperadas pelo simulador. Nesse quesito, o projeto funciona corretamente, passando em todos os testes de simulação. 
Todos os requisitos críticos de implementação foram atendidos, atentando-se principalmente para a identificação correta dos componentes de hardware e utilização de uma abordagem direcionada à proposta. 

# Considerações

Durante o desenvolvimento, buscou-se uma implementação que atendesse ao requisitos do cenário escolhido e fosse compatível com os testes automatizados do Wokwi CI, priorizando, nesse caso, o monitoramento contínuo do estado do botão. A utilização do Timer, da leitura contínua dos sensores e da organização modular de execução tornou o firmware mais legível e aplicável ao projeto.

As principais decisões foram motivadas pela necessidade de manter o laço principal não bloqueante, separar as responsabilidades do código e utilizar apenas os recursos necessários para atender aos requisitos do desafio. No entanto, em um ambiente real seria necessário utilizar interrupções e tratamento de debounce para as oscilações do botão, comportamento que não foi identificado no ambiente de simulação durante os testes. Também foi observado que os valores de entrada do botão apresentavam comportamento inverso ao descrito, o valor definido 0 para porta aberta era identificado como 1. Logo, para a execução correta, a lógica de leitura foi invertida.
