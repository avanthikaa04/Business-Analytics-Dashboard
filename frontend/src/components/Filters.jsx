import { CalendarDays, RotateCcw } from 'lucide-react'
function Select({ label, value, options, onChange }) {
  return <label className="filter-field"><span>{label}</span><select value={value} onChange={e => onChange(e.target.value)}>
    <option value="">All {label}</option>{(options || []).map(v => <option key={v} value={v}>{v}</option>)}
  </select></label>
}
export default function Filters({ filters, values, setValues, onReset }) {
  const update = (key, value) => setValues(old => ({ ...old, [key]: value }))
  return <section className="filter-panel">
    <div className="filter-heading"><div><CalendarDays size={17}/><strong>Filters</strong><span>Refine your analytics</span></div>
      <button className="reset-button" onClick={onReset}><RotateCcw size={14}/> Reset</button></div>
    <div className="filter-grid">
      <label className="filter-field"><span>From date</span><input type="date" value={values.start_date} min={filters.min_date || ''} max={values.end_date || filters.max_date || ''} onChange={e => update('start_date', e.target.value)}/></label>
      <label className="filter-field"><span>To date</span><input type="date" value={values.end_date} min={values.start_date || filters.min_date || ''} max={filters.max_date || ''} onChange={e => update('end_date', e.target.value)}/></label>
      <Select label="Outlet" value={values.outlet} options={filters.outlets} onChange={v => update('outlet',v)}/>
      <Select label="Brand" value={values.brand} options={filters.brands} onChange={v => update('brand',v)}/>
      <Select label="Category" value={values.category} options={filters.categories} onChange={v => update('category',v)}/>
      <Select label="Order type" value={values.order_type} options={filters.order_types} onChange={v => update('order_type',v)}/>
      <Select label="Payment" value={values.settlement} options={filters.settlements} onChange={v => update('settlement',v)}/>
    </div>
  </section>
}
