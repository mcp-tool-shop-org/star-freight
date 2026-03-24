<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.md">English</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/star-freight/readme.png" alt="Star Freight — Trade. Decide. Survive." width="400">
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/star-freight/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/star-freight/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  <a href="https://mcp-tool-shop-org.github.io/star-freight/"><img src="https://img.shields.io/badge/landing_page-live-brightgreen" alt="Landing Page"></a>
</p>

# Star Freight

Você era um piloto militar. Depois, você se tornou um escândalo. Agora, você é um capitão com uma nave problemática, sem prestígio, e um sistema estelar que já estava em movimento quando você chegou.

**Star Freight** é um RPG de estratégia e comércio focado em texto, onde você transporta cargas através de um sistema estelar politicamente fragmentado. Cinco civilizações. Uma economia. Quatro verdades que não permitem que você viva a mesma vida duas vezes.

---

## O jogo

Você atraca em estações onde a cultura influencia a forma como você negocia. Você escolhe rotas onde o terreno afeta a forma como você luta. Você contrata tripulação que muda o que você pode fazer, o que você pode acessar e o que você deve. Você aceita contratos que parecem simples até que a papelada se torne um problema, a escassez altera o preço ou a carga se revela uma evidência.

Você não é o escolhido. Você é um capitão trabalhador tentando manter uma nave em movimento enquanto instituições apreendem cargas, a escassez redefine rotas, a tripulação traz obrigações a bordo e verdades perigosas vêm à tona através do trabalho cotidiano.

Cada viagem se torna uma vida de capitão diferente. Não porque você escolheu uma classe, mas porque sua tripulação, suas rotas, seus riscos e sua reputação moldam você em alguém.

## Por que isso parece diferente

A maioria dos RPGs combina sistemas lado a lado. Star Freight faz com que eles interajam.

**A tripulação é lei vinculante.** Thal não é apenas um bônus de +10% no reparo. Thal é *o motivo* de você poder atracar nas estações de Keth, *o motivo* de sua nave ter uma capacidade de reparo de emergência e *o motivo* de você ter notado que a carga médica não correspondia à estação do ano. Perder Thal significa que três sistemas perdem capacidade ao mesmo tempo.

**O combate é um evento de campanha.** Você não entra em uma luta e sai dela. A vitória gera créditos de sucata e "calor" da facção. A retirada custa carga descartada e uma reputação de alguém que foge. A derrota significa carga apreendida, tripulação ferida e uma nave que chega cambaleante à estação mais próxima, com um preço alto. Cada resultado muda sua próxima decisão de comércio.

**A cultura é a lógica social.** Os Keth não têm apenas preços diferentes. Eles têm um calendário biológico sazonal que muda o que significa fazer presentes, quando oferecer um negócio é um insulto e quando os forasteiros são confinados ao anel externo. Os Veshan não apenas lutam. Eles desafiam — e recusar é pior do que perder. O conhecimento não é um código. É ler a situação.

**A investigação emerge da vida.** Você percebe que a carga médica não corresponde à estação do ano porque você a transportou. Você encontra a discrepância no manifesto porque recuperou destroços. Sua tripulação Keth interpreta o padrão porque ela se lembra de sua dívida com o mesmo fornecedor. A conspiração não se anuncia. Você se depara com ela ao fazer o trabalho.

## O mundo

Cinco civilizações compartilham um sistema estelar chamado Threshold.

**O Compacto Terrano** — Governo humano burocrático. Eles te humilharam. Voltar significa obter permissões, ter paciência e engolir o orgulho. Mercados seguros, margens estreitas, muita papelada.

**A Comunhão Keth** — Coletivo de artrópodes em um calendário biológico. Pacientes, observadores e devastadores quando ofendidos. As melhores margens do sistema se você entender as estações do ano. O colapso de reputação mais rápido se você não entender.

**Os Principados Veshan** — Casas feudais reptilianas obcecadas com honra e dívida. Eles lutam formalmente, comercializam diretamente e lembram de tudo. O Livro de Dívidas não é apenas um detalhe. É alavancagem.

**A Deriva Orryn** — Civilização de corretores móveis. Neutros por política, lucrativos por design. Eles comercializam com todos, sabem de tudo e cobram por ambos. Ignorá-los economiza dinheiro. Perder a boa vontade deles custa mais.

**A Fronteira Sombria** — Facções de piratas, recuperadores de tecnologia ancestral e pessoas que a Compacta preferiria esquecer. Sem leis. Sem costumes. Sem reembolsos. O maior risco e a maior recompensa do sistema.

## Três tipos de capitão

O mesmo mundo. Três pressões diferentes.

**Capitão de suprimentos.** Disciplina de comboio, acesso baseado na confiança, consequências públicas. Você mantém as pessoas alimentadas e fica preso à legitimidade. Você teme atrasos e capacidade insuficiente.

**Corretor cinzento.** Alavancagem através de documentos, exploração de prazos, risco institucional. Você ganha dinheiro permanecendo enigmático. Você teme apreensões e exposição.

**Capitão de honra.** Confronto direto, política interna, volatilidade da reputação. Você resolve problemas cara a cara. Você teme a escalada e redes de apoio frágeis.

Estas não são classes. São o que suas escolhas o transformaram.

## Guia de início rápido

```bash
# Clone and install
git clone https://github.com/mcp-tool-shop-org/star-freight.git
cd star-freight
pip install -e ".[tui]"

# Start a new game
starfreight new "Captain Nyx" --type merchant
starfreight tui
```

**Controles:** `D` Painel | `C` Tripulação | `R` Rotas | `M` Mercado | `T` Estação | `J` Diário | `F` Facção | `B` Comprar | `S` Vender | `G` Viajar | `A` Avançar

## Estado atual

Star Freight é um produto comprovado, não um conceito de design.

| | Contagem |
|---|---|
| Estações | 9 |
| Rotas espaciais | 14 |
| Mercadorias | 18 |
| Membros da tripulação | 5 + jogador |
| Contratos | 9 |
| Encontros | 6 |
| Linhas de investigação | 4 |
| Testes aprovados | 2,200+ |

A versão completa passou em todos os três critérios de validação: Caminho Dourado (vida de capitão contínua), Encontro (três ramificações com diferentes estados da campanha) e Economia (a pressão se mantém sem entrar em um ciclo repetitivo).

Três pacotes de expansão foram lançados: Working Lives (textura humana), Houses, Audits, and Seizures (pressão institucional) e Shortages, Sanctions, and Convoys (escassez controlada).

A divergência do caminho do capitão foi comprovada: três posturas produzem rotas diferentes, diferentes combinações de comércio, diferentes perfis de combate, diferentes texturas de falha e diferentes identidades de capitão.

## Relatório de verificação da nave

| Portão | Status | Evidências |
|------|--------|----------|
| A. Segurança | APROVADO | SECURITY.md, apenas para uso offline, sem segredos/telemetria |
| B. Erros | APROVADO | Mais de 2200 testes, validação estruturada da campanha |
| C. Documentação | APROVADO | README (8 idiomas), CHANGELOG, LICENÇA, MANUAIS |
| D. Higiene | APROVADO | CI (Python 3.11+3.12), v1.0.0, fluxo de trabalho com restrições de caminho |
| E. Refinamento | APROVADO | Logotipo, traduções, controle de qualidade de termos marítimos |

## Tecnologia

Python 3.11+. Interface de usuário textual avançada. Vinculação da tripulação, combate em grade, conhecimento cultural, investigação e orquestração da campanha. Mais de 2200 testes.

Sem dependências de IA externas. Sem serviços em nuvem. Executa na sua máquina.

**Modelo de ameaças:** Star Freight é um jogo para um único jogador, que funciona offline. Ele acessa apenas arquivos de salvamento locais. NÃO acessa a rede, coleta dados de telemetria, armazena credenciais ou requer contas de usuário. As dependências são Typer, Rich e Textual — todas bem mantidas e sem código nativo. Consulte [SECURITY.md](SECURITY.md) para a política completa.

## A regra fundamental

Quando não tiver certeza do que construir em seguida:

- Isso reforça uma das quatro verdades?
- Isso aprimora a vida de um capitão?
- Isso cria uma decisão que o jogador possa sentir?

Se não, pode esperar.

---

*Star Freight é um jogo sobre navegar em sistemas de poder sem nunca pertencer totalmente a eles.*

Desenvolvido por <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
