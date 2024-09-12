d = {"0 1111 0100 0001 0001 0011": 1024}

res = next(iter(d))
res = res.replace(" ", "")

res_t = int(res[0], 2)
res_n = int(res[1:5], 2)
res_b = int(res[5:9], 2)
res_a = int(res[9:13], 2)
res_x_mult = int(res[13:17], 2)
res_x = int(res[17:], 2)

print(f"res_t = {res_t} ({res[0]})")
print(f"res_n = {res_n} ({res[1:5]})")
print(f"res_b = {res_b} ({res[5:9]})")
print(f"res_a = {res_a} ({res[9:13]})")
print(f"res_x_mult = {res_x_mult} ({res[13:17]})")
print(f"res_x = {res_x} ({res[17:]})")
