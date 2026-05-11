from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from random import choice, randint, seed, sample
from collections import Counter, defaultdict
import os
import time
import requests

from app.database import Base, engine, get_db
from app.models import Restaurant, Customer, MenuItem, Order, OrderItem, AiMessage

app = FastAPI(title="JoeAI API", version="8.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for _ in range(90):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except Exception:
        time.sleep(1)

JOEAI_AI_URL = os.getenv("JOEAI_AI_URL", "http://ai:8099")

def fnum(v, d=0):
    try:
        return float(v) if v not in [None, ""] else d
    except Exception:
        return d

def inum(v, d=1):
    try:
        return int(v) if v not in [None, ""] else d
    except Exception:
        return d

def pdate(v):
    try:
        return datetime.strptime(str(v), "%Y-%m-%d").date() if v else date.today()
    except Exception:
        return date.today()

@app.get("/health")
def health():
    return {"status": "ok", "service": "joeai_backend", "version": "8.0.0", "ai_url": JOEAI_AI_URL}

@app.get("/ai/health")
def ai_health():
    try:
        return requests.get(JOEAI_AI_URL + "/health", timeout=10).json()
    except Exception as e:
        return {"status": "error", "url": JOEAI_AI_URL, "error": str(e)}

RESTAURANTS = [
    ("McDonald's Torino Porta Nuova Demo", "Fast Food", "Corso Vittorio Emanuele II, Torino", "+390110000001", "porta.demo@joeai.local", "https://demo.joeai.local"),
    ("JoeAI Pizza San Salvario", "Pizza", "Via Berthollet, Torino", "+390110000002", "pizza@joeai.local", "https://pizza.joeai.local"),
    ("Mole Bistro Demo", "Piedmontese", "Via Montebello, Torino", "+390110000003", "mole@joeai.local", "https://mole.joeai.local"),
    ("Quadrilatero Osteria Demo", "Italian", "Via Sant'Agostino, Torino", "+390110000004", "osteria@joeai.local", "https://osteria.joeai.local"),
]

MENUS = {
    "Fast Food": [("Big Mac","Burger",6.9,2.4),("McChicken","Burger",6.5,2.3),("Crispy McBacon","Burger",7.2,2.7),("Patatine Medie","Side",3.2,.8),("McFlurry","Dessert",3.9,1.1),("Coca-Cola Media","Drink",3.3,.55)],
    "Pizza": [("Margherita","Pizza",8,2.5),("Diavola","Pizza",10,3.2),("Bufalina","Pizza",12,4.2),("Patatine","Side",4,.9),("Tiramisu","Dessert",6,1.8),("Birra Media","Drink",5,1.1)],
    "Piedmontese": [("Agnolotti del Plin","Pasta",15,4.8),("Vitello Tonnato","Starter",11,3.9),("Brasato al Barolo","Main",22,8.5),("Bonet","Dessert",7,2.1)],
    "Italian": [("Carbonara","Pasta",12,3.2),("Lasagna","Pasta",13,3.8),("Risotto ai Funghi","Pasta",14,4.3),("Tiramisu","Dessert",6,1.8),("Spritz","Drink",7,1.7)],
}

NAMES = ["Marco Rossi","Sara Bianchi","Luca Verdi","Giulia Neri","Davide Costa","Elena Romano","Matteo Gallo","Chiara Ferri","Andrea Conti","Francesca Riva","Alessandro Greco","Martina Leone"]

def make_order(db, rid, customer, items, channel, order_date):
    order = Order(restaurant_id=rid, customer_id=customer.id, order_date=order_date, channel=channel, total_amount=0)
    db.add(order)
    db.flush()

    total = 0
    for raw in items:
        name = raw["name"]
        qty = inum(raw.get("quantity"), 1)
        mi = db.query(MenuItem).filter(MenuItem.restaurant_id == rid, MenuItem.name == name).first()
        price = float(mi.price if mi else raw.get("unit_price", 0))
        cost = float(mi.cost if mi else raw.get("unit_cost", 0))
        category = mi.category if mi else raw.get("category", "Other")
        line = round(price * qty, 2)
        total += line
        db.add(OrderItem(order_id=order.id, restaurant_id=rid, menu_item_id=mi.id if mi else None, item_name=name, category=category, quantity=qty, unit_price=price, unit_cost=cost, line_total=line))
        customer.favorite_item = name

    order.total_amount = round(total, 2)
    customer.total_spent = round(float(customer.total_spent or 0) + order.total_amount, 2)
    customer.visit_count = int(customer.visit_count or 0) + 1
    customer.last_visit = order_date
    return order

@app.post("/demo/reset")
def demo_reset(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed(42)
    today = date.today()
    total_customers = total_orders = total_items = 0

    for name, cuisine, address, phone, email, website in RESTAURANTS:
        r = Restaurant(name=name, city="Turin", cuisine=cuisine, address=address, phone=phone, email=email, website=website, logo_url="/joeai-logo.svg", status="Active")
        db.add(r)
        db.flush()

        for n, cat, price, cost in MENUS[cuisine]:
            db.add(MenuItem(restaurant_id=r.id, name=n, category=cat, price=price, cost=cost, active=True))
        db.flush()

        menu_rows = db.query(MenuItem).filter(MenuItem.restaurant_id == r.id).all()

        for i in range(100):
            first = today - timedelta(days=randint(60, 500))
            c = Customer(restaurant_id=r.id, name=f"{choice(NAMES)} {r.id}-{i}", phone=f"+3933{r.id:02d}{i:04d}", email=f"c{r.id}_{i}@demo.local", first_visit=first, last_visit=first, total_spent=0, visit_count=0, favorite_item=None, tags=choice(["vip","lunch","delivery","inactive","family","student"]), notes="demo", opted_in_whatsapp=True)
            db.add(c)
            db.flush()

            for _ in range(randint(1, 12)):
                picked = sample(menu_rows, min(randint(2, 4), len(menu_rows)))
                items = [{"name": x.name, "quantity": randint(1, 2)} for x in picked]
                make_order(db, r.id, c, items, choice(["dine_in","takeaway","delivery","glovo","just_eat","pos"]), first + timedelta(days=randint(0, max(1, (today-first).days))))
                total_orders += 1
                total_items += len(items)
            total_customers += 1

    db.commit()
    return {"status":"ok","restaurants":len(RESTAURANTS),"customers":total_customers,"orders":total_orders,"order_items":total_items}

@app.get("/restaurants")
def restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).order_by(Restaurant.id).all()

@app.post("/restaurants")
def add_restaurant(data: dict, db: Session = Depends(get_db)):
    r = Restaurant(name=data["name"], city=data.get("city","Turin"), cuisine=data.get("cuisine","Other"), address=data.get("address"), phone=data.get("phone"), email=data.get("email"), website=data.get("website"), logo_url="/joeai-logo.svg", status="Active")
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@app.get("/menu")
def menu(restaurant_id: int = 1, db: Session = Depends(get_db)):
    return db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).order_by(MenuItem.category, MenuItem.name).all()

@app.post("/menu")
def add_menu(data: dict, db: Session = Depends(get_db)):
    m = MenuItem(restaurant_id=int(data.get("restaurant_id",1)), name=data["name"], category=data.get("category","Other"), price=fnum(data.get("price")), cost=fnum(data.get("cost")), active=True)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@app.get("/customers")
def customers(restaurant_id: int = 1, limit: int = 500, query: str = "", category: str = "all", sort: str = "spent", db: Session = Depends(get_db)):
    rows = db.query(Customer).filter(Customer.restaurant_id == restaurant_id).all()
    q = query.lower().strip()
    if q:
        def val(c):
            if category == "id": return str(c.id)
            if category == "name": return c.name or ""
            if category == "phone": return c.phone or ""
            if category == "email": return c.email or ""
            if category == "favorite": return c.favorite_item or ""
            if category == "tags": return c.tags or ""
            return f"{c.id} {c.name} {c.phone} {c.email} {c.favorite_item} {c.tags}"
        rows = [c for c in rows if q in val(c).lower()]
    if sort == "orders":
        rows.sort(key=lambda x: x.visit_count or 0, reverse=True)
    elif sort == "name":
        rows.sort(key=lambda x: x.name or "")
    else:
        rows.sort(key=lambda x: x.total_spent or 0, reverse=True)
    return rows[:limit]

@app.post("/customers")
def add_customer(data: dict, db: Session = Depends(get_db)):
    c = Customer(restaurant_id=int(data.get("restaurant_id",1)), name=data["name"], phone=data["phone"], email=data.get("email"), first_visit=date.today(), last_visit=date.today(), total_spent=0, visit_count=0, favorite_item=data.get("favorite_item"), tags=data.get("tags"), notes=data.get("notes"), opted_in_whatsapp=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@app.post("/orders")
def add_order(data: dict, db: Session = Depends(get_db)):
    rid = int(data.get("restaurant_id", 1))
    cid = int(data["customer_id"])
    c = db.query(Customer).filter(Customer.id == cid, Customer.restaurant_id == rid).first()
    if not c:
        raise HTTPException(404, "Customer not found")
    items = data.get("items") or [{"name":data.get("item_name","Custom item"), "quantity":inum(data.get("quantity"),1), "unit_price":fnum(data.get("total_amount"))}]
    order = make_order(db, rid, c, items, data.get("channel","in_house"), pdate(data.get("order_date")))
    db.commit()
    db.refresh(order)
    return order

@app.get("/orders")
def orders(restaurant_id: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    rows = db.query(Order).filter(Order.restaurant_id == restaurant_id).order_by(Order.order_date.desc()).limit(limit).all()
    out = []
    for o in rows:
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        out.append({"id":o.id,"customer_id":o.customer_id,"channel":o.channel,"amount":o.total_amount,"date":str(o.order_date),"items_summary":", ".join([f"{i.quantity}x {i.item_name}" for i in items[:5]]),"items":[{"name":i.item_name,"quantity":i.quantity,"line_total":i.line_total} for i in items]})
    return out

@app.get("/analytics/items")
def analytics_items(restaurant_id: int = 1, customer_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(OrderItem).filter(OrderItem.restaurant_id == restaurant_id)
    if customer_id:
        ids = [o.id for o in db.query(Order).filter(Order.restaurant_id == restaurant_id, Order.customer_id == customer_id).all()]
        q = q.filter(OrderItem.order_id.in_(ids)) if ids else q.filter(OrderItem.id == -1)
    agg = defaultdict(lambda: {"quantity":0,"revenue":0.0,"cost":0.0})
    for i in q.all():
        qty = i.quantity or 1
        agg[i.item_name]["quantity"] += qty
        agg[i.item_name]["revenue"] += i.line_total or 0
        agg[i.item_name]["cost"] += (i.unit_cost or 0) * qty
    rows = [{"name":k,"quantity":int(v["quantity"]),"revenue":round(v["revenue"],2),"cost":round(v["cost"],2),"margin":round(v["revenue"]-v["cost"],2)} for k,v in agg.items()]
    rows.sort(key=lambda x: x["quantity"], reverse=True)
    return rows

def build_metrics(rid, db):
    today = date.today()
    r = db.query(Restaurant).filter(Restaurant.id == rid).first()
    cs = db.query(Customer).filter(Customer.restaurant_id == rid).all()
    os_ = db.query(Order).filter(Order.restaurant_id == rid).all()
    its = db.query(OrderItem).filter(OrderItem.restaurant_id == rid).all()
    menu_ = db.query(MenuItem).filter(MenuItem.restaurant_id == rid).all()

    inactive = [c for c in cs if c.last_visit and c.last_visit < today - timedelta(days=45)]
    cold = [c for c in cs if c.last_visit and c.last_visit < today - timedelta(days=90)]
    returning = [c for c in cs if (c.visit_count or 0) >= 2]
    vip = [c for c in cs if (c.total_spent or 0) >= 250]

    revenue = round(sum(o.total_amount or 0 for o in os_), 2)
    cost = round(sum((i.unit_cost or 0) * (i.quantity or 1) for i in its), 2)
    avg_spend = round(sum(c.total_spent or 0 for c in cs) / len(cs), 2) if cs else 0

    item_qty = Counter()
    item_rev = defaultdict(float)
    channels = defaultdict(float)
    monthly = defaultdict(float)

    for i in its:
        item_qty[i.item_name] += i.quantity or 1
        item_rev[i.item_name] += i.line_total or 0
    for o in os_:
        channels[o.channel] += o.total_amount or 0
        monthly[o.order_date.strftime("%Y-%m")] += o.total_amount or 0

    kpis = {
        "customers":len(cs),
        "orders":len(os_),
        "order_items":len(its),
        "inactive":len(inactive),
        "cold":len(cold),
        "returning":len(returning),
        "vip":len(vip),
        "total_revenue":revenue,
        "total_cost_estimate":cost,
        "gross_margin_estimate":round(revenue-cost,2),
        "avg_order":round(revenue/len(os_),2) if os_ else 0,
        "average_spend":avg_spend,
        "repeat_rate":round(len(returning)/len(cs)*100,1) if cs else 0,
        "churn_risk_rate":round(len(cold)/len(cs)*100,1) if cs else 0,
        "ltv_estimate":round(avg_spend*2.4,2),
        "campaign_roi":312,
        "menu_items":len(menu_),
        "estimated_app_value":round(len(inactive)*avg_spend*.18,2),
    }

    revenue_12 = []
    for i in range(11, -1, -1):
        m = today.replace(day=1) - timedelta(days=i*30)
        key = m.strftime("%Y-%m")
        revenue_12.append({"month":key,"value":round(monthly.get(key,0),2)})

    charts = {
        "top_selling_items":[{"name":x,"quantity":q,"revenue":round(item_rev[x],2)} for x,q in item_qty.most_common(12)],
        "revenue_by_channel":[{"name":x,"value":round(v,2)} for x,v in channels.items()],
        "revenue_12_months":revenue_12,
        "returning_vs_non":[{"name":"Returning","value":len(returning)},{"name":"Non-returning","value":len(cs)-len(returning)}],
        "favorite_items":[{"name":x,"value":q} for x,q in Counter([c.favorite_item for c in cs if c.favorite_item]).most_common(8)],
    }

    return r, cs, os_, its, menu_, kpis, charts

@app.get("/dashboard")
def dashboard(restaurant_id: int = 1, db: Session = Depends(get_db)):
    r, cs, os_, its, menu_, k, ch = build_metrics(restaurant_id, db)
    if not r:
        raise HTTPException(404, "Restaurant not found")
    return {
        "restaurant":{"id":r.id,"name":r.name,"city":r.city,"cuisine":r.cuisine,"address":r.address,"phone":r.phone,"email":r.email,"website":r.website,"logo_url":r.logo_url,"status":r.status},
        "kpis":k,
        "charts":ch,
        "customers":[{"id":c.id,"name":c.name,"phone":c.phone,"email":c.email,"spent":c.total_spent,"orders":c.visit_count,"favorite_item":c.favorite_item,"tags":c.tags,"last_visit":str(c.last_visit)} for c in sorted(cs,key=lambda x:x.total_spent or 0,reverse=True)[:160]],
        "orders":orders(restaurant_id,100,db),
        "menu":[{"id":m.id,"name":m.name,"category":m.category,"price":m.price,"cost":m.cost,"active":m.active} for m in menu_],
        "campaign_strategies":[{"name":"Win-back inactive guests","audience":f"{k['inactive']} inactive customers","timing":"Tue/Wed 17:00","offer":"free dessert or 15% comeback offer","expected_uplift":18},{"name":"Cold 90-day recovery","audience":f"{k['cold']} cold customers","timing":"Wed 17:30","offer":"strong limited-time return offer","expected_uplift":11},{"name":"VIP loyalty","audience":f"{k['vip']} VIP customers","timing":"Thu 16:00","offer":"priority booking / special menu","expected_uplift":22}],
    }

@app.post("/campaigns/generate")
def campaign(data: dict, db: Session = Depends(get_db)):
    rid = int(data.get("restaurant_id", 1))
    segment = data.get("segment", "inactive")
    r, cs, os_, its, menu_, k, ch = build_metrics(rid, db)

    targets = sorted(cs, key=lambda x: x.total_spent or 0, reverse=True)[:50]

    ai_task = (
        f"Create a detailed WhatsApp campaign for segment: {segment}. "
        f"Include campaign name, audience logic, reason, offer, timing, "
        f"3 Italian WhatsApp message variants, follow-up message, and KPIs to measure."
    )

    ai_answer = ask_service(r, k, ch, cs, ai_task)

    return {
        "strategy": {
            "name": f"AI {segment} campaign",
            "audience": f"{len(targets)} selected customers",
            "timing": "AI recommended",
            "offer": "AI generated",
            "expected_uplift": 15,
            "ai_plan": ai_answer
        },
        "target_count": len(targets),
        "messages": [
            {
                "customer_id": c.id,
                "name": c.name,
                "phone": c.phone,
                "message": f"Ciao {c.name}, ci manchi da {r.name}. Questa settimana abbiamo una proposta speciale per te. Ti va di prenotare?"
            }
            for c in targets
        ],
    }


def ask_service(r, k, ch, cs, task):
    top_customers = [{"id":c.id,"name":c.name,"spent":c.total_spent,"orders":c.visit_count,"favorite_item":c.favorite_item,"last_visit":str(c.last_visit),"tags":c.tags} for c in sorted(cs,key=lambda x:x.total_spent or 0,reverse=True)[:8]]
    try:
        res = requests.post(JOEAI_AI_URL + "/marketing", json={"restaurant":{"name":r.name,"cuisine":r.cuisine,"city":r.city},"kpis":k,"top_items":ch.get("top_selling_items",[])[:8],"top_customers":top_customers,"task":task}, timeout=60)
        if res.status_code != 200:
            return f"AI service error {res.status_code}: {res.text[:500]}"
        return res.json().get("answer","No answer generated.")
    except Exception:
        churn = k.get("churn_risk_rate", 0)
        cold = k.get("cold", 0)
        customers = k.get("customers", 0)
        return (
            f"Churn rate means the percentage of customers who stopped coming back. "
            f"In JoeAI, churn risk is estimated as cold customers divided by total customers. "
            f"For this restaurant, the current churn risk is {churn}% ({cold} cold customers out of {customers}). "
            f"Business action: target cold/inactive customers with a WhatsApp win-back offer, sent mid-week around 17:00, with a simple comeback incentive."
        )

@app.post("/ai/ask")
def ai_ask(data: dict, db: Session = Depends(get_db)):
    rid = int(data.get("restaurant_id",1))
    area = data.get("area","marketing")
    q = data.get("question","Give recommendations")
    r, cs, os_, its, menu_, k, ch = build_metrics(rid, db)
    return {"answer":ask_service(r,k,ch,cs,f"{area}: {q}"),"provider":"joeai_ai_qwen","ai_url":JOEAI_AI_URL}

@app.post("/ai/quick")
def ai_quick(data: dict, db: Session = Depends(get_db)):
    return ai_ask(data, db)

@app.post("/ai/deep")
def ai_deep(data: dict, db: Session = Depends(get_db)):
    return ai_ask(data, db)

@app.post("/ai/accounting")
def ai_accounting(data: dict, db: Session = Depends(get_db)):
    data["area"] = "accounting"
    return ai_ask(data, db)

@app.post("/ai/campaign")
def ai_campaign(data: dict, db: Session = Depends(get_db)):
    data["area"] = "campaign"
    return ai_ask(data, db)

@app.post("/ai/customer-sort")
def ai_customer_sort(data: dict, db: Session = Depends(get_db)):
    data["area"] = "customer prioritization"
    return ai_ask(data, db)

@app.post("/campaigns/ai-generate")
def ai_campaign_generate(data: dict, db: Session = Depends(get_db)):
    rid = int(data.get("restaurant_id", 1))
    segment = data.get("segment", "inactive")
    r, cs, os_, its, menu_, k, ch = build_metrics(rid, db)

    targets = sorted(cs, key=lambda x: x.total_spent or 0, reverse=True)[:30]

    task = (
        f"Create a serious restaurant WhatsApp campaign for segment '{segment}'. "
        f"Use the restaurant data. Include: campaign name, target logic, business reason, "
        f"offer, timing, 3 Italian WhatsApp message variants, follow-up, expected uplift, "
        f"and KPIs to measure. Be specific and not generic."
    )

    ai_plan = ask_service(r, k, ch, cs, task)

    messages = []
    for c in targets:
        messages.append({
            "customer_id": c.id,
            "name": c.name,
            "phone": c.phone,
            "message": (
                f"Ciao {c.name}, abbiamo pensato a una proposta dedicata per te da {r.name}. "
                f"Questa settimana puoi tornare con un vantaggio speciale sul tuo prossimo ordine. "
                f"Ti va di prenotare o passare a trovarci?"
            )
        })

    return {
        "strategy": {
            "name": f"AI {segment} recovery campaign",
            "audience": f"{len(targets)} selected customers",
            "segment": segment,
            "ai_plan": ai_plan
        },
        "target_count": len(targets),
        "messages": messages
    }
