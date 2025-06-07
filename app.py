import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 🔐 Přihlášení
def check_password():
    def password_entered():
        if st.session_state["password"] == "nemeckyeshop2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Zadejte heslo:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Zadejte heslo:", type="password", on_change=password_entered, key="password")
        st.error("❌ Nesprávné heslo")
        st.stop()

check_password()

# 📅 Základní nastavení
st.set_page_config(page_title="Rozdělení nákladů", layout="wide")
st.title("📊 Rozdělení nákladového rozpočtu podle ceny za kus")

# 📥 Upload CSV
uploaded_file = st.file_uploader("📄 Nahraj CSV soubor", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="cp1250", sep=";")
    df["turnover"] = df["turnover"].astype(str).str.replace(",", ".")
    df["turnover"] = pd.to_numeric(df["turnover"], errors="coerce")
    df["count"] = pd.to_numeric(df["count"], errors="coerce")
    df = df.dropna(subset=["turnover", "count"])
    df["cena_za_kus"] = df["turnover"] / df["count"]

    # 🧩 Cenová pásma (16 pásem)
    def assign_price_band(price):
        if price > 1000: return (16, "16. pásmo (1001–3500 Kč)")
        elif price > 400: return (15, "15. pásmo (401–1000 Kč)")
        elif price > 300: return (14, "14. pásmo (301–400 Kč)")
        elif price > 230: return (13, "13. pásmo (231–300 Kč)")
        elif price > 180: return (12, "12. pásmo (181–230 Kč)")
        elif price > 140: return (11, "11. pásmo (141–180 Kč)")
        elif price > 110: return (10, "10. pásmo (111–140 Kč)")
        elif price > 90: return (9, "9. pásmo (91–110 Kč)")
        elif price > 75: return (8, "8. pásmo (76–90 Kč)")
        elif price > 60: return (7, "7. pásmo (61–75 Kč)")
        elif price > 50: return (6, "6. pásmo (51–60 Kč)")
        elif price > 40: return (5, "5. pásmo (41–50 Kč)")
        elif price > 30: return (4, "4. pásmo (31–40 Kč)")
        elif price > 20: return (3, "3. pásmo (21–30 Kč)")
        elif price > 10: return (2, "2. pásmo (11–20 Kč)")
        else: return (1, "1. pásmo (0–10 Kč)")

    df[["pasmo_id", "cenove_pasmo"]] = df["cena_za_kus"].apply(assign_price_band).apply(pd.Series)

    # 📊 Výpočty
    obrat = df["turnover"].sum()
    pocet_ks = df["count"].sum()
    rozpocet = st.number_input("💰 Zadej rozpočet (Kč):", min_value=1_000_000, value=13_200_000, step=100_000)

    summary = df.groupby(["pasmo_id", "cenove_pasmo"]).agg(
        prodanych_kusu=("count", "sum"),
        cenove_rozpeti=("cena_za_kus", lambda x: f"{x.min():.2f} Kč – {x.max():.2f} Kč"),
        prumerna_cena=("cena_za_kus", "mean"),
        obrat=("turnover", "sum")
    ).reset_index()

    summary["naklad_celkem"] = summary["obrat"] / obrat * rozpocet
    summary["naklad_na_1_ks"] = summary["naklad_celkem"] / summary["prodanych_kusu"]
    summary = summary.sort_values("pasmo_id").round(2)

    # 📋 Tabulka
    st.subheader("📋 Výsledná tabulka")
    st.dataframe(summary[[
        "cenove_pasmo", "prodanych_kusu", "cenove_rozpeti",
        "prumerna_cena", "obrat", "naklad_na_1_ks", "naklad_celkem"
    ]], use_container_width=True)

    # 📦 Souhrn
    st.markdown("---")
    st.success(f"📦 Celkový počet prodaných kusů: {int(pocet_ks):,}")
    st.success(f"📈 Celkový obrat: {obrat:,.2f} Kč")
    st.success(f"✅ Kontrolní součet rozpočtu: {summary['naklad_celkem'].sum():,.2f} Kč")
    st.success(f"🧮 Průměrný náklad na 1 ks v hrubém: {obrat / pocet_ks:.2f} Kč")
    st.success("📅 Rok 2025")

    # 🏷️ Aktuální sklad
    if "stockAmount" in df.columns:
        df["stockAmount"] = pd.to_numeric(df["stockAmount"], errors="coerce")
        sklad = df[df["stockAmount"] > 0]["stockAmount"].sum()
        st.success(f"📦 Aktuálně skladem: {int(sklad):,} ks (bez záporných stavů)")

    # ℹ️ Metodika
    with st.expander("ℹ️ Jak se počítají náklady?"):
        st.markdown("""
        **Náklady celkem pro pásmo** = *(obrat pásma / celkový obrat) × rozpočet*  
        **Náklad na 1 ks** = *náklady celkem / počet kusů v pásmu*  
        """)

    # 📊 Graf 1 – Náklady celkem
    st.subheader("📊 Celkové náklady podle pásem")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(summary["cenove_pasmo"], summary["naklad_celkem"], color="lightcoral")
    ax1.set_ylabel("Náklady celkem (Kč)")
    ax1.set_xticklabels(summary["cenove_pasmo"], rotation=45, ha="right")
    ax1.set_title("Rozdělení nákladů podle cenových pásem")
    st.pyplot(fig1)

    # 📊 Graf 2 – Náklady na 1 ks
    st.subheader("📊 Náklad na 1 ks podle pásem")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.bar(summary["cenove_pasmo"], summary["naklad_na_1_ks"], color="skyblue")
    ax2.set_ylabel("Náklad na 1 ks (Kč)")
    ax2.set_xticklabels(summary["cenove_pasmo"], rotation=45, ha="right")
    ax2.set_title("Náklady na 1 ks v jednotlivých pásmech")
    for i, v in enumerate(summary["naklad_na_1_ks"]):
        ax2.text(i, v + 1, f"{v:.0f} Kč", ha='center', fontsize=8)
    st.pyplot(fig2)
