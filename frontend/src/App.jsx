import { useCallback, useEffect, useMemo, useState } from 'react'
import { Activity, ArrowDownToLine, BarChart3, CalendarClock, ChartNoAxesCombined, CircleDollarSign, ClipboardList, Database, Filter, LayoutDashboard, RefreshCw, ShoppingBag, Store, Utensils } from 'lucide-react'
import api from './api'
import StatCard from './components/StatCard'
import Filters from './components/Filters'
import { RevenueChart, CategoryChart, OrderTypeChart } from './components/Charts'
import OrdersTable from './components/OrdersTable'

const emptyFilters = { start_date:'', end_date:'', outlet:'', brand:'', category:'', order_type:'', settlement:'' }
const money = n => `₹${Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
const number = n => Number(n || 0).toLocaleString('en-IN')
export default function App() {
  const [filters,setFilters] = useState({})
  const [values,setValues] = useState(emptyFilters)
  const [overview,setOverview] = useState({})
  const [trend,setTrend] = useState([])
  const [categories,setCategories] = useState([])
  const [types,setTypes] = useState([])
  const [outlets,setOutlets] = useState([])
  const [orders,setOrders] = useState({items:[],total:0,total_pages:1})
  const [page,setPage] = useState(1)
  const [search,setSearch] = useState('')
  const [loading,setLoading] = useState(true)
  const [error,setError] = useState('')
  const query = useMemo(()=>Object.fromEntries(Object.entries(values).filter(([,v])=>v)),[values])
  const params = useMemo(()=>({...query,page,page_size:25,...(search?{search}:{})}),[query,page,search])
  useEffect(()=>{ api.get('/api/filters').then(r=>setFilters(r.data)).catch(()=>setError('Cannot connect to the analytics API. Start the backend and check VITE_API_URL.')) },[])
  const load = useCallback(async()=>{
    setLoading(true); setError('')
    try {
      const [o,t,c,ot,top,ord] = await Promise.all([
        api.get('/api/overview',{params:query}),
        api.get('/api/revenue-trend',{params:query}),
        api.get('/api/category-breakdown',{params:query}),
        api.get('/api/order-types',{params:query}),
        api.get('/api/top-outlets',{params:query}),
        api.get('/api/orders',{params})
      ])
      setOverview(o.data);setTrend(t.data);setCategories(c.data);setTypes(ot.data);setOutlets(top.data);setOrders(ord.data)
    } catch(e) { setError(e.response?.data?.detail || 'Unable to load dashboard data. Check that the API is running and the dataset has been imported.') }
    finally { setLoading(false) }
  },[query,params])
  useEffect(()=>{load()},[load])
  const reset=()=>{setValues(emptyFilters);setSearch('');setPage(1)}
  const exportCsv=()=>{
    const headers=['BillNo','Outlet','DateTime','Item','Category','Quantity','UnitPrice','Revenue','OrderType','Payment']
    const rows=orders.items.map(r=>[r.bill_no,r.outlet_name,r.order_datetime,r.item,r.category,r.quantity,r.price,r.revenue,r.order_type,r.settlement])
    const csv=[headers,...rows].map(row=>row.map(v=>`"${String(v??'').replaceAll('"','""')}"`).join(',')).join('\n')
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));const a=document.createElement('a');a.href=url;a.download='orders-page.csv';a.click();URL.revokeObjectURL(url)
  }
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand-mark"><div className="brand-icon"><ChartNoAxesCombined size={21}/></div><div><b>insight<span>ly.</span></b><small>BUSINESS ANALYTICS</small></div></div>
      <div className="side-label">WORKSPACE</div><div className="nav-item active"><LayoutDashboard size={17}/> Overview</div>
      <div className="side-label data-label">DATA</div><div className="nav-item"><Database size={17}/> Order analytics</div><div className="nav-item"><Store size={17}/> Outlet performance</div>
      <div className="sidebar-bottom"><div className="db-status"><span className="live-dot"></span><div><b>Data connected</b><small>Restaurant dataset</small></div></div><small className="version">ANALYTICS DASHBOARD · v1.0</small></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div className="breadcrumb">Workspace <span>/</span> <b>Overview</b></div><div className="topbar-right"><span className="date-chip"><CalendarClock size={15}/> Jun 2025 – Jun 2026</span><div className="avatar">BA</div></div></header>
      <div className="content">
        <div className="page-heading"><div><div className="eyebrow">RESTAURANT PERFORMANCE</div><h1>Business overview</h1><p>Track revenue, orders and outlet performance in one place.</p></div><button className="refresh-button" onClick={load}><RefreshCw size={15}/> Refresh data</button></div>
        {error && <div className="error-banner">{error}</div>}
        <Filters filters={filters} values={values} setValues={v=>{setValues(v);setPage(1)}} onReset={reset}/>
        <div className="section-heading"><div><h2>Key performance indicators</h2><p>Business snapshot for the selected period</p></div><span className="live-tag"><span className="live-dot"/> LIVE DATA</span></div>
        <div className="stats-grid">
          <StatCard label="Total revenue" value={money(overview.total_revenue)} hint="Price × quantity" icon={CircleDollarSign} tone="purple"/>
          <StatCard label="Total orders" value={number(overview.total_orders)} hint="Unique bill numbers" icon={ShoppingBag} tone="teal"/>
          <StatCard label="Average order value" value={money(overview.average_order_value)} hint="Revenue per order" icon={Activity} tone="orange"/>
          <StatCard label="Line item records" value={number(overview.total_records)} hint={`${number(overview.total_quantity)} units sold`} icon={ClipboardList} tone="pink"/>
        </div>
        <div className="charts-grid">
          <section className="panel revenue-panel"><div className="panel-title"><div><h3>Revenue trend</h3><p>Daily revenue across the selected period</p></div><span className="chart-icon"><Activity size={17}/></span></div>
            {loading?<div className="chart-loading">Loading analytics…</div>:<RevenueChart data={trend}/>}</section>
          <section className="panel"><div className="panel-title"><div><h3>Revenue by category</h3><p>Category contribution</p></div><span className="chart-icon"><BarChart3 size={17}/></span></div>
            {loading?<div className="chart-loading">Loading analytics…</div>:<CategoryChart data={categories}/>}</section>
        </div>
        <div className="lower-grid">
          <section className="panel"><div className="panel-title"><div><h3>Orders by type</h3><p>Unique orders by service mode</p></div><span className="chart-icon"><Utensils size={17}/></span></div>
            {loading?<div className="chart-loading">Loading analytics…</div>:<OrderTypeChart data={types}/>}</section>
          <section className="panel outlet-panel"><div className="panel-title"><div><h3>Top outlets</h3><p>Ranked by total revenue</p></div><span className="chart-icon"><Store size={17}/></span></div>
            <div className="outlet-list">{outlets.map((o,i)=><div className="outlet-row" key={o.outlet_name}><span className="rank">{String(i+1).padStart(2,'0')}</span><div className="outlet-info"><b>{o.outlet_name}</b><div className="progress"><i style={{width:`${outlets[0]?.revenue?o.revenue/outlets[0].revenue*100:0}%`}}/></div></div><strong>{money(o.revenue)}</strong></div>)}
            {!outlets.length&&<div className="empty">No outlet data</div>}</div>
        </section>
        </div>
        <OrdersTable data={orders} page={page} setPage={setPage} search={search} setSearch={setSearch}/>
        <footer>Built with React · FastAPI · SQLite <span>Business Analytics Dashboard</span></footer>
      </div>
    </main>
  </div>
}
