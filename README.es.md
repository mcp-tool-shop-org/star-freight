<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.md">English</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
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

Fuiste piloto militar. Luego, fuiste un deshonrado. Ahora eres capitán de un barco en mal estado, sin influencia y en un sistema estelar que ya estaba en movimiento cuando llegaste.

**Star Freight** es un RPG táctico de comercio centrado en la narrativa, donde transportas mercancías a través de un sistema estelar políticamente fragmentado. Cinco civilizaciones. Una economía. Cuatro verdades que no te permitirán vivir la misma vida dos veces.

---

## El juego

Aterrizas en estaciones donde la cultura influye en cómo negocias. Eliges rutas donde el terreno afecta a cómo luchas. Contratas a tripulantes que cambian lo que puedes hacer, a lo que puedes acceder y lo que debes. Aceptas contratos que parecen sencillos hasta que la burocracia se complica, la escasez cambia el precio o la carga resulta ser evidencia.

No eres el elegido. Eres un capitán que intenta mantener un barco en funcionamiento mientras las instituciones confiscan la carga, las escasez alteran las rutas, la tripulación genera obligaciones y las peligrosas verdades emergen a través del trabajo diario.

Cada viaje se convierte en una vida diferente como capitán. No porque hayas elegido una clase, sino porque tu tripulación, tus rutas, tus riesgos y tu reputación te moldean en alguien.

## Por qué se siente diferente

La mayoría de los RPGs combinan sistemas uno al lado del otro. Star Freight hace que interactúen.

**La tripulación es ley vinculante.** Thal no es un bono del +10% en reparaciones. Thal es *por qué* puedes aterrizar en las estaciones de Keth, *por qué* tu nave tiene una capacidad de reparación de emergencia y *por qué* notaste que la carga médica no coincidía con la temporada. Pierde a Thal, y tres sistemas pierden funcionalidad al mismo tiempo.

**El combate es un evento de campaña.** No entras en una batalla y sales. La victoria genera créditos de rescate y "calor" de facción. La retirada cuesta carga abandonada y una reputación de cobarde. La derrota significa carga confiscada, tripulación herida y una nave que llega a la estación más cercana a un precio elevado. Cada resultado cambia tu próxima decisión comercial.

**La cultura es lógica social.** Los Keth no solo tienen precios diferentes. Tienen un calendario biológico estacional que cambia lo que significa dar regalos, cuándo ofrecer un trato es una ofensa y cuándo a los forasteros se les confina al anillo exterior. Los Veshan no solo luchan. Desafían, y rechazar es peor que perder. El conocimiento no es un compendio. Es leer la situación.

**La investigación emerge de la vida.** Notas que la carga médica no coincide con la temporada porque has estado transportándola. Encuentras la discrepancia en el manifiesto porque rescataste un naufragio. Tu miembro de la tripulación Keth interpreta el patrón porque recuerda su deuda con el mismo proveedor. La conspiración no se anuncia. Te topas con ella al hacer tu trabajo.

## El mundo

Cinco civilizaciones comparten un sistema estelar llamado el Umbral.

**El Compacto Terrano** — Gobierno humano burocrático. Te deshonraron. Recuperar tu posición implica permisos, paciencia y humildad. Mercados seguros, márgenes estrechos, mucha burocracia.

**La Comunión Keth** — Colectivo de artrópodos con un calendario biológico. Pacientes, observadores y devastadores cuando se les ofende. Los mejores márgenes del sistema si entiendes las estaciones. El colapso de reputación más rápido si no lo haces.

**Los Principados Veshan** — Casas feudales reptilianas obsesionadas con el honor y la deuda. Luchan formalmente, comercian directamente y recuerdan todo. El Libro de Deudas no es solo un detalle. Es un punto de palanca.

**La Deriva Orryn** — Civilización de intermediarios móviles. Neutral por política, rentable por diseño. Comercian con todos, saben todo y cobran por ello. Evitarlos ahorra dinero. Perder su buena voluntad cuesta más.

**La Frontera Sable** — Facciones piratas, recuperadores de tecnología ancestral y personas que la Compacta preferiría olvidar. No hay leyes. No hay costumbres. No hay reembolsos. El mayor riesgo y la mayor recompensa del sistema.

## Tres tipos de capitán

El mismo mundo. Tres presiones diferentes.

**Capitán de escolta.** Disciplina de convoy, acceso basado en la confianza, consecuencias públicas. Mantienes a la gente alimentada y te ves atrapado por la legitimidad. Temes los retrasos y la falta de capacidad.

**Contrabandista.** Aprovechamiento de la burocracia, abuso del tiempo, riesgo institucional. Ganas dinero siendo difícil de descifrar. Temes el decomiso y la exposición.

**Capitán honorable.** Confrontación directa, política interna, volatilidad de la reputación. Resuelves los problemas cara a cara. Temes la escalada y las redes de apoyo débiles.

Estos no son clases. Son lo que tus elecciones te han convertido.

## Inicio rápido

```bash
# Clone and install
git clone https://github.com/mcp-tool-shop-org/star-freight.git
cd star-freight
pip install -e ".[tui]"

# Start a new game
starfreight new "Captain Nyx" --type merchant
starfreight tui
```

**Controles:** `D` Panel | `C` Tripulación | `R` Rutas | `M` Mercado | `T` Estación | `J` Diario | `F` Facción | `B` Comprar | `S` Vender | `G` Viajar | `A` Avanzar

## Estado actual

Star Freight es un producto probado, no un concepto de diseño.

| | Conteo |
|---|---|
| Estaciones | 9 |
| Rutas espaciales | 14 |
| Mercancías | 18 |
| Miembros de la tripulación | 5 + jugador |
| Contratos | 9 |
| Encuentros | 6 |
| Pistas de investigación | 4 |
| Pruebas superadas | 2,200+ |

La versión completa ha superado los tres criterios de prueba: Camino Dorado (vida de capitán continua), Encuentro (tres ramas con diferentes estados de campaña) y Economía (la presión se mantiene sin colapsar en una rutina).

Se han incluido tres paquetes de expansión: Vidas Laborales (textura humana), Casas, Auditorías y Decomisos (presión institucional) y Escasez, Sanciones y Convoys (escasez controlada).

La divergencia del camino del capitán está probada: tres posturas producen rutas diferentes, diferentes combinaciones comerciales, diferentes perfiles de combate, diferentes texturas de fracaso y diferentes identidades de capitán.

## Hoja de evaluación de la nave

| Puerta | Estado | Evidencia |
|------|--------|----------|
| A. Seguridad | PASADO | SECURITY.md, solo sin conexión, sin secretos/telemetría |
| B. Errores | PASADO | 2200+ pruebas, validación de campaña estructurada |
| C. Documentación | PASADO | README (8 idiomas), REGISTRO DE CAMBIOS, LICENCIA, MANIFESTO |
| D. Mantenimiento | PASADO | CI (Python 3.11+3.12), v1.0.0, flujo de trabajo con control de acceso |
| E. Pulido | PASADO | Logotipo, traducciones, control de calidad de términos marítimos |

## Tecnología

Python 3.11+. Interfaz de usuario basada en texto. Vinculación de la tripulación, combate por cuadrícula, conocimiento cultural, investigación y orquestación de la campaña. 2200+ pruebas.

No hay dependencias de IA externas. No hay servicios en la nube. Funciona en tu máquina.

**Modelo de amenazas:** Star Freight es un juego para un solo jugador que se ejecuta sin conexión. Solo utiliza archivos de guardado locales. NO accede a la red, recopila datos de telemetría, almacena credenciales ni requiere cuentas de usuario. Las dependencias son Typer, Rich y Textual, todas bien mantenidas y sin código nativo. Consulta [SECURITY.md](SECURITY.md) para obtener la política completa.

## La regla general

Cuando no estés seguro de qué construir a continuación:

- ¿Refuerza alguna de las cuatro verdades?
- ¿Mejora la vida de un capitán?
- ¿Crea una decisión que el jugador pueda sentir?

Si no, puede esperar.

---

*Star Freight es un juego sobre moverse a través de sistemas de poder sin pertenecer completamente a ellos.*

Creado por <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
