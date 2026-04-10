

import pandas as pd
import glob
import os

# ============================================================
# STEP 1: 读取所有 Sold CSV 文件
# ============================================================
sold_files = sorted(glob.glob('CRMLSSold*.csv'))

# 打印每个文件的 row count（append 前）
for f in sold_files:
    df_temp = pd.read_csv(f)
    print(f"{os.path.basename(f)}: {len(df_temp)} rows")

# Append 所有文件
df_sold = pd.concat([pd.read_csv(f) for f in sold_files], ignore_index=True)
print(f"\n✅ Row count after concatenation: {len(df_sold)}")

# ============================================================
# STEP 2: PropertyType 过滤
# ============================================================
print("\nPropertyType distribution BEFORE filter:")
print(df_sold['PropertyType'].value_counts())

df_sold = df_sold[df_sold['PropertyType'] == 'Residential']
print(f"\n✅ Row count after Residential filter: {len(df_sold)}")

print("\nPropertyType distribution AFTER filter:")
print(df_sold['PropertyType'].value_counts())

# ============================================================
# STEP 3: 输出最终 CSV
# ============================================================
df_sold.to_csv('sold_final.csv', index=False)
print(f"\n✅ sold_final.csv saved: {len(df_sold)} rows")


# ============================================================
# STEP 4: EDA
# ============================================================
print("\n===== BASIC INFO =====")
print(f"Shape: {df_sold.shape}")
print(f"Date range: {df_sold['CloseDate'].min()} to {df_sold['CloseDate'].max()}")

print("\n===== CLOSE PRICE =====")
print(df_sold['ClosePrice'].describe())

print("\n===== TOP 10 CITIES BY VOLUME =====")
print(df_sold['City'].value_counts().head(10))

print("\n===== AVG CLOSE PRICE BY CITY (Top 10) =====")
print(df_sold.groupby('City')['ClosePrice'].mean().sort_values(ascending=False).head(10))

print("\n===== AVG DAYS ON MARKET =====")
print(f"Mean DOM: {df_sold['DaysOnMarket'].mean():.1f} days")
print(f"Median DOM: {df_sold['DaysOnMarket'].median():.1f} days")

print("\n===== AVG LIST PRICE VS CLOSE PRICE =====")
print(f"Avg List Price: ${df_sold['ListPrice'].mean():,.0f}")
print(f"Avg Close Price: ${df_sold['ClosePrice'].mean():,.0f}")