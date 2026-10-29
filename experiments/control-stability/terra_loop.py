"""Models of Terra's control loops, ported from the Rust code (Terra main, 2026-10-28).

speed/yaw PI: crates/terra-control/src/lib.rs   turning limiter: crates/terra-control/src/turning.rs
pursuit law: crates/terra-waypoint/src/lib.rs   100 Hz tick, every 5th tick routed: crates/terra-mobile/src/{drive_loop,gate}.rs
"""
import numpy as np
DT=0.01
class PI:
    def __init__(s,kp=0.3,ki=0.6,ff=1/3,aw=4.0,emax=1.0,deadband=0.0):
        s.kp,s.ki,s.ff,s.aw,s.emax,s.db=kp,ki,ff,aw,emax,deadband; s.I=0.0
    def step(s,r,y,dt=DT,hold=False):
        if hold: s.I=0.0; return 0.0
        e=r-y; u=s.ff*r+s.kp*e+s.I
        sc=max(abs(u)/s.emax,1.0); ua=u/sc
        s.I=np.clip(s.I+(s.ki*e+s.aw*(ua-u))*dt,-s.emax,s.emax)
        if r==0 and abs(y)<0.015: s.I=0.0; ua=0.0
        if s.db>0:
            ua=0.0 if abs(ua)<0.01 else np.sign(ua)*(s.db+(s.emax-s.db)*min(abs(ua)/s.emax,1))
        return ua
def simulate(ref,K=1.0,d=0.0,tau=0.15,L=0.1,scale=0.88,tf=0.03,vio_lag=0.06,ctl=None,
             tick=0.01,route_every=5,gate_hold=None,ctl_hold=None,T=None):
    """ref: function t->target (phone-frame m/s). Returns t, true v, phone v, effort.
    gate_hold(t): motors forced to 0 but controller keeps integrating (gate-level hold).
    ctl_hold(t): controller safety hold (integrals cleared)."""
    ctl=ctl or PI()
    n=int(T/DT); t=np.arange(n)*DT
    v=np.zeros(n); meas=np.zeros(n); u_out=np.zeros(n)
    nL=int(round(L/DT)); nV=int(round(vio_lag/DT))
    buf=[0.0]*(nL+1)
    yf=0.0; held=0.0; last_tick=-1e9; u=0.0; k_tick=0
    for k in range(1,n):
        tk=t[k]
        # sensor: VIO sample delayed, LPF (phone frame)
        idx=max(k-1-nV,0)
        yf+= (DT/(tf+DT))*(scale*v[idx]-yf) if tf>0 else (scale*v[idx]-yf)
        meas[k]=yf
        if tk-last_tick>=tick-1e-9:
            last_tick=tk
            u=ctl.step(ref(tk),yf,dt=tick,hold=bool(ctl_hold and ctl_hold(tk)))
            if k_tick%route_every==0: held=0.0 if (gate_hold and gate_hold(tk)) else u
            k_tick+=1
        buf.append(held); a=buf.pop(0)
        # plant: deadband offset then first order
        drive=np.sign(a)*max(abs(a)-d,0.0)
        v[k]=v[k-1]+DT/tau*(K*drive-v[k-1])
        u_out[k]=held
    return t,v,meas,u_out

def loop(w,kp,ki,K,tau,theta,tf=0.0):
    s=1j*w
    return (kp+ki/s)*K*np.exp(-theta*s)/((tau*s+1)*(tf*s+1))
def margins(Lf,w):
    mag=np.abs(Lf); ph=np.unwrap(np.angle(Lf))
    out={}
    i=np.flatnonzero((mag[:-1]>=1)&(mag[1:]<1))
    if len(i):
        i=i[-1]; f=(np.log(mag[i])-0)/(np.log(mag[i])-np.log(mag[i+1]))
        wc=np.exp(np.log(w[i])+f*(np.log(w[i+1])-np.log(w[i]))); phc=ph[i]+f*(ph[i+1]-ph[i])
        out['wc']=wc; out['pm']=np.degrees(phc)+180; out['dm']=np.radians(out['pm'])/wc
    else: out['wc']=np.nan; out['pm']=np.nan; out['dm']=np.nan
    j=np.flatnonzero((ph[:-1]>-np.pi)&(ph[1:]<=-np.pi))
    if len(j):
        j=j[0]; f=(ph[j]+np.pi)/(ph[j]-ph[j+1]); m=mag[j]+f*(mag[j+1]-mag[j])
        out['w180']=w[j]+f*(w[j+1]-w[j]); out['gm_db']=-20*np.log10(m)
    else: out['w180']=np.nan; out['gm_db']=np.inf
    return out

import numpy as np

def wrap(a): return (a+np.pi)%(2*np.pi)-np.pi
class Turning:
    def __init__(s,maxw=0.5,acc=0.5,dec=0.8,R=0.5,inplace=False): s.maxw,s.acc,s.dec,s.R,s.ip=maxw,acc,dec,R,inplace; s.prev=None
    def step(s,v,w,dt):
        cap=s.maxw if s.ip else min(s.maxw,abs(v)/s.R)
        des=np.clip(w,-cap,cap); p=0.0 if s.prev is None else s.prev
        rev=p*des<0; goal=0.0 if rev else des
        rate=s.dec if (rev or abs(goal)<abs(p)) else s.acc
        out=np.clip(p+np.clip(goal-p,-rate*dt,rate*dt),-cap,cap); s.prev=out; return out
def pursuit(x,y,yaw,gx,gy,cruise=1.0,k=1.6,wmax=1.2,gate=0.55,slow=3.0,arrive=0.05):
    dx,dy=gx-x,gy-y; D=np.hypot(dx,dy)
    if D<=arrive: return 0.0,0.0
    e=wrap(np.arctan2(dy,dx)-yaw); w=np.clip(k*e,-wmax,wmax)
    if abs(e)>=gate: return 0.0,w
    return cruise*(1-abs(e)/gate)*(max(D/slow,0.2) if D<slow else 1.0), w
def run(route,start=(0,0,0),cruise=1.0,k=1.6,Kv=0.93/0.88,d=0.06,Kpsi=1.6,L=0.2,tau=0.02,scale=0.88,
        gains=(0.3,0.6,1/3,0.1,0.3,0.2),T=40,visible=None,turning=None,max_lin=2.0):
    kp,ki,ff,ykp,yki,yff=gains
    x,y,yaw=start; v=0.0; w=0.0; Il=0.0; Iy=0.0
    nL=int(L/DT); buf=[(0.0,0.0)]*(nL+1); held=(0.0,0.0)
    tl=turning or Turning(); idx=0; out=[]; vf=0.0
    for k_ in range(int(T/DT)):
        t=k_*DT
        # drop reached points / advance when next visible
        while idx<len(route)-1 and (np.hypot(route[idx][0]-x,route[idx][1]-y)<0.2 or (visible and visible(x,y,idx+1))): idx+=1
        gx,gy=route[idx]
        lin_i,ang_i=pursuit(x,y,yaw,gx,gy,cruise=cruise,k=k)
        if idx==len(route)-1 and np.hypot(gx-x,gy-y)<=0.75: lin_i,ang_i=0.0,0.0
        lin_i=min(lin_i,max_lin)
        ang=tl.step(lin_i,ang_i,DT) if (lin_i!=0 or ang_i!=0) else 0.0
        # sensors: phone forward (scaled, 30 ms filter, 60 ms lag approximated by filter), gyro yaw
        vf+= DT/(0.09+DT)*(scale*v-vf)
        el=lin_i-vf; ey=ang-w
        ul=ff*lin_i+kp*el+Il; uy=yff*ang+ykp*ey+Iy
        l,r=ul-uy,ul+uy; sc=max(abs(l),abs(r),1.0); l,r=l/sc,r/sc
        if l*r<0:  # no opposite wheels (Terra, no in-place)
            f=(l+r)/2; l,r=(max(l,0),max(r,0)) if f>0 else ((min(l,0),min(r,0)) if f<0 else (0,0))
        al,ay=(l+r)/2,(r-l)/2
        Il=np.clip(Il+(ki*el+4*(al-ul))*DT,-1,1); Iy=np.clip(Iy+(yki*ey+4*(ay-uy))*DT,-1,1)
        if lin_i==0 and ang==0 and abs(vf)<0.015 and abs(w)<0.015: Il=Iy=0; al=ay=0
        if k_%5==0: held=(al,ay)
        buf.append(held); a=buf.pop(0)
        dz=np.sign(a[0])*max(abs(a[0])-d,0)
        v+=DT/tau*(Kv*dz-v); w+=DT/tau*(Kpsi*a[1]-w)
        yaw+=w*DT; x+=v*np.cos(yaw)*DT; y+=v*np.sin(yaw)*DT
        out.append((t,x,y,yaw,v,w,lin_i,ang,idx))
    return np.array(out)
