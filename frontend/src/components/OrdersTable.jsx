import { ChevronLeft, ChevronRight, Search } from 'lucide-react'
const money = n => `₹${Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
export default function OrdersTable({ data, page, setPage, search, setSearch }) {
  return <section className="panel table-panel">
    <div className="panel-title table-title"><div><h3>Order line items</h3><p>Explore individual items from the source dataset</p></div>
      <label className="search-box"><Search size={15}/><input placeholder="Search bill, item or outlet" value={search} onChange={e=>{setSearch(e.target.value);setPage(1)}}/></label>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Bill no.</th><th>Outlet</th><th>Date & time</th><th>Item</th><th>Category</th><th>Qty</th><th>Revenue</th><th>Order type</th><th>Payment</th></tr></thead>
      <tbody>{data.items?.map((r,i)=><tr key={`${r.bill_no}-${i}`}><td className="bill">#{r.bill_no}</td><td>{r.outlet_name}</td><td>{r.order_datetime}</td><td className="item-cell">{r.item}</td><td><span className="category-pill">{r.category}</span></td><td>{r.quantity}</td><td className="revenue-cell">{money(r.revenue)}</td><td>{r.order_type}</td><td>{r.settlement}</td></tr>)}
      {!data.items?.length && <tr><td colSpan="9" className="empty">No matching records found.</td></tr>}</tbody>
    </table></div>
    <div className="pagination"><span>{data.total ? `Showing ${(page-1)*25+1}–${Math.min(page*25,data.total)} of ${data.total.toLocaleString('en-IN')} records` : 'No records'}</span>
      <div><button disabled={page<=1} onClick={()=>setPage(p=>p-1)}><ChevronLeft size={16}/></button><b>{page} / {Math.max(data.total_pages || 1,1)}</b><button disabled={page>=(data.total_pages||1)} onClick={()=>setPage(p=>p+1)}><ChevronRight size={16}/></button></div>
    </div>
  </section>
}
