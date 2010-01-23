import random

def paroli(unit_bet,stop_step,old_bet,payoff,current_step,**kwargs):
    if payoff==0 or current_step==0:
        return unit_bet
    else:
        current_step+=1
        current_step%=stop_step
        return old_bet+payoff

def labouchere(unit_bet):
    series=[]
    def bet(last_payoff,**kwargs):
        s = series;
        if s == []:
            s+=[random.randrange(1,10) for _ in range(6)]
        if last_payoff>0:
            s.pop(0)
            s.pop(-1)
        elif last_payoff==0:
            s.append(s[0]+s[-1])
        print repr(s)
        print repr(series)
        return unit_bet*(s[0]+s[-1])
    return bet


if __name__ == '__main__' :
    x = labouchere(3)
    print x(-1)
    print x(3)
    print x(0)
