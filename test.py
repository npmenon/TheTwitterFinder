import re

string = 'DrSueDVM✞ 🙏🏼for 🇺🇸 ‏@DrSueDVM  3h3 hours ago
Praying that whoever replaces Obama can prevent economic collapse of America.'
# string = str(string.encode('unicode_escape'))
# print(string)
myre = re.compile(u'['
    u'\U0001F300-\U0001F64F'
    u'\U0001F680-\U0001F6FF'
    u'\u2600-\u26FF\u2700-\u27BF]+', 
    re.UNICODE)

m = myre.findall(string)
if m:
	print('match')
	print(m)
else:
	print('no match')