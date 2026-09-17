import { Link, Route, Routes } from 'react-router-dom'
import { AlertTriangle, FileSearch, ShieldCheck } from 'lucide-react'

function Home() {
  return <main className="shell">
    <header className="topbar"><div className="brand"><ShieldCheck size={28} /> <span>SafeNestT</span></div><Link className="button secondary" to="/report">Report a Scam</Link></header>
    <section className="hero"><div className="eyebrow">FRAUD PROTECTION & INVESTIGATION</div><h1>Turn a scam report into an organized case.</h1><p>SafeNestT helps you document what happened, preserve evidence, and understand the investigative steps available to you.</p><div className="actions"><Link className="button primary" to="/report">Start a Case</Link><Link className="button secondary" to="/cases">View My Cases</Link></div></section>
    <section className="cards"><article><AlertTriangle /><h2>Report fraud</h2><p>Capture the incident details and important transaction or contact information.</p></article><article><FileSearch /><h2>Preserve evidence</h2><p>Keep documents, messages, links, transaction details, and a clear case timeline together.</p></article><article><ShieldCheck /><h2>Investigate</h2><p>Use SafeNestT's investigation workflow to organize findings and next steps.</p></article></section>
  </main>
}

function Report() {
  return <main className="shell narrow"><header className="topbar"><Link className="brand" to="/"><ShieldCheck size={28} /> <span>SafeNestT</span></Link></header><section className="panel"><div className="eyebrow">NEW CASE</div><h1>Report a scam or fraud</h1><p>Start with the facts you know. You can add evidence and details after creating the case.</p><form className="form"><label>What happened?<textarea placeholder="Describe the scam or fraud..." rows={6} /></label><label>Type<select defaultValue=""><option value="" disabled>Select a case type</option><option>Online scam</option><option>Crypto fraud</option><option>Identity theft</option><option>Payment fraud</option><option>Investment fraud</option><option>Other</option></select></label><button className="button primary" type="button">Create Case</button></form></section></main>
}

function Cases() {
  return <main className="shell narrow"><header className="topbar"><Link className="brand" to="/"><ShieldCheck size={28} /> <span>SafeNestT</span></Link><Link className="button primary" to="/report">New Case</Link></header><section className="panel"><div className="eyebrow">YOUR CASES</div><h1>Case Center</h1><div className="empty"><FileSearch size={38} /><h2>No cases yet</h2><p>When you report a scam, your case and investigation timeline will appear here.</p><Link className="button primary" to="/report">Report a Scam</Link></div></section></main>
}

export default function App() { return <Routes><Route path="/" element={<Home />} /><Route path="/report" element={<Report />} /><Route path="/cases" element={<Cases />} /></Routes> }
