import pandas as pd

books = pd.read_csv("data/books.csv")
book_tags = pd.read_csv("data/book_tags.csv")
tags = pd.read_csv("data/tags.csv")

#how many nulls are in each column
#print(books.isna().sum())

#image_url values are the generic “no photo” image instead of a real cover
#print(books["image_url"].str.contains("nophoto").sum())

#print(books[books["image_url"].str.contains("nophoto")].head())

#Which ID joins to the tags
''' 
"for col in ["id", "book_id", "best_book_id", "work_id"]:
    result = book_tags["goodreads_book_id"].isin(books[col]).all()
    print(col, result)'''
    

merged  = book_tags.merge(tags, on="tag_id")    
top_tags = (
    merged.groupby("tag_name")["count"]
    .sum()
    .sort_values(ascending=False)
    .head(150)
)
top_tags.to_csv("top_tags.csv", encoding="utf-8")
print("Top 30 tags:")
print(top_tags)
print("Total number of tags:", len(tags))

