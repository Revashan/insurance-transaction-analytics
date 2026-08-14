from pathlib import Path
import pandas as pd
import numpy as np
import random

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)
random.seed(42)
source_updated = pd.Timestamp("2026-08-01")

states_cities = {
    "Kuala Lumpur":["Kuala Lumpur"],
    "Selangor":["Shah Alam","Petaling Jaya","Subang Jaya","Klang"],
    "Johor":["Johor Bahru","Batu Pahat","Muar"],
    "Penang":["George Town","Bayan Lepas","Butterworth"],
    "Perak":["Ipoh","Taiping"],
    "Sabah":["Kota Kinabalu","Sandakan"],
    "Sarawak":["Kuching","Miri"],
    "Melaka":["Melaka City"],
    "Negeri Sembilan":["Seremban"],
}
states=list(states_cities)

# Customers
n=6000
customer_ids=[f"CUST{i:06d}" for i in range(1,n+1)]
dob0=np.datetime64("1955-01-01"); dob1=np.datetime64("2003-12-31")
dobs=dob0+rng.integers(0,(dob1-dob0).astype(int),n).astype("timedelta64[D]")
cust_states=rng.choice(states,n,p=[.18,.24,.13,.10,.08,.07,.07,.06,.07])
customers=pd.DataFrame({
    "customer_id":customer_ids,
    "gender":rng.choice(["Female","Male"],n,p=[.49,.51]),
    "date_of_birth":pd.to_datetime(dobs),
    "state":cust_states,
    "city":[random.choice(states_cities[s]) for s in cust_states],
    "income_band":rng.choice(["<RM3k","RM3k-6k","RM6k-10k","RM10k-15k",">RM15k"],n,p=[.18,.30,.25,.16,.11]),
    "risk_segment":rng.choice(["Low","Medium","High"],n,p=[.54,.34,.12]),
    "customer_since":pd.to_datetime(rng.integers(pd.Timestamp("2018-01-01").value//10**9,pd.Timestamp("2025-12-31").value//10**9,n),unit="s").normalize(),
    "source_updated_at":source_updated
})

# Agents
n_agents=80
agent_ids=[f"AGT{i:04d}" for i in range(1,n_agents+1)]
agents=pd.DataFrame({
    "agent_id":agent_ids,
    "agent_name":[f"Agent {i:03d}" for i in range(1,n_agents+1)],
    "sales_channel":rng.choice(["Agency","Bancassurance","Digital","Broker"],n_agents,p=[.42,.25,.23,.10]),
    "region":rng.choice(["Central","Northern","Southern","East Malaysia"],n_agents,p=[.38,.20,.20,.22]),
    "tenure_years":rng.integers(1,16,n_agents),
    "source_updated_at":source_updated
})

# Policies
n_policies=9000
policy_ids=[f"POL{i:07d}" for i in range(1,n_policies+1)]
products=rng.choice(["Motor","Medical","Life","Travel","Home"],n_policies,p=[.31,.25,.20,.14,.10])
starts=pd.to_datetime(rng.integers(pd.Timestamp("2023-01-01").value//10**9,pd.Timestamp("2026-07-31").value//10**9,n_policies),unit="s").normalize()
terms=np.where(products=="Travel",rng.integers(7,91,n_policies),rng.integers(330,396,n_policies))
ends=starts+pd.to_timedelta(terms,unit="D")
premium_ranges={"Motor":(800,2600),"Medical":(1000,5200),"Life":(1200,7000),"Travel":(60,850),"Home":(300,1800)}
insured_ranges={"Motor":(20000,180000),"Medical":(50000,500000),"Life":(100000,1500000),"Travel":(20000,150000),"Home":(80000,900000)}
premiums=[round(rng.uniform(*premium_ranges[p]),2) for p in products]
insured=[round(rng.uniform(*insured_ranges[p]),2) for p in products]
today=pd.Timestamp("2026-08-01")
statuses=[]
for s,e in zip(starts,ends):
    statuses.append(rng.choice(["Expired","Renewed","Cancelled"],p=[.42,.48,.10]) if e<today else rng.choice(["Active","Cancelled"],p=[.94,.06]))
policies=pd.DataFrame({
    "policy_id":policy_ids,
    "customer_id":rng.choice(customer_ids,n_policies),
    "agent_id":rng.choice(agent_ids,n_policies),
    "product_type":products,
    "policy_start_date":starts,
    "policy_end_date":ends,
    "annual_premium":premiums,
    "sum_insured":insured,
    "payment_frequency":rng.choice(["Monthly","Quarterly","Semi-Annual","Annual"],n_policies,p=[.40,.18,.12,.30]),
    "policy_status":statuses,
    "renewal_flag":[1 if x=="Renewed" else 0 for x in statuses],
    "source_updated_at":source_updated
})

# Transactions
n_tx=75000
ix=rng.integers(0,n_policies,n_tx)
px=policies.iloc[ix].reset_index(drop=True)
dates=[]
for _,r in px.iterrows():
    lo=max(r.policy_start_date,pd.Timestamp("2024-01-01"))
    hi=min(max(r.policy_end_date,lo+pd.Timedelta(days=1)),pd.Timestamp("2026-07-31"))
    dates.append(lo+pd.Timedelta(days=int(rng.integers(0,max((hi-lo).days,1)+1))))
types=rng.choice(["PREMIUM_PAYMENT","CLAIM_PAYOUT","REFUND","ADJUSTMENT","CANCELLATION_FEE"],n_tx,p=[.72,.13,.05,.07,.03])
amounts=[]
for t,a in zip(types,px.annual_premium):
    if t=="PREMIUM_PAYMENT": v=a*rng.choice([1/12,1/4,1/2,1],p=[.45,.20,.10,.25])
    elif t=="CLAIM_PAYOUT": v=rng.uniform(500,30000)
    elif t=="REFUND": v=-rng.uniform(20,min(a,1000))
    elif t=="ADJUSTMENT": v=rng.normal(0,max(a*.08,10))
    else: v=rng.uniform(20,250)
    amounts.append(round(float(v),2))
pay_status=rng.choice(["SUCCESS","FAILED","PENDING"],n_tx,p=[.932,.052,.016])
reasons=["Payment gateway timeout","Insufficient funds","Invalid account","Duplicate request","Bank unavailable"]
transactions=pd.DataFrame({
    "transaction_id":[f"TXN{i:09d}" for i in range(1,n_tx+1)],
    "policy_id":px.policy_id.values,
    "transaction_date":dates,
    "transaction_type":types,
    "transaction_amount":amounts,
    "payment_method":rng.choice(["FPX","Card","Direct Debit","E-Wallet","Bank Transfer"],n_tx,p=[.30,.25,.21,.14,.10]),
    "payment_status":pay_status,
    "transaction_channel":rng.choice(["Web","Mobile App","Agent Portal","Bank Partner","Batch"],n_tx,p=[.25,.30,.20,.15,.10]),
    "processing_seconds":np.maximum(1,np.round(rng.gamma(2.3,1.6,n_tx),2)),
    "failure_reason":[random.choice(reasons) if s=="FAILED" else "" for s in pay_status],
    "source_updated_at":source_updated
})

# Claims
n_claims=12000
ix=rng.integers(0,n_policies,n_claims)
cp=policies.iloc[ix].reset_index(drop=True)
claim_dates=[]
for _,r in cp.iterrows():
    lo=max(r.policy_start_date,pd.Timestamp("2024-01-01"))
    hi=min(max(r.policy_end_date,lo+pd.Timedelta(days=1)),pd.Timestamp("2026-07-31"))
    claim_dates.append(lo+pd.Timedelta(days=int(rng.integers(0,max((hi-lo).days,1)+1))))
cstatus=rng.choice(["APPROVED","REJECTED","PENDING","UNDER_REVIEW"],n_claims,p=[.66,.14,.11,.09])
claim_type_map={
    "Motor":["Accident","Theft","Windshield"],"Medical":["Hospitalisation","Outpatient","Surgery"],
    "Life":["Death Benefit","Critical Illness","Disability"],"Travel":["Trip Delay","Medical Abroad","Lost Baggage"],
    "Home":["Fire","Flood","Theft"]
}
ctypes=[random.choice(claim_type_map[p]) for p in cp.product_type]
claim_amount=[]; approved=[]; days=[]; scores=[]; flags=[]
# Product severity multipliers calibrated so loss ratio is portfolio-realistic.
severity={"Motor":0.185,"Medical":0.195,"Life":0.160,"Travel":0.048,"Home":0.062}
for st,p,si in zip(cstatus,cp.product_type,cp.sum_insured):
    cap=min(float(si)*.35,80000)
    amt=float(rng.uniform(200,max(cap,500)))*severity[p]
    claim_amount.append(round(amt,2))
    if st=="APPROVED":
        appr=amt*float(rng.uniform(.72,1.0)); d=int(max(1,rng.normal(13 if p!="Life" else 21,7)))
    elif st=="REJECTED":
        appr=0; d=int(max(2,rng.normal(9,5)))
    else:
        appr=0; d=0
    approved.append(round(appr,2)); days.append(d)
    score=float(np.clip(rng.beta(2,7)*100,0,100))
    if rng.random()<.035: score=float(rng.uniform(72,99))
    scores.append(round(score,2)); flags.append(1 if score>=75 else 0)

claims=pd.DataFrame({
    "claim_id":[f"CLM{i:08d}" for i in range(1,n_claims+1)],
    "policy_id":cp.policy_id.values,
    "claim_date":claim_dates,
    "claim_type":ctypes,
    "claim_amount":claim_amount,
    "approved_amount":approved,
    "claim_status":cstatus,
    "days_to_settle":days,
    "fraud_score":scores,
    "fraud_flag":flags,
    "source_updated_at":source_updated
})

for name,df in [("customers",customers),("agents",agents),("policies",policies),("transactions",transactions),("claims",claims)]:
    df.to_csv(RAW/f"{name}.csv",index=False,date_format="%Y-%m-%d")
print("Regenerated deterministic synthetic raw data in", RAW)
