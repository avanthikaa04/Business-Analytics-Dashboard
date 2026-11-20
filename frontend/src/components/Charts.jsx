import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, PieChart, Pie, Cell, Legend } from 'recharts'
const COLORS = ['#6c63ff','#20b8a6','#f6a84a','#ec6b87','#4d9de0','#9b7ede']
const money = n => `₹${Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
const compact = n => Number(n || 0).toLocaleString('en-IN', { notation: 'compact', maximumFractionDigits: 1 })
export function RevenueChart({ data }) {
  return <div className="chart-wrap"><ResponsiveContainer width="100%" height={270}>
    <AreaChart data={data} margin={{top:10,right:12,left:0,bottom:0}}>
      <defs><linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#766cff" stopOpacity={.28}/><stop offset="95%" stopColor="#766cff" stopOpacity={0}/></linearGradient></defs>
      <CartesianGrid strokeDasharray="3 5" vertical={false} stroke="#273247"/>
      <XAxis dataKey="day" tickFormatter={v=>v.slice(5)} tick={{fill:'#8290a6',fontSize:11}} axisLine={false} tickLine={false}/>
      <YAxis tickFormatter={compact} tick={{fill:'#8290a6',fontSize:11}} axisLine={false} tickLine={false} width={48}/>
      <Tooltip contentStyle={{background:'#121c2d',border:'1px solid #2b3850',borderRadius:10,color:'#fff'}} formatter={v=>money(v)}/>
      <Area type="monotone" dataKey="revenue" stroke="#8a82ff" strokeWidth={2.5} fill="url(#revenueFill)" />
    </AreaChart>
  </ResponsiveContainer></div>
}
export function CategoryChart({ data }) {
  return <div className="chart-wrap"><ResponsiveContainer width="100%" height={270}>
    <BarChart data={data} layout="vertical" margin={{top:5,right:16,left:10,bottom:5}}>
      <CartesianGrid strokeDasharray="3 5" horizontal={false} stroke="#273247"/>
      <XAxis type="number" tickFormatter={compact} tick={{fill:'#8290a6',fontSize:11}} axisLine={false} tickLine={false}/>
      <YAxis type="category" dataKey="category" width={85} tick={{fill:'#b7c1d2',fontSize:11}} axisLine={false} tickLine={false}/>
      <Tooltip contentStyle={{background:'#121c2d',border:'1px solid #2b3850',borderRadius:10,color:'#fff'}} formatter={v=>money(v)}/>
      <Bar dataKey="revenue" fill="#6c63ff" radius={[0,6,6,0]} barSize={19}/>
    </BarChart>
  </ResponsiveContainer></div>
}
export function OrderTypeChart({ data }) {
  return <div className="chart-wrap pie-wrap"><ResponsiveContainer width="100%" height={270}>
    <PieChart><Pie data={data} dataKey="orders" nameKey="order_type" cx="50%" cy="48%" innerRadius={62} outerRadius={94} paddingAngle={4}>
      {data.map((entry,i)=><Cell key={entry.order_type} fill={COLORS[i%COLORS.length]}/>)}
    </Pie><Tooltip contentStyle={{background:'#121c2d',border:'1px solid #2b3850',borderRadius:10,color:'#fff'}}/>
      <Legend verticalAlign="bottom" iconType="circle" formatter={v=><span style={{color:'#aeb9ca',fontSize:12}}>{v}</span>}/>
    </PieChart>
  </ResponsiveContainer></div>
}
