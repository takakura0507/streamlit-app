import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def load_csv(path: str):
    return pd.read_csv(path, encoding="utf-8-sig")

st.title("2023年度 懲戒処分の状況")

st.sidebar.header("表示設定")

datasets = {
    "官職、処分内容、人数": "data1_utf8.csv",
    "処分事由,処分理由,処分内容,人数": "data2_utf8.csv",
    "処分事由,処分理由,官職等,人数": "data3_utf8.csv",
}

selected_label = st.sidebar.selectbox("データセットを選択", list(datasets.keys()))

sort_order = st.sidebar.radio("並び順を選択", ("人数の多い順", "人数の少ない順"))

view_mode = st.sidebar.radio("表示形式", ["表で表示", "グラフで表示"])

df = load_csv(datasets[selected_label])  # ← UTF-8 に変換したCSVを指定

st.sidebar.subheader("絞り込み設定")

filtered_df = df.copy()
for col in df.columns:
    if col == "人数":
        continue

    unique_vals = df[col].dropna().unique()

    if len(unique_vals) <= 20:
        selected_vals = st.sidebar.multiselect(f"{col}で絞り込み", unique_vals)
        if selected_vals:
            filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]
    else:
        keyword = st.sidebar.text_input(f"{col}を含むキーワード")
        if keyword:
            filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(keyword)]

if sort_order == "人数の多い順":
    df = df.sort_values(by="人数", ascending=False)
else:
    df = df.sort_values(by="人数", ascending=True)

main_col = filtered_df.columns[0]

st.subheader(f"{selected_label} の懲戒処分データ")

if view_mode == "表で表示":
    st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True)

else:
    chart = (
        alt.Chart(filtered_df)
        .mark_bar()
        .encode(
            x=alt.X("人数:Q", title="人数"),
            y=alt.Y(df.columns[0] + ":N", sort='-x', title=df.columns[0]),
            axis=alt.Axis(labelLimit=300),
            color=alt.Color(df.columns[0] + ":N", legend=None)
        )
        .properties(width=800, height=500)
    )
    st.altair_chart(chart, use_container_width=True)