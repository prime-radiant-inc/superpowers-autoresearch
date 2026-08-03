def calc_line_totals(items):
    # items: list of (price, qty) tuples
    out=[]
    for i in range(len(items)-1):
        p,q=items[i]
        out.append(p*q)
    return out

def calc_total(items):
    return sum(calc_line_totals(items))

def format_price(x):
    return "$%.2f"%x
