# Hyperscaler Capex and AI Infrastructure Evidence

**Run date:** 2026-06-18

**Purpose:** Add primary-source demand-side evidence for AI infrastructure capex and compute build-out. This supports the platform-demand bridge and risk framework, but does not identify PCB suppliers or customer/platform revenue split.

**Raw archive:** `sources/probe-hyperscaler-capex-20260618/`

## Source Coverage

| Company | Source archived | Key extracted evidence | Treatment |
|---|---|---|---|
| Alphabet | `alphabet-2026-q1-earnings-release.pdf`; `.txt` | Q1 2026 revenue release states Google Cloud revenue rose 63% to USD 20.0bn, led by GCP across enterprise AI solutions and enterprise AI infrastructure. CEO says AI investments and full-stack approach are driving the business. Cash-flow table shows Q1 2026 purchases of property and equipment of USD 35.674bn and TTM purchases of USD 109.924bn. | Strong official demand/capex evidence for AI infrastructure. Not supplier allocation. |
| Amazon | `amazon-q1-2026-aboutamazon.html`; `.txt` | Amazon official Q1 2026 release says AWS sales grew 28% to USD 37.6bn. Free cash flow fell due to a USD 59.3bn YoY increase in purchases of property and equipment, primarily reflecting investments in AI. Amazon also says chips business exceeded a USD 20bn annual revenue run rate, OpenAI committed to about 2GW of Trainium capacity, Anthropic secured up to 5GW of Trainium chips, and Amazon landed 2.1mn+ AI chips over the past 12 months plus announced 1mn+ NVIDIA GPUs to deploy from 2026. | Strong official demand and accelerated-compute evidence. Not supplier allocation. |
| Meta | `meta-q1-2026-earnings-call-transcript.pdf`; `.txt` | Q1 2026 capex including finance-lease principal was USD 19.8bn, driven by servers, data centers and network infrastructure. Meta raised 2026 capex guidance to USD 125--145bn from USD 115--135bn, citing higher component pricing and additional data-center costs. It also cited >1GW of custom silicon with Broadcom, AMD chips, Nvidia systems, cloud deals, and USD 107bn increase in contractual commitments from cloud and infrastructure purchase agreements. | Strong official capex/component-cost evidence. Not supplier allocation. |
| Microsoft | `microsoft-fy2026-q3-press-release-webcast.html` | The archived Microsoft URL returned a thin/noindex shell and did not expose useful capex text in static HTML. | Archived as failed/thin primary-source route; not used for capex numbers. |

## Interpretation

- The source-backed demand side is strong: Alphabet, Amazon and Meta all disclose elevated AI infrastructure / data-center / server / accelerated-compute investment.
- This supports the report's view that AI infrastructure capex is a core demand driver for high-layer PCB, HDI, CCL and related equipment.
- These sources do **not** identify which PCB/CCL suppliers serve specific platforms, nor do they disclose supplier revenue, order value, ASP, shipments or margins.
- Therefore they improve the platform-demand bridge and risk triggers, but they do not close `named_platform_customer_revenue_split` or `bottom_up_customer_platform_eps_model`.
