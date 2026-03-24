import type { SiteConfig } from '@mcptoolshop/site-theme';

export const config: SiteConfig = {
  title: 'Star Freight',
  description: 'Text-first tactics merchant RPG. Five civilizations, one economy, four truths that won\'t let you play the same life twice.',
  logoBadge: 'SF',
  brandName: 'Star Freight',
  repoUrl: 'https://github.com/mcp-tool-shop-org/star-freight',
  footerText: 'MIT Licensed — built by <a href="https://mcp-tool-shop.github.io/" style="color:var(--color-muted);text-decoration:underline">MCP Tool Shop</a>',

  hero: {
    badge: 'Space merchant RPG',
    headline: 'Star Freight:',
    headlineAccent: 'Trade. Decide. Survive.',
    description: 'Lead a disgraced pilot through a politically fractured star system. Five civilizations. One economy. Four truths that make every run a different captain life.',
    primaryCta: { href: '#quickstart', label: 'Get started' },
    secondaryCta: { href: 'handbook/', label: 'Read the Handbook' },
    previews: [
      { label: 'Install', code: 'pip install -e ".[tui]"' },
      { label: 'Play', code: 'starfreight tui' },
      { label: 'Test', code: 'python -m pytest tests/ -x -q' },
    ],
  },

  sections: [
    {
      kind: 'features',
      id: 'features',
      title: 'Four Truths',
      subtitle: 'The load-bearing walls. Every system transacts with every other.',
      features: [
        {
          title: 'Crew is Binding Law',
          desc: 'Crew members are capabilities, access gates, and obligations. Lose one and three systems lose capability at once.',
        },
        {
          title: 'Combat is a Campaign Event',
          desc: 'Victory writes salvage and faction heat. Retreat costs cargo and reputation. Defeat means seized goods and injured crew.',
        },
        {
          title: 'Culture is Decision Grammar',
          desc: 'Each civilization has social logic that shapes trade, access, and conflict. Knowledge is reading the room, not reading a codex.',
        },
        {
          title: 'Plot Emerges from Life',
          desc: 'Investigation threads surface through ordinary work. The conspiracy doesn\'t announce itself — you stumble into it by doing the job.',
        },
        {
          title: 'Three Captain Paths',
          desc: 'Relief, Gray, and Honor produce genuinely different lives — different routes, trades, combat profiles, and fears.',
        },
        {
          title: '2,200+ Tests',
          desc: 'Comprehensive suite covering crew binding, grid combat, cultural knowledge, investigation, campaign integration, and dogfood simulation.',
        },
      ],
    },
    {
      kind: 'code-cards',
      id: 'quickstart',
      title: 'Quick Start',
      cards: [
        {
          title: 'Install',
          code: '# Clone and install\ngit clone https://github.com/mcp-tool-shop-org/star-freight.git\ncd star-freight\npip install -e ".[tui]"',
        },
        {
          title: 'Play',
          code: '# Launch the TUI\nstarfreight tui\n\n# Controls\n# D Dashboard | C Crew | R Routes\n# M Market | T Station | J Journal\n# F Faction | B Buy | S Sell\n# G Travel | A Advance',
        },
      ],
    },
    {
      kind: 'data-table',
      id: 'civilizations',
      title: 'Five Civilizations',
      subtitle: 'Each shapes trade, access, and conflict differently.',
      columns: ['Civilization', 'Identity', 'Trade Character'],
      rows: [
        ['Terran Compact', 'Bureaucratic human government', 'Safe markets, tight margins, heavy paperwork'],
        ['Keth Communion', 'Arthropod collective, biological calendar', 'Best margins if you understand seasons'],
        ['Veshan Principalities', 'Reptilian feudal houses', 'Formal challenge, direct trade, the Debt Ledger'],
        ['Orryn Drift', 'Mobile broker civilization', 'Neutral, profitable, charges for everything'],
        ['Sable Reach', 'Pirate factions + salvagers', 'No law, highest risk and reward'],
      ],
    },
  ],
};
