

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