import pandas as pd
import glob
import os

# ============================================================
# STEP 1: 读取所有 Listed CSV 文件
# ============================================================
listed_files = sorted(glob.glob('CRMLSListing*.csv'))

# 打印每个文件的 row count（append 前）
for f in listed_files:
    df_temp = pd.read_csv(f)
    print(f"{os.path.basename(f)}: {len(df_temp)} rows")

# Append 所有文件
df_listed = pd.concat([pd.read_csv(f) for f in listed_files], ignore_index=True)
print(f"\n✅ Row count after concatenation: {len(df_listed)}")

# ============================================================
# STEP 2: PropertyType 过滤
# ============================================================
print("\nPropertyType distribution BEFORE filter:")
print(df_listed['PropertyType'].value_counts())

df_listed = df_listed[df_listed['PropertyType'] == 'Residential']
print(f"\n✅ Row count after Residential filter: {len(df_listed)}")

print("\nPropertyType distribution AFTER filter:")
print(df_listed['PropertyType'].value_counts())

# ============================================================
# STEP 3: 输出最终 CSV
# ============================================================
df_listed.to_csv('listed_final.csv', index=False)
print(f"\n✅ listed_final.csv saved: {len(df_listed)} rows")
