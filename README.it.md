<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.md">English</a> | <a href="README.pt-BR.md">Português (BR)</a>
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

Sei stato un pilota militare. Poi sei caduto in disgrazia. Ora sei un capitano con una nave malandata, senza prestigio e in un sistema stellare che era già in movimento quando sei arrivato.

**Star Freight** è un gioco di ruolo mercantile tattico incentrato sulla gestione del trasporto di merci in un sistema stellare politicamente diviso. Cinque civiltà. Un'unica economia. Quattro verità che non ti permetteranno di vivere la stessa vita due volte.

---

## Il gioco

Attracchi in stazioni dove la cultura influenza il modo in cui negozi. Scegli rotte dove il terreno cambia il modo in cui combatti. Assumi membri dell'equipaggio che cambiano ciò che puoi fare, a cosa puoi accedere e cosa devi. Accetti contratti che sembrano semplici finché la burocrazia non si mette in mezzo, la scarsità non cambia i prezzi o il carico si rivela essere una prova.

Non sei l'eletto. Sei un capitano che cerca di mantenere una nave in movimento mentre le istituzioni sequestrano le merci, le carenze modificano le rotte, l'equipaggio porta con sé degli obblighi e pericolose verità emergono attraverso il lavoro quotidiano.

Ogni viaggio diventa una vita diversa da capitano. Non perché hai scelto una classe, ma perché il tuo equipaggio, le tue rotte, i tuoi rischi e la tua reputazione ti hanno trasformato in qualcuno.

## Perché si percepisce come diverso

La maggior parte dei giochi di ruolo impilano i sistemi uno accanto all'altro. Star Freight fa interagire i sistemi.

**L'equipaggio è legge vincolante.** Thal non è un bonus del +10% alla riparazione. Thal è *il motivo* per cui puoi attraccare nelle stazioni di Keth, *il motivo* per cui la tua nave ha una capacità di riparazione di emergenza e *il motivo* per cui hai notato che il carico medico non corrispondeva alla stagione. Perdere Thal significa perdere la funzionalità di tre sistemi contemporaneamente.

**Il combattimento è un evento della campagna.** Non entri in una battaglia e ne esci subito. La vittoria ti fa guadagnare crediti di recupero e aumenta la tua reputazione con le fazioni. La ritirata costa il carico abbandonato e una reputazione di codardo. La sconfitta significa merci sequestrate, membri dell'equipaggio feriti e una nave che si trascina verso la stazione più vicina a un prezzo elevato. Ogni esito cambia la tua prossima decisione commerciale.

**La cultura è logica sociale.** I Keth non hanno solo prezzi diversi. Hanno un calendario biologico stagionale che cambia il significato dei doni, quando fare un'offerta è un insulto e quando gli stranieri sono confinati nell'anello esterno. I Veshan non combattono semplicemente. Si sfidano e rifiutare è peggio che perdere. La conoscenza non è un codice. È leggere la situazione.

**L'indagine emerge dalla vita.** Noti che il carico medico non corrisponde alla stagione perché lo stai trasportando. Trovi la discrepanza nel manifesto perché hai recuperato un relitto. Il tuo membro dell'equipaggio Keth interpreta lo schema perché ricorda il suo debito verso lo stesso fornitore. La cospirazione non si rivela. Ci ci imbatte mentre svolgi il tuo lavoro.

## Il mondo

Cinque civiltà condividono un sistema stellare chiamato Threshold.

**Il Terran Compact** — Governo umano burocratico. Ti hanno fatto cadere in disgrazia. Ritornare significa ottenere permessi, avere pazienza e ingoiare l'orgoglio. Mercati sicuri, margini ridotti, molta burocrazia.

**La Keth Communion** — Collettivo di artropodi con un calendario biologico. Pazienti, osservatori e devastanti quando vengono offesi. I migliori margini di profitto del sistema se capisci le stagioni. Il crollo della reputazione più rapido se non lo fai.

**I Veshan Principalities** — Casate feudali rettiliane ossessionate dall'onore e dal debito. Combattono formalmente, commerciano direttamente e ricordano tutto. Il Registro dei Debiti non è solo un dettaglio. È un'arma di pressione.

**L'Orryn Drift** — Civiltà di broker mobili. Neutri per politica, redditizi per design. Commerciano con tutti, sanno tutto e fanno pagare per entrambi. Evitarli fa risparmiare denaro. Perdere la loro benevolenza costa di più.

**La Frontiera Oscura** — Fazioni piratesche, recuperatori di tecnologia ancestrale e persone che la Compagnia preferirebbe dimenticare. Nessuna legge. Nessuna consuetudine. Nessun rimborso. Il rischio più alto e la ricompensa più grande del sistema.

## Tre tipi di capitano

Lo stesso mondo. Tre pressioni diverse.

**Capitano di servizio.** Disciplina della scorta, accesso basato sulla fiducia, conseguenze pubbliche. Mantenete le persone nutrite e rimanete intrappolati nella legittimità. Temete i ritardi e la capacità insufficiente.

**Corriere grigio.** Pressione istituzionale, sfruttamento dei tempi, rischio istituzionale. Guadagnate denaro rimanendo enigmatici. Temete le confische e le rivelazioni.

**Capitano d'onore.** Confronto diretto, politica interna, volatilità della reputazione. Risolvete i problemi a viso aperto. Temete l'escalation e le reti di supporto limitate.

Queste non sono classi. Sono ciò in cui le vostre scelte vi hanno trasformato.

## Guida rapida

```bash
# Clone and install
git clone https://github.com/mcp-tool-shop-org/star-freight.git
cd star-freight
pip install -e ".[tui]"

# Start a new game
starfreight new "Captain Nyx" --type merchant
starfreight tui
```

**Controlli:** `D` Cruscotto | `C` Equipaggio | `R` Rotte | `M` Mercato | `T` Stazione | `J` Diario | `F` Fazione | `B` Acquista | `S` Vendi | `G` Viaggia | `A` Avanza

## Stato attuale

Star Freight è un prodotto collaudato, non un concetto di design.

| | Conteggio |
|---|---|
| Stazioni | 9 |
| Vie spaziali | 14 |
| Merci commerciali | 18 |
| Membri dell'equipaggio | 5 + giocatore |
| Contratti | 9 |
| Incontri | 6 |
| Filoni di indagine | 4 |
| Test superati | 2,200+ |

La versione completa ha superato tutti e tre i criteri di validazione: Percorso ideale (vita del capitano coerente), Incontro (tre rami con diversi stati della campagna) ed Economia (la pressione rimane sostenibile senza degenerare in ripetitività).

Sono stati distribuiti tre pacchetti di espansione: Working Lives (approfondimento della condizione umana), Houses, Audits, and Seizures (pressione istituzionale) e Shortages, Sanctions, and Convoys (scarsità gestita).

La divergenza del percorso del capitano è stata dimostrata: tre approcci producono percorsi diversi, combinazioni commerciali diverse, profili di combattimento diversi, texture di fallimento diverse e identità di capitano diverse.

## Scheda di controllo della nave

| Porta | Stato | Prove |
|------|--------|----------|
| A. Sicurezza | PASS | SECURITY.md, solo offline, nessuna informazione sensibile/telemetria |
| B. Errori | PASS | 2200+ test, validazione strutturata della campagna |
| C. Documentazione | PASS | README (8 lingue), CHANGELOG, LICENZA, MANUALE |
| D. Manutenzione | PASS | CI (Python 3.11+3.12), v1.0.0, flusso di lavoro con controllo delle versioni |
| E. Rifiniture | PASS | Logo, traduzioni, controllo della terminologia marittima tramite CI |

## Tecnologia

Python 3.11+. Interfaccia utente testuale avanzata. Collegamento dell'equipaggio, combattimento a griglia, conoscenza culturale, indagine e orchestrazione della campagna. 2200+ test.

Nessuna dipendenza da intelligenza artificiale esterna. Nessun servizio cloud. Funziona sulla tua macchina.

**Modello di minaccia:** Star Freight è un gioco per giocatore singolo e offline. Accede solo ai file di salvataggio locali. NON accede alla rete, non raccoglie dati di telemetria, non memorizza credenziali e non richiede account utente. Le dipendenze sono Typer, Rich e Textual, tutte ben mantenute e senza codice nativo. Consultare [SECURITY.md](SECURITY.md) per la politica completa.

## La regola fondamentale

Quando non si è sicuri di cosa costruire successivamente:

- Rafforza una delle quattro verità fondamentali?
- Migliora la vita di un capitano?
- Crea una decisione che il giocatore possa percepire?

Se la risposta è no, può aspettare.

---

*Star Freight è un gioco che parla di come muoversi all'interno di sistemi di potere senza mai appartenervi completamente.*

Creato da <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
