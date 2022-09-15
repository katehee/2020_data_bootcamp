from original_code.instagram_crawler import instagram as insta
from original_code.instagram_crawler import preprocessing as pp

keyword = input("Input Keyword: ")

# login
link_list = insta.crawl_insta_link(keyword, "tempcrawlingbot2", "asdfqwer!@#$")

# crawl link
insta.save_links_to_txt("insta_link", link_list)

# collect data
data_list = insta.crawl_instagram_data("insta_link.txt")

# save data
insta.save_to_csv("instagram_data", data_list)

# pre-processing
file = "instagram_data.csv"
data = pp.pd.read_csv(file)
df = pp.pd.DataFrame(data)

# remove korean
pp_text_col = list(map(pp.only_eng_num, df['text']))
df['pp_text'] = pp_text_col

# extract tag
tag_col = df['text']
tag_col = list(map(pp.extract_tag, tag_col))
df['tag'] = tag_col

# extract like
like_col = df['like']
like_col = list(map(pp.extract_like, like_col))
df['like_point'] = like_col
df = df.dropna(subset=["pp_text"])

# save data frame
df.to_csv(file + '_pp.csv', header=True, index=False, encoding='utf-8-sig')
