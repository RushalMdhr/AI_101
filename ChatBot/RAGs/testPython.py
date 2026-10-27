# msg = [{"system" : "hello"}]

# print(msg)

# msg.append({"role": "user", "content": "hi"})

# print(msg)

msg = [1,2,3]
msg2=[4,5,6]
msg = tuple(msg)
msg2 = tuple(msg2)
print(msg)
# for x in msg2:
#     msg.append(x)
# print(msg)
msg=msg2 + msg
print(msg)