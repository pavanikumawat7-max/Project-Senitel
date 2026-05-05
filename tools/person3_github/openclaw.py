def tool(fn):
    return fn

def request_approval(message: str):
    print(f"\n[APPROVAL REQUEST] {message}")
    ans = input("Type y to approve, n to deny: ").strip().lower()
    return ans
