import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]

SKILL_MIRRORS = (
    (
        ".agents/skills/equity-research/SKILL.md",
        ".codex/skills/equity-research/SKILL.md",
    ),
    (
        ".agents/skills/research-prose-polish/SKILL.md",
        ".codex/skills/research-prose-polish/SKILL.md",
    ),
    (
        ".agents/skills/research-report-review/SKILL.md",
        ".codex/skills/research-report-review/SKILL.md",
    ),
    (
        ".agents/skills/evolve/anti-patterns.md",
        ".codex/skills/evolve/anti-patterns.md",
    ),
)

BANNED_CHINESE_RHETORIC = re.compile(
    r"不是|没有|最难|而非|(?:并非|绝非)[^。！？；\n]{0,96}(?:而是|也(?:不是|非|不))|既非[^。！？；\n]{0,96}也非|(?:既)?不[^。！？；\n]{0,96}也不|(?:无|未)[^。！？；\n]{0,96}也(?:无|未)"
)


def test_chinese_rhetorical_template_prohibition_is_mirrored_and_explicit() -> None:
    for left_relative, right_relative in SKILL_MIRRORS:
        left = REPO_ROOT / left_relative
        right = REPO_ROOT / right_relative
        assert left.read_text(encoding="utf-8") == right.read_text(encoding="utf-8")

    prose_rules = (REPO_ROOT / SKILL_MIRRORS[1][0]).read_text(encoding="utf-8")
    review_rules = (REPO_ROOT / SKILL_MIRRORS[2][0]).read_text(encoding="utf-8")
    equity_rules = (REPO_ROOT / SKILL_MIRRORS[0][0]).read_text(encoding="utf-8")

    for token in (
        "Chinese Rhetorical-Template Prohibition",
        "every authored `不是` occurrence",
        "every authored `没有` occurrence",
        "`不是……而是……`",
        "`最难……`",
        "`最重要……不是……`",
        "`而非`",
        "`而不是`",
        "`绝非……而是……`",
        "`真正/关键……不是……`",
        "`不是……也不是……`",
        "`既不是……也不是……`",
        "reader_prose_template_ban",
    ):
        assert token in prose_rules
    assert "reader_prose_template_ban" in review_rules
    assert "R2 cannot PASS" in equity_rules


def test_chinese_rhetorical_template_regression_samples() -> None:
    prohibited = (
        "这不是 X，而是 Y。",
        "最难的是把制度翻译成交易规则。",
        "最重要的不是预测，而是控制损失。",
        "研究覆盖治理与执行能力，而非品牌。",
        "研究先验证实际合约，而不是使用连续主力图。",
        "这并非惯性延续，而是一次制度变化。",
        "关键不是形式完整，而是证据可核验。",
        "q=0 不是方向判断，也不是延后交易的表达。",
        "这既不是方向判断，也不是交易授权。",
        "本报告没有收集这些信息，也没有替代专业意见。",
        "该结论既不覆盖账户，也不覆盖税务。",
    )
    permitted = (
        "证据不足时，研究暂停。",
        "治理和执行能力决定个人复制的边界。",
    )

    assert all(BANNED_CHINESE_RHETORIC.search(text) for text in prohibited)
    assert all(not BANNED_CHINESE_RHETORIC.search(text) for text in permitted)
