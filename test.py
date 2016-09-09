# import re


# regex = r'(\-|\:|\!|\%|\*|\)|\(|\+|\-|\/|\$|\'|\"|\*|\[|\]|\{|\}|\#|\^|\,|\.)+'
# entity_regex = r'&\w+;'
# string = "@mlauer #journalism or #stateoftheunion #Election2016 #trump #realitytv #lightweight\u2026 https://t.co/KdPGds1Xmv"

# string = re.sub(r'[^\x00-\x7F]+','', string)
# print(string)

# # pattern = re.compile(entity_regex)
# # match = pattern.findall(string)

# # if match:
# # 	print(match)
# # else:
# # 	print("no match")

# # print("final: ", pattern.sub('',string))

_count = 0
def counter(count):
	count = 5

counter(_count)
print(_count)