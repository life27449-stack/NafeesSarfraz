import pandas as pd
from strategy import signal

def run(df, min_score=70):
    trades=[]
    for i in range(100, len(df)-1):
        s = signal(df.iloc[:i+1], min_score)
        if s["direction"] == "WAIT": continue
        entry = float(df.iloc[i]["close"])
        exitp = float(df.iloc[i+1]["close"])
        win = (exitp > entry) if s["direction"]=="UP" else (exitp < entry)
        trades.append({"time":df.iloc[i]["time"],"direction":s["direction"],
                       "score":s["score"],"entry":entry,"exit":exitp,"win":win})
    out=pd.DataFrame(trades)
    if out.empty: return out, {"trades":0,"win_rate":0}
    return out, {"trades":len(out),"win_rate":round(out.win.mean()*100,2)}
