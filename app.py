import math
from collections import Counter

import streamlit as st

st.set_page_config(page_title="敘述性統計計算器", page_icon="📊", layout="wide")


def parse_numbers(raw_text: str) -> list[float]:
    tokens = [token.strip() for token in __import__("re").split(r"[\s,、，;；]+", raw_text) if token.strip()]
    if not tokens:
        raise ValueError("請先輸入至少一個數字。")

    numbers: list[float] = []
    for idx, token in enumerate(tokens, start=1):
        try:
            numbers.append(float(token))
        except ValueError as exc:
            raise ValueError(f"第 {idx} 個值（{token}）不是有效數字。") from exc
    return numbers


def quantile(sorted_data: list[float], q: float) -> float:
    pos = (len(sorted_data) - 1) * q
    base = int(math.floor(pos))
    rest = pos - base
    if base + 1 < len(sorted_data):
        return sorted_data[base] + rest * (sorted_data[base + 1] - sorted_data[base])
    return sorted_data[base]


def describe_data(numbers: list[float], use_sample_std: bool) -> dict[str, float | int | None | str]:
    sorted_data = sorted(numbers)
    n = len(numbers)

    total = sum(numbers)
    mean = total / n
    median = quantile(sorted_data, 0.5)
    q1 = quantile(sorted_data, 0.25)
    q3 = quantile(sorted_data, 0.75)

    minimum = sorted_data[0]
    maximum = sorted_data[-1]
    data_range = maximum - minimum
    iqr = q3 - q1

    divisor = n - 1 if use_sample_std else n
    if divisor <= 0:
        raise ValueError("樣本標準差需要至少兩筆資料。")

    variance = sum((x - mean) ** 2 for x in numbers) / divisor
    std = math.sqrt(variance)
    cv = None if mean == 0 else std / abs(mean) * 100

    counts = Counter(numbers)
    max_count = max(counts.values())
    modes = [k for k, v in counts.items() if v == max_count and max_count > 1]
    mode_text = "、".join(f"{m:g}" for m in sorted(modes)) if modes else "無眾數"

    return {
        "樣本數": n,
        "總和": total,
        "平均數": mean,
        "中位數": median,
        "最小值": minimum,
        "最大值": maximum,
        "全距": data_range,
        "第一四分位數 (Q1)": q1,
        "第三四分位數 (Q3)": q3,
        "四分位距 (IQR)": iqr,
        "變異數": variance,
        "標準差": std,
        "變異係數 CV(%)": cv,
        "眾數": mode_text,
    }


def fmt(value: float | int | None | str) -> str:
    if value is None:
        return "無法計算（平均數為 0）"
    if isinstance(value, str):
        return value
    return f"{value:,.6f}".rstrip("0").rstrip(".")


st.title("📊 網頁版敘述性統計計算器")
st.caption("輸入數字後可快速計算平均數、標準差、變異數、四分位數等資料。")

col1, col2 = st.columns([3, 2])

with col1:
    raw_input = st.text_area(
        "請輸入數字（可用逗號、空白、換行分隔）",
        value="12, 15, 18, 20, 22, 22, 25, 30",
        height=180,
    )

with col2:
    std_type = st.radio(
        "標準差類型",
        options=["母體標準差（除以 n）", "樣本標準差（除以 n-1）"],
        index=0,
    )
    st.info("樣本標準差建議用在從母體抽樣的資料。")

if st.button("開始計算", type="primary"):
    try:
        numbers = parse_numbers(raw_input)
        use_sample_std = "n-1" in std_type
        results = describe_data(numbers, use_sample_std)

        st.subheader("計算結果")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("樣本數", fmt(results["樣本數"]))
        m2.metric("平均數", fmt(results["平均數"]))
        m3.metric("中位數", fmt(results["中位數"]))
        m4.metric("標準差", fmt(results["標準差"]))

        ordered_keys = [
            "總和",
            "最小值",
            "最大值",
            "全距",
            "第一四分位數 (Q1)",
            "第三四分位數 (Q3)",
            "四分位距 (IQR)",
            "變異數",
            "變異係數 CV(%)",
            "眾數",
        ]
        st.table({"統計項目": ordered_keys, "數值": [fmt(results[k]) for k in ordered_keys]})

        st.success(
            f"此資料共 {results['樣本數']} 筆，平均數 {fmt(results['平均數'])}，"
            f"中位數 {fmt(results['中位數'])}，標準差 {fmt(results['標準差'])}。"
        )
    except ValueError as err:
        st.error(str(err))

st.markdown("---")
st.markdown("💡 小提醒：若資料有極端值，建議同時參考中位數與四分位距。")
