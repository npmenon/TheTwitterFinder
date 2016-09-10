import re


kaomojis_regex1 = u'(?<=^|\s)[\:\;8\<\|]-*\S(?=\s|$)'
kaomojis_regex12 = u'(\\o\/|D:|c:|=D|=3|B\)|\(8|8\)|\(8\))'

string = "This is a string that has (-‿‿-) kaomoji"

match = re.search(kaomojis_regex1,string)
if match: print(match.group(0))
else: print('no match')

# pattern = re.compile(entity_regex)
# match = pattern.findall(string)

# if match:
# 	print(match)
# else:
# 	print("no match")

# print("final: ", pattern.sub('',string))