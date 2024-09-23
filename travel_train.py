import numpy as np
import pandas as pd

# aihub : https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=data&dataSetSn=71780
# 데이터셋 로드
df_place = pd.read_csv('./tn_visit_area_info_방문지정보_D.csv', encoding='utf-8')
df_place.head()
df_travel = pd.read_csv('./tn_travel_여행_D.csv')
df_travel.head()
df_traveler = pd.read_csv('./tn_traveller_master_여행객 Master_D.csv')
df_traveler.head()

# 데이터 병합
df = pd.merge(df_place, df_travel, on='TRAVEL_ID', how='left')
df = pd.merge(df, df_traveler, on='TRAVELER_ID', how='left')
#df.head()

#df[df['TRAVEL_ID'] == 'd_d006731']

# 전처리 1
df_fil = df[~df['TRAVEL_MISSION_CHECK'].isnull()].copy()
df_fil.loc[:, 'TRAVEL_MISSION_INT'] = df_fil['TRAVEL_MISSION_CHECK'].str.split(';').str[0].astype(int)
#df_fil

# 전처리 2
df_fil = df_fil[[
    'GENDER', 'AGE_GRP',
    'TRAVEL_STYL_1', 'TRAVEL_STYL_2', 'TRAVEL_STYL_3', 'TRAVEL_STYL_4', 'TRAVEL_STYL_5', 'TRAVEL_STYL_6', 'TRAVEL_STYL_7', 'TRAVEL_STYL_8',
    'TRAVEL_MOTIVE_1',
    'TRAVEL_COMPANIONS_NUM',
    'TRAVEL_MISSION_INT',
    'VISIT_AREA_NM',
    'DGSTFN',
]]

df_fil = df_fil.dropna()
#df_fil

# 전처리 3
cat_features_names = [
    'GENDER',
    #'AGE_GRP',
    'TRAVEL_STYL_1', 'TRAVEL_STYL_2', 'TRAVEL_STYL_3', 'TRAVEL_STYL_4', 'TRAVEL_STYL_5', 'TRAVEL_STYL_6', 'TRAVEL_STYL_7', 'TRAVEL_STYL_8',
    'TRAVEL_MOTIVE_1',
    #'TRAVEL_COMPANIONS_NUM',
    'TRAVEL_MISSION_INT',
    'VISIT_AREA_NM',
    #'DGSTFN',
]
df_fil[cat_features_names[1:-1]] = df_fil[cat_features_names[1:-1]].astype(int)
#df_fil

# 데이터셋 분류
from sklearn.model_selection import train_test_split
train_data, test_data = train_test_split(df_fil, test_size = 0.2, random_state=2023)
print(train_data.shape)
print(test_data.shape)

# Catboost
from catboost import CatBoostRegressor, Pool
train_pool = Pool(train_data.drop(['DGSTFN'], axis=1),# 열방향
                  label = train_data['DGSTFN'],
                  cat_features = cat_features_names)

test_pool = Pool(test_data.drop(['DGSTFN'], axis=1),# 열방향
                 label = test_data['DGSTFN'],
                 cat_features = cat_features_names)

# 모델 생성
model = CatBoostRegressor(
    loss_function = 'RMSE', # 평균제곱근오차
    eval_metric='MAE', # 평균오차
    task_type='CPU',
    depth=6,
    learning_rate=0.01,
    n_estimators=2000)

model.fit(
    train_pool,
    eval_set = test_pool,
    verbose=500,
    plot=True )

# Save the model
model.save_model('catboost_model.cbm')

#test_data.iloc[2]

# 모델 테스트
model.predict(test_data.iloc[2].drop(['DGSTFN']))

# 테스트데이터 갯수 확인(1~5점)
test_data[test_data['DGSTFN'] == 6].index

# 길이 출력해보기 만족도 점수별로 for 문으로
for i in range(1, 6):
  dgs_len = [index for index in test_data.index if test_data.loc[index, 'DGSTFN'] == i]
  print(f'만족도 {i}의 개수 :', len(dgs_len))

  model.get_feature_importance(prettified=True)

area_names = df_fil[['VISIT_AREA_NM']].drop_duplicates()
area_names

# 여행자를 샘플로
traveler = {
    'GENDER':'남',
    'AGE_GRP' : 30.0,
    'TRAVEL_STYL_1' : 1,
    'TRAVEL_STYL_2' : 1,
    'TRAVEL_STYL_3' : 1,
    'TRAVEL_STYL_4' : 4,
    'TRAVEL_STYL_5' : 1,
    'TRAVEL_STYL_6' : 4,
    'TRAVEL_STYL_7' : 2,
    'TRAVEL_STYL_8' : 6,
    'TRAVEL_MOTIVE_1' : 3,
    'TRAVEL_COMPANIONS_NUM' : 4.0,
    'TRAVEL_MISSION_INT' : 5 }
results = pd.DataFrame([], columns=['AREA', 'SCORE'])
for area in area_names['VISIT_AREA_NM']:
  input = list(traveler.values())
  input.append(area)
  score = model.predict(input)
  results = pd.concat([results, pd.DataFrame([[area,score]], columns=['AREA','SCORE'])])
print(results.sort_values('SCORE', ascending=False)[:10])

# 하위 score 구간 오름 차순 정렬
#results.sort_values('SCORE', ascending=True)[:10]
