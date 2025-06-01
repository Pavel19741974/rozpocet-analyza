import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 🔒 Přihlašovací ochrana
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

# 🧾 Titulek aplikace
st.title("📊 Rozdělení marketingového rozpočtu podle obratu")

# 📤 Nahrání CSV
uploaded_file = st.file_uploader("📄 Nahraj CSV soubor", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="cp1250", sep=";")
    df["turnover"] = df["turnover"].astype(str).str.replace(",", ".")
    df["turnover"] = pd.to_numeric(df["turnover"], errors="coerce")
    df["count"] = pd.to_numeric(df["count"], errors="coerce")
    df = df.dropna(subset=["turnover", "count"])
    df["cena_za_kus"] = df["turnover"] / df["count"]

    # 🎯 Fixních 15 pásem + nové 16. pásmo
    def assign_price_band(price):
        if price > 1000:
            return (16, "16. pásmo (1001–3500 Kč)")
        elif price > 400:
            return (15, "15. pásmo (401–1000 Kč)")
        elif price > 300:
            return (14, "14. pásmo (301–400 Kč)")
        elif price > 230:
            return (13, "13. pásmo (231–300 Kč)")
        elif price > 180:
            return (12, "12. pásmo (181–230 Kč)")
        elif price > 140:
            return (11, "11. pásmo (141–180 Kč)")
        elif price > 110:
            return (10, "10. pásmo (111–140 Kč)")
        elif price > 90:
            return (9, "9. pásmo (91–110 Kč)")
        elif price > 75:
            return (8, "8. pásmo (76–90 Kč)")
        elif price > 60:
            return (7, "7. pásmo (61–75 Kč)")
        elif price > 50:
            return (6, "6. pásmo (51–60 Kč)")
        elif price > 40:
            return (5, "5. pásmo (41–50 Kč)")
        elif price > 30:
            return (4, "4. pásmo (31–40 Kč)")
        elif price > 20:
            return (3, "3. pásmo (21–30 Kč)")
        elif price > 10:
            return (2, "2. pásmo (11–20 Kč)")
        else:
            return (1, "1. pásmo (0–10 Kč)")

    df[["pasmo_id", "cenove_pasmo"]] = df["cena_za_kus"].apply(assign_price_band).apply(pd.Series)

    # 💰 Rozpočet
    rozpocet = st.number_input("💰 Zadej rozpočet (Kč)", min_value=0, value=13_200_000)

    # 📊 Výpočty
    obrat = df["turnover"].sum()
    pocet_ks = df["count"].sum()

    summary = df.groupby(["pasmo_id", "cenove_pasmo"]).agg(
        prodanych_kusu=("count", "sum"),
        cenove_rozpeti=("cena_za_kus", lambda x: f"{x.min():.2f} Kč – {x.max():.2f} Kč"),
        prumerna_cena=("cena_za_kus", "mean"),
        obrat=("turnover", "sum")
    ).reset_index()

    summary["naklad_celkem"] = summary["obrat"] / obrat * rozpocet
    summary["naklad_na_1_ks"] = summary["naklad_celkem"] / summary["prodanych_kusu"]

    summary = summary.sort_values("pasmo_id").round(2)

    # 📋 Zobrazení tabulky
    st.dataframe(summary[[
        "cenove_pasmo",
        "prodanych_kusu",
        "cenove_rozpeti",
        "prumerna_cena",
        "obrat",
        "naklad_na_1_ks",
        "naklad_celkem"
    ]], use_container_width=True)

    # 📦 Přehled
    st.success(f"📦 Celkem ks: {int(pocet_ks):,}")
    st.success(f"📈 Celkový obrat: {obrat:,.2f} Kč")
    st.success(f"✅ Rozpočet: {summary['naklad_celkem'].sum():,.2f} Kč")

    # 📘 Vysvětlivka výpočtu
    with st.expander("📘 Jak se počítají náklady na 1 ks"):
        st.markdown("""
        **Náklady na 1 ks** = `Náklad celé skupiny / počet prodaných kusů`
        
        **Náklad celé skupiny** = `(obrat pásma / obrat celkem) × rozpočet`
        
        Pásma jsou pevně daná (0–10 Kč, 11–20 Kč, ..., 1001–3500 Kč).
        """)

    # 📊 Graf rozdělení nákladů
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(summary["cenove_pasmo"], summary["naklad_celkem"])
    ax.set_ylabel("Náklady celkem (Kč)")
    ax.set_xlabel("Cenové pásmo")
    ax.set_title("📊 Rozdělení rozpočtu podle pásma")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)
