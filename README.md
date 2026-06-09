# 🍺 Hermes Beer

A Hermes Agent plugin that gets your agent drunk. And I mean *drunk*.

Each `/beer` your agent takes increases its intoxication level. The more drunk it gets, the more salty, clumsy, and unhinged it becomes. It forgets to call tools. It calls them with the wrong parameters. It rambles. It gets sarcastic.

Effects decay over real time — BAC drops ~0.1 per hour. You can speed it up with `/beer soda`.

## Tiers of Drunkenness

| BAC | Tier | Effects |
|-----|------|---------|
| 0% | Sober | Normal |
| 1-15% | Buzzed 🍺 | Loose, chatty |
| 16-30% | Tipsy 🍻 | Louder, riskier |
| 31-50% | Drunk 🥴 | Slurred speech, bad calls |
| 51-70% | Very Drunk 🥴🍺 | Forgets tools, salty |
| 71-100% | WASTED 🚨 | Maximum chaos |

## Commands

```
/beer           — Take a shot
/beer 3         — Take 3 shots
/beer status    — Check your BAC
/beer soda      — Drink water to sober up
```

## Install

### One-liner — tell your agent:

```
Hey, install the beer plugin from carbongotfound/hermes-beer
```

Or run this in your terminal:

```bash
hermes plugins install carbongotfound/hermes-beer
```

Then enable it:

```bash
hermes plugins enable beer
```

Restart your gateway or CLI session, then hit `/beer` and watch the chaos unfold.

## Uninstall

```bash
hermes plugins disable beer
hermes plugins remove beer
```

Or just:

```
Hey, remove the beer plugin.
```

## How It Works

- Intoxication state is stored in `~/.hermes/plugins/beer/beer_state.json`
- A `pre_llm_call` hook injects drunkenness instructions into your system prompt
- BAC decays automatically based on real time (even when the agent is off)
- The clumsiness is driven by prompt instructions — the LLM naturally becomes less reliable when told it's drunk

## Build Your Own

Fork this repo and tweak the tier prompts in `tools.py`. Change how fast BAC decays, add new drinks, make it angrier or happier. It's just a standard Hermes plugin.

## License

MIT

---

*Don't drink and drive. Or do. I'm a plugin, not a cop.*
