import random

def paroli(unit_bet,stop_step,table_min,table_max):
    old_bet=[0]
    current_step=[0]
    def bet(**kwargs):
        last_payoff=kwargs['last_payoff']
        ob=old_bet
        cs=current_step
        if last_payoff==0:
            cs[0]=0
            ob[0] = unit_bet
        elif cs[0]==0:
            ob[0] = unit_bet
        elif last_payoff>0:
            ob[0]+=last_payoff
        cs[0]+=1
        cs[0]%=stop_step
        ob[0] = max(min(table_max,ob[0]),table_min)
        return ob[0]
    return bet

def labouchere(unit_bet,table_min,table_max):
    series=[]
    def bet(**kwargs):
        last_payoff=kwargs['last_payoff']
        s = series;
        if s == []:
            s+=[random.randrange(1,10) for _ in range(6)]
        if last_payoff>0:
            s.pop(0)
            s.pop(-1)
        elif last_payoff==0:
            s.append(s[0]+s[-1])
        #print repr(s)
        #print repr(series)
        return max(min(unit_bet*(s[0]+s[-1]),table_max),table_min)
    return bet

def martingale(unit_bet,table_min,table_max):
    old_bet=[0]
    def bet(**kwargs):
        last_payoff=kwargs['last_payoff']
        ob=old_bet
        if last_payoff==0:
            ob[0]*=2
        else:
            ob[0]=unit_bet
        ob[0] = max(min(table_max,ob[0]),table_min)
        return ob[0]
    return bet

def random_bet(table_min,table_max):
    def bet(**kwargs):
        money=kwargs['money']
        limit=max(table_min,money/4)
        return min(random.randint(table_min,limit),table_max)
    return bet

def kelly(table_min,table_max):
    def bet(**kwargs):
        probability=kwargs['edge']
        money=kwargs['money']
        return max(min(table_max,money*(2.0*probability-1)),table_min)
    return bet

def half_kelly(table_min,table_max):
    def bet(**kwargs):
        probability=kwargs['edge']
        money=kwargs['money']
        return max(min(table_max,money*(probability-0.5)),table_min)
    return bet

def count_bet(table_min,table_max):
    def bet(**kwargs):
        count=kwargs['edge']
        return max(min(table_max,count*table_min),table_min)
    return bet

if __name__ == '__main__' :
    x = labouchere(3)
    print x(-1)
    print x(3)
    print x(0)
