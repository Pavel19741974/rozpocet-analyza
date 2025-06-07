import pandas as pd
import tkinter as tk
from tkinter import filedialog
import getpass

# 🔐 Přihlášení heslem
spravne_heslo = "nemeckyeshop2025"
zadane_heslo = getpass.getpass("🔐 Zadej heslo pro spuštění aplikace: ")

if zadane_heslo != spravne_heslo:
    print("❌ Nesprávné heslo. Přístup odepřen.")
    exit()
else:
    print("✅ Heslo správné. Pokračuji...\n")

# 📂 Výběr CSV souboru ručně
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Vyber CSV soubor", filetypes=[("CSV files", "*.csv")])

if not file_path:
    print("❌ Soubor nebyl vybrán.")
    exit()

# 1. Načtení dat
produkt_list = pd.read_csv(file_path, encoding="cp1250", sep=";")

# 2. Převod sloupců
produkt_list["turnover"] = produkt_list["turnover"].astype(str).str.replace(",", ".")
produkt_list["turnover"] = pd.to_numeric(produkt_list["turnover"], errors="coerce")
produkt_list["count"] = pd.to_numeric(produkt_list["count"], errors="coerce")

# 3. Odstranění neplatných řádků
produkt_list = produkt_list.dropna(subset=["turnover", "count"])
produkt_list["cena_za_kus"] = produkt_list["turnover"] / produkt_list["count"]

# 4. Cenová pásma (16)
def assign_custom_price_band(price):
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

produkt_list[["pasmo_id", "cenove_pasmo"]] = produkt_list["cena_za_kus"].apply(assign_custom_price_band).apply(pd.Series)

# 5. Výpočty
celkovy_obrat_realita = produkt_list["turnover"].sum().round(2)
celkovy_pocet_ks = produkt_list["count"].sum()
total_budget = 13_200_000

summary = produkt_list.groupby(["pasmo_id", "cenove_pasmo"]).agg(
    prodanych_kusu=("count", "sum"),
    cenove_rozpeti=("cena_za_kus", lambda x: f"{x.min():.2f} Kč – {x.max():.2f} Kč"),
    prumerna_cena=("cena_za_kus", "mean"),
    obrat=("turnover", "sum")
).reset_index()

summary["naklad_celkem"] = summary["obrat"] / celkovy_obrat_realita * total_budget
summary["naklad_na_1_ks"] = summary["naklad_celkem"] / summary["prodanych_kusu"]

# 6. Zaokrouhlení
summary = summary.sort_values("pasmo_id").round(2)

# 7. Výstupní tabulka
summary_final = summary[[
    "cenove_pasmo",
    "prodanych_kusu",
    "cenove_rozpeti",
    "prumerna_cena",
    "obrat",
    "naklad_na_1_ks",
    "naklad_celkem"
]]

# 8. Výpis tabulky
print("\n📋 Výsledná tabulka podle cenových pásem:\n")
print(summary_final.to_string(index=False))

# 9. Dodatečné výpočty
prumerny_naklad_hruby = celkovy_obrat_realita / celkovy_pocet_ks
print(f"\n📎 Průměrný náklad na 1 ks v hrubém: {prumerny_naklad_hruby:.2f} Kč")

# 10. Skladové zásoby (ignorovat záporné hodnoty)
if "stockAmount" in produkt_list.columns:
    produkt_list["stockAmount"] = pd.to_numeric(produkt_list["stockAmount"], errors="coerce")
    sklad_kusu = produkt_list.loc[produkt_list["stockAmount"] > 0, "stockAmount"].sum()
    print(f"📦 Aktuální počet kusů skladem: {int(sklad_kusu):,}")
else:
    print("⚠️ Sloupec 'stockAmount' nebyl nalezen v CSV souboru.")

# 11. Shrnutí
print(f"\n📊 Celkový počet prodaných kusů: {int(celkovy_pocet_ks):,}")
print(f"💰 Celkový obrat (ze sloupce 'turnover'): {celkovy_obrat_realita:,.2f} Kč")
print(f"✅ Kontrolní součet rozpočtu: {summary['naklad_celkem'].sum():,.2f} Kč")
print("📅 Rok: 2025")
