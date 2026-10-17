import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
t = t.replace('<td bgcolor="#ffffff" style="background-color:#ffffff">&nbsp;</td>', "<td></td>")
t = re.sub(r'<td bgcolor="(#[0-9a-f]{6})" style="background-color:#[0-9a-f]{6}">&nbsp;</td>', r'<td style="background:\1">&nbsp;</td>', t)
t = re.sub(r'<td colspan="(\d+)" bgcolor="#1f4e79" style="background-color:#1f4e79;color:#fff">', r'<td colspan="\1" style="background:#1f4e79;color:#ffffff">', t)
open(sys.argv[2], "w", encoding="utf-8").write(t)
print(len(t))
