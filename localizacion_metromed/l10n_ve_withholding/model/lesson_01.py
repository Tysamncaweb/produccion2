"""AND
X   Y   RES
0   0   0
0   1   0
1   0   0
1   1   1

OR
X   Y   RES
0   0   0
0   1   1
1   0   1
1   1   1

lista[n] == lista[len(lista)-n]"""

self.search(['|','&',('is_company', '=', True), ('customer', '=', True), ('is_company', '=', True)])


a or (b and c)
a or (b and or (c and d))

a and b and (c or d)

self.write({key:value})
obj.write({key:value})
self.env['model_name'].write([id],{key:value})
obj.search(domain).write({key:value})