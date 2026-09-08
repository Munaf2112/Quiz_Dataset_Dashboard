import numpy as np
import pandas as pd
import html 
df=pd.read_csv("data/quiz_questions.csv")
print(df.columns)
print(df.describe())
df.rename(columns={'type':'Type','difficulty':'Level','category':'Category','question':'Question','correct_answer':'Answer'},inplace=True)
print(df.columns)
a=df['Level'].unique()
df['Level']=df['Level'].map({'easy':'Easy','medium':'Medium','hard':'Hard'})
a=df['Level'].unique()
b=df['Category'].unique()
print(b)
df['Category']=df['Category'].map({'General Knowledge':'GK','Entertainment: Books':'Books','Entertainment: Film':'Film','Entertainment: Music':'Music','Entertainment: Video Games':'Video_Games','Science &amp; Nature':'Nature','Science: Computers':'Computers','Geography':'Geography','History':'History'})
c=df['Category'].unique()
print(c)
d=df['Answer'].unique()
print(d)
print(df['Question'])
df['Question']=df['Question'].apply(html.unescape)
print(df['Question'])
df['Type']=df['Type'].map({'boolean':'Bool'})
print("-------------Dataset Contains---------------")
print(f"No of Questions  :{df['Type'].count()}")
print(f"No of Categories :{df['Category'].nunique()}")
print(f"No of Level      :{df['Level'].nunique()}")
print(f"No of Answer Type:{df['Answer'].nunique()}")
print()
print("------------Category Analysis---------")
df.groupby("Category")

Count_Category=[]
print("Count Based on Category")
for category in df['Category'].unique():
    Count=0
    for i in df['Category']:
        if i==category:
            Count+=1
    Count_Category.append((category,Count))
print("--------------------------------")
for Category,Count in Count_Category:
    print(f"|{Category} : {Count}|")
print("--------------------------------")
Category_Answer= []
print("Count of True False Based on Categories")
for category in df['Category'].unique():
    count_true = 0
    count_false = 0
    for i in df.index:
        if df['Category'][i] == category:
            if df['Answer'][i] == True:
                count_true += 1
            else:
                count_false += 1
    Category_Answer.append((category, count_true, count_false))

print("--------------------------------")
for category, count_true, count_false in Category_Answer:
    print(f"|{category} - True: {count_true}, False: {count_false}|")
print("------------------------------------------")
Category_Level_Counts = []
print("Count of levels Based On Categories")
for category in df['Category'].unique():
    count_easy = 0
    count_medium = 0
    count_hard = 0
    for i in df.index:
        if df['Category'][i] == category:
            if df['Level'][i] == 'Easy':
                count_easy += 1
            elif df['Level'][i] == 'Medium':
                count_medium += 1
            elif df['Level'][i] == 'Hard':
                count_hard += 1
    Category_Level_Counts.append((category, count_easy, count_medium, count_hard))

for category, easy, medium, hard in Category_Level_Counts:
    print(f"|{category} - Easy: {easy}, Medium: {medium}, Hard: {hard}|")
print("-------------------------------------------")
print("Percent Based On Categories")
Category_Percent=[]
for category in df['Category'].unique():
    Count=0
    for i in df['Category']:
        if i==category:
            Count+=1
    Category_Percent.append((category,round(Count/260*100,2)))
for Category,percent in Category_Percent:
    print(f"| {Category} - {percent}% |")
print("--------------------------------")








