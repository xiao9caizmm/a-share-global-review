---
name: a-share-global-review
description: Integrated A-share daily review workflow combining evening A-share short/quant review with morning global-market mapping and optional SMTP email delivery. Use when asked for 晚间复盘, 早间复盘, 全球市场映射A股, 美股映射A股, 美股大涨板块, 商品/黄金/白银映射, 早间消息面复盘, 邮件发送复盘, or a full A股盘前/盘后复盘 system.
---

# A股全球映射复盘 Skill

Use this skill to build a two-stage A-share review system:

- **晚间复盘**: summarize today's A-share market evidence using `a-share-short-review` and `quant-test`.
- **早间复盘**: before the next A-share open, add overnight US market, theme-basket, commodity, precious-metal, and news catalysts, then revise the A-share opening plan.

This skill coordinates existing skills; it does not replace them.

## Operating Modes

Choose the mode from the user's wording:

- `晚间`: write only the A-share evening review and next-day plan.
- `早间`: write only the global mapping brief for the coming A-share session.
- `完整`: write both, or append the morning update to the prior evening view.

If the user gives only one A-share date, treat that as the A-share target date. For a morning brief, use the most recent completed US session and same-morning news before the A-share open. If either market was closed, label it as a holiday/non-trading session and do not invent data.

## Data Source Priority

### A-share evening data

Use the existing skills first:

1. `a-share-short-review`: A-share market breadth, limit-up/down, new highs, ladder, style.
2. `quant-test`: 880005 emotion clock, quantitative score, main-line ranking, stock pool, windows, position discipline.
3. Fallbacks follow those skills: MXSKILLS first, Eastmoney public APIs second, reputable public review sources third.

Hard rule: 涨停、跌停、炸板、封板率、连板梯队、连板晋级率 use non-ST口径 by default. Exclude names containing `ST`, `*ST`, `S*ST`, or `退市` unless the user explicitly asks to include ST.

Also collect `回头波` risk from the A-share evening review. `回头波 = (日内最高价 - 收盘价) / 日内最高价 * 100%`; count non-ST stocks where `回头波 > 8%`. Use it to judge intraday fade and chasing-loss pressure before applying US/global catalysts.

### US market and theme data

Use low-frequency public sources:

1. Alpha Vantage `TOP_GAINERS_LOSERS` for US top gainers, top losers, and most active.
2. Daily prices for US indices and ETFs from a public EOD source such as Alpha Vantage, Nasdaq, Stooq, or Yahoo/yfinance fallback. Label unofficial fallback.
3. Nasdaq, Finviz, Barchart, Yahoo Finance, company IR, SEC filings, and reputable news pages for cross-checking catalysts.

Core US index set:

| Metric | Symbols |
| --- | --- |
| US indices | `SPY`, `QQQ`, `DIA`, `IWM`, `SOXX` or `SMH` |
| Rates/currency background | US 10Y yield, DXY, USD/CNH when available |
| Sector ETFs | `XLK`, `XLF`, `XLV`, `XLY`, `XLP`, `XLE`, `XLI`, `XLB`, `XLU`, `XLRE`, `XLC` |

### Commodity and precious-metal data

Pull a small commodity watchlist and output only the top three gainers and top three losers by daily percent change.

Suggested futures/ETF proxies:

| Category | Symbols |
| --- | --- |
| Precious metals | `GC=F` gold, `SI=F` silver, `PL=F` platinum, `PA=F` palladium |
| Energy | `CL=F` WTI crude, `BZ=F` Brent crude, `NG=F` natural gas |
| Industrial metals | `HG=F` copper, aluminum/zinc/nickel proxies when available |
| Agriculture optional | `ZS=F` soybean, `ZC=F` corn, `ZW=F` wheat, `CT=F` cotton |

Commodity moves only affect macro style and resource-sector priority. They cannot independently define an A-share main line.

### Morning news

Collect only fresh, directional messages that can map to A-shares:

- Domestic finance/policy: 财联社, 东方财富资讯, 证券时报, 中国证券报, official ministries/exchanges.
- Overseas macro: Reuters/CNBC/MarketWatch/Fed/BLS/Treasury public releases when available.
- Tech/industry: company IR, Nasdaq/Yahoo Finance, SEC 8-K, credible semiconductor/AI/data-center news.
- Commodities: Kitco, OilPrice, EIA/IEA/OPEC, exchanges, or reputable financial news.

Classify each message as `强催化`, `中催化`, `弱催化`, or `负催化`. A message enters the opening plan only if it is fresh, directional, price-confirmed, and can map to A-share core stocks.

## US Theme Baskets And A-share Mapping

Judge US signals by basket resonance, not one stock alone. A single stock can be company-specific; a theme becomes useful when multiple names or a sector ETF confirm.

| US theme | US watchlist | A-share mapping |
| --- | --- | --- |
| Optical/CPO/data-center networking | `LITE`, `COHR`, `AAOI`, `CIEN`, `ANET`, `AVGO`, `MRVL`, `CRDO` | CPO, 光模块, 光通信, AI算力硬件 |
| AI compute/server chain | `NVDA`, `AMD`, `AVGO`, `MRVL`, `ARM`, `SMCI`, `DELL`, `VRT` | 服务器, PCB, 液冷, 铜缆, 光模块, 电源 |
| Semiconductor equipment/storage | `AMAT`, `LRCX`, `KLAC`, `ASML`, `TER`, `MU`, `WDC` | 半导体设备, 先进封装, 存储 |
| Robotics/automation | `TSLA`, `ISRG`, `SYM`, `TER`, `ROK`, `ABBNY` | 人形机器人, 减速器, 伺服, 电机 |
| Crypto | `COIN`, `MSTR`, `MARA`, `RIOT`, `IBIT` | 金融科技, 算力, 区块链概念 |
| Biotech | `XBI`, `IBB`, `MRNA`, `BIIB`, `REGN`, `VRTX` | 创新药, CXO, 医疗服务 |
| Energy | `XLE`, `XOM`, `CVX`, `SLB`, `OXY` | 油气, 油服, 煤化工 |
| Precious metals | `GLD`, `SLV`, `NEM`, `GOLD`, `AEM` | 黄金, 白银, 贵金属, 有色 |

Transmission strength:

- `强`: theme basket rises together, catalyst is industry-level, and A-share prior evening review already shows matching main-line strength or divergence return.
- `中`: one or two core US names rise with a plausible catalyst, but A-share prior evidence is only rotation or unconfirmed.
- `弱`: single-stock earnings, buyback, M&A, short squeeze, or no A-share mapping.
- `负`: US theme breaks down, commodity shock hurts the mapped A-share direction, or news is regulatory/negative.

US/global signals can add to `叙事催化` and `次日观察优先级`; they must not override A-share 880005, market breadth, volume, main-line scoring, or opening verification.

## Evening Review Workflow

1. Confirm target A-share trading date and previous trading day.
2. Use `a-share-short-review` to collect market data and write the short-review structure.
3. Use `quant-test` to calculate 880005 emotion clock, quantitative score, six-direction main-line ranking, stock pool, windows, and position cap.
4. Ensure all limit-up/down statistics use non-ST口径.
5. Include `回头波风险统计`: count non-ST stocks with `回头波 > 8%`, show concentrated themes and representative names, and state whether intraday fade weakens any main-line continuation.
6. Save evening integrated A-share files under `A股复盘/全球映射早盘复盘` unless the user specifies another folder. Suggested filename: `YYYYMMDD A股全球映射复盘.md` or keep the user's naming convention.

Required evening sections:

1. `◆ 一、晚间核心结论`
2. `◆ 二、A股市场全景`
3. `◆ 三、创新高历史个股分析`
4. `◆ 四、连板梯队与涨跌停结构`
5. `◆ 五、回头波风险统计`
6. `◆ 六、主线板块量化排名`
7. `◆ 七、选股观察池`
8. `◆ 八、明日窗口计划`
9. `◆ 九、仓位与纪律`
10. `◆ 十、风险提示`

## Morning Global Mapping Workflow

1. Identify the most recent completed US session and current A-share target session.
2. Pull US indices, semiconductor ETF, sector ETFs, top gainers/losers/most active, and theme baskets.
3. Pull commodity/precious-metal watchlist and list top three gainers plus top three losers.
4. Search fresh morning news and classify catalysts.
5. Compare with the prior evening A-share main-line ranking and 回头波风险统计. State which A-share directions rise or fall in priority.
6. Output only an opening plan. Do not turn overnight signals into direct buy instructions.
7. Save morning global-mapping files under `A股复盘/全球映射早盘复盘` unless the user specifies another folder. Suggested filename: `YYYYMMDD 全球市场映射A股早间复盘.md`.
8. If email delivery is requested or configured, send a second copy as HTML email using the rules below. Do not send raw Markdown as the email body.

## Optional Email Delivery

This skill can send a mobile-friendly HTML email copy of the generated review, but credentials must be configured by the user. Never hard-code or commit real SMTP passwords, authorization codes, or recipient addresses into the skill.

Use bundled script `scripts/send_review_email.py` after the Markdown file is generated:

```powershell
$env:A_SHARE_REVIEW_SMTP_HOST='smtp.qq.com'
$env:A_SHARE_REVIEW_SMTP_PORT='465'
$env:A_SHARE_REVIEW_SMTP_USER='your_sender@qq.com'
$env:A_SHARE_REVIEW_SMTP_PASS='your_smtp_authorization_code'
$env:A_SHARE_REVIEW_TO='recipient@qq.com'
python 'C:\Users\33256\.codex\skills\a-share-global-review\scripts\send_review_email.py' --file 'A股复盘\全球映射早盘复盘\YYYYMMDD全球市场映射A股早间复盘.md' --subject 'YYYYMMDD A股全球映射早盘复盘'
```

Configuration rules:

- QQ Mail uses `smtp.qq.com` with SSL port `465`.
- `A_SHARE_REVIEW_SMTP_PASS` should be the mailbox SMTP authorization code/app password, not the login password.
- `A_SHARE_REVIEW_TO` may contain one or more recipients separated by commas.
- If any required field is missing, do not guess. Ask the user to configure it or skip email delivery.
- The email body must be generated from the Markdown review as styled HTML with a single-column, phone-readable layout and compact tables.
- The Markdown file is still saved under `A股复盘/全球映射早盘复盘`; email is only an additional delivery channel.

Required morning sections:

1. `◆ 一、隔夜核心结论`
2. `◆ 二、全球市场全景`
3. `◆ 三、美股主题篮子表现`
4. `◆ 四、美股重点异动个股`
5. `◆ 五、商品/贵金属涨跌幅前三`
6. `◆ 六、早间消息面`
7. `◆ 七、对A股晚间复盘的修正`
8. `◆ 八、A股开盘验证计划`
9. `◆ 九、风险提示`

Required morning tables:

US theme table:

| 美股主题 | 代表标的 | 涨跌幅/表现 | 是否共振 | A股映射方向 | 传导等级 | 处理 |
| --- | --- | --- | --- | --- | --- | --- |

US movers table:

| 美股 | 涨跌幅 | 所属链条 | 催化原因 | A股映射 | 传导等级 |
| --- | ---: | --- | --- | --- | --- |

Commodity table:

| 排名 | 商品 | 涨跌幅 | 类别 | A股映射方向 | 判断 |
| --- | --- | ---: | --- | --- | --- |

News table:

| 消息 | 来源/时间 | 影响方向 | 催化等级 | A股映射 | 处理 |
| --- | --- | --- | --- | --- | --- |

## Opening Verification Rules

Use this plan every morning:

- `9:15-9:30`: only check auction and emotion. Do not chase just because a US stock or commodity moved.
- `9:30-10:30`: verify whether mapped A-share core stocks open with承接, whether the sector diffuses, and whether volume supports the move.
- `10:30-14:30`: if the index weakens or 880005 is high-hot, prohibit weak dip-buying and back-row chasing.
- `14:30-15:00`: confirm whether the morning mapped theme became a real A-share main line or only a one-day stimulus.

Mandatory discipline:

- If US signal is single-stock only, label it as `个股事件` unless same-chain names confirm.
- If A-share prior evening review shows高潮/high heat, US positive signals only mean `看核心承接`, not `追高后排`.
- If commodity/news signals conflict with A-share market evidence, reduce transmission level.
- If a mapped A-share stock fails the direction-consistency gate from `quant-test`, exclude it from the observation pool.

## Writing Style

Keep the tone direct and trading-log oriented. Start with the conclusion, then show data. Distinguish clearly between:

- `盘面证据`: A-share closing evidence.
- `隔夜催化`: US/global price and news signals.
- `开盘验证`: what must happen before action.

End user-facing reviews with a risk note: this is a review and observation plan, not investment advice.
