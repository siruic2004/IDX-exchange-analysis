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


# ============================================================
# STEP 4: 数据集基本检查
# ============================================================
print("\n===== SHAPE =====")
print(df_listed.shape)

print("\n===== MISSING VALUES =====")
missing = df_listed.isnull().sum()
missing_pct = (missing / len(df_listed) * 100).round(2)
missing_report = pd.DataFrame({
    'missing_count': missing,
    'missing_pct': missing_pct
}).sort_values('missing_pct', ascending=False)
print(missing_report)

print("\n===== COLUMNS WITH >90% MISSING =====")
print(missing_report[missing_report['missing_pct'] > 90])

# ============================================================
# STEP 5: 数值分布
# ============================================================
numeric_fields = ['ListPrice', 'OriginalListPrice', 'LivingArea',
                  'BedroomsTotal', 'BathroomsTotalInteger', 'DaysOnMarket']

for field in numeric_fields:
    if field in df_listed.columns:
        print(f"\n===== {field} =====")
        print(df_listed[field].describe(percentiles=[.1,.25,.5,.75,.9]))

# ============================================================
# STEP 6: Mortgage Rate 合并
# ============================================================
print("\n===== 获取 Mortgage Rate 数据 =====")
import pandas as pd
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url)
mortgage.columns = ['date', 'rate_30yr_fixed']
mortgage['date'] = pd.to_datetime(mortgage['date'])
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean().reset_index()
)

df_listed['year_month'] = pd.to_datetime(df_listed['ListingContractDate']).dt.to_period('M')
df_listed = df_listed.merge(mortgage_monthly, on='year_month', how='left')

nulls = df_listed['rate_30yr_fixed'].isnull().sum()
print(f"合并后 rate_30yr_fixed 空值数量: {nulls}")
print(df_listed[['ListingContractDate', 'year_month', 'ListPrice', 'rate_30yr_fixed']].head())

df_listed.to_csv('listed_final.csv', index=False)
print(f"\n✅ listed_final.csv 已更新，共 {len(df_listed)} 行")

