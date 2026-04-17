# 每次在terminal跑之前，输入cd ~/Desktop/IDX\ Exchange

import pandas as pd
import glob
import os


# STEP 1: 读取所有 Sold CSV 文件
sold_files = sorted(glob.glob('CRMLSSold*.csv'))

# 打印每个文件的 row count（append 前）
for f in sold_files:
    df_temp = pd.read_csv(f)
    print(f"{os.path.basename(f)}: {len(df_temp)} rows")

# Append 所有文件
df_sold = pd.concat([pd.read_csv(f) for f in sold_files], ignore_index=True)
print(f"\n✅ Row count after concatenation: {len(df_sold)}")


# STEP 2: PropertyType 过滤
print("\nPropertyType distribution BEFORE filter:")
print(df_sold['PropertyType'].value_counts())

df_sold = df_sold[df_sold['PropertyType'] == 'Residential']
print(f"\n✅ Row count after Residential filter: {len(df_sold)}")

print("\nPropertyType distribution AFTER filter:")
print(df_sold['PropertyType'].value_counts())


# STEP 3: 输出最终 CSV
df_sold.to_csv('sold_final.csv', index=False)
print(f"\n✅ sold_final.csv saved: {len(df_sold)} rows")



# STEP 4: EDA
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

# --------------------------------------------------------------------------------------

# STEP 5: 数据集基本检查

print("\n===== SHAPE =====")
print(df_sold.shape)

print("\n===== DATA TYPES =====")
print(df_sold.dtypes)

print("\n===== MISSING VALUES =====")
missing = df_sold.isnull().sum()
missing_pct = (missing / len(df_sold) * 100).round(2)
missing_report = pd.DataFrame({
    'missing_count': missing,
    'missing_pct': missing_pct
}).sort_values('missing_pct', ascending=False)
print(missing_report)

print("\n===== COLUMNS WITH >90% MISSING =====")
print(missing_report[missing_report['missing_pct'] > 90])


# STEP 6: 数值分布分析
numeric_fields = ['ClosePrice', 'ListPrice', 'OriginalListPrice',
                  'LivingArea', 'LotSizeAcres', 'BedroomsTotal',
                  'BathroomsTotalInteger', 'DaysOnMarket', 'YearBuilt']

for field in numeric_fields:
    if field in df_sold.columns:
        print(f"\n===== {field} =====")
        print(df_sold[field].describe(percentiles=[.1,.25,.5,.75,.9]))


# STEP 7: 回答关键问题
print("\n===== 高于挂牌价成交的比例 =====")
above_list = (df_sold['ClosePrice'] > df_sold['ListPrice']).sum()
pct = above_list / len(df_sold) * 100
print(f"{above_list:,} 套 ({pct:.1f}%) 高于挂牌价成交")

print("\n===== 各County中位成交价 Top 10 =====")
print(df_sold.groupby('CountyOrParish')['ClosePrice']
      .median().sort_values(ascending=False).head(10))

print("\n===== 日期异常检查 =====")
df_sold['CloseDate'] = pd.to_datetime(df_sold['CloseDate'])
df_sold['ListingContractDate'] = pd.to_datetime(df_sold['ListingContractDate'])
anomaly = (df_sold['CloseDate'] < df_sold['ListingContractDate']).sum()
print(f"成交日期早于挂牌日期的异常记录: {anomaly}")



# STEP 8: Mortgage Rate 合并 (FRED)
print("\n===== 获取 Mortgage Rate 数据 =====")
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

# changed column name to force it run
mortgage = pd.read_csv(url)
mortgage.columns = ['date', 'rate_30yr_fixed']
mortgage['date'] = pd.to_datetime(mortgage['date'])


mortgage.columns = ['date', 'rate_30yr_fixed']

# 重采样：weekly → monthly 平均
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean().reset_index()
)
print(mortgage_monthly.tail())

# 创建 year_month key
df_sold['year_month'] = pd.to_datetime(df_sold['CloseDate']).dt.to_period('M')

# 合并
df_sold = df_sold.merge(mortgage_monthly, on='year_month', how='left')

# 验证
nulls = df_sold['rate_30yr_fixed'].isnull().sum()
print(f"\n合并后 rate_30yr_fixed 空值数量: {nulls}")
print(df_sold[['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']].head())

# 保存最终 CSV
df_sold.to_csv('sold_final.csv', index=False)
print(f"\n✅ sold_final.csv 已更新，共 {len(df_sold)} 行")