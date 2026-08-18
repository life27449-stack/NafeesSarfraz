def daily_loss_allowed(start_balance, current_balance, max_loss_percent):
    if start_balance <= 0: return False
    loss_pct = max(0, (start_balance-current_balance)/start_balance*100)
    return loss_pct < max_loss_percent
