import { Link, useLocation } from 'react-router-dom'

interface LayoutProps {
  children: React.ReactNode
}

const IconDatabase = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 5.625c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
  </svg>
)

const IconFilter = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
  </svg>
)

const IconChart = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
  </svg>
)

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const isIngestionActive = () =>
    location.pathname === '/sources' ||
    location.pathname === '/runs' ||
    location.pathname.startsWith('/runs/') ||
    location.pathname === '/explorer' ||
    location.pathname.startsWith('/data/')

  const isPreprocessingActive = () =>
    location.pathname === '/preprocessing' || location.pathname.startsWith('/preprocessing/')

  const isAnalysisActive = () =>
    location.pathname === '/analysis' || location.pathname.startsWith('/analysis/')

  const navItem = (
    to: string,
    label: string,
    isActive: boolean,
    Icon: React.FC
  ) => (
    <Link
      to={to}
      className={`flex items-center gap-3 px-3 py-2.5 mx-2 rounded-lg text-sm font-medium transition-all duration-150 ${
        isActive
          ? 'bg-white/10 text-white'
          : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
      }`}
    >
      <Icon />
      {label}
    </Link>
  )

  const subTabs = [
    { to: '/sources', label: 'Sources', match: location.pathname === '/sources' },
    {
      to: '/runs',
      label: 'Runs',
      match: location.pathname === '/runs' || location.pathname.startsWith('/runs/'),
    },
    {
      to: '/data/raw_shopify',
      label: 'Data Preview',
      match: location.pathname.startsWith('/data/'),
    },
    { to: '/explorer', label: 'DB Explorer', match: location.pathname === '/explorer' },
  ]

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <div className="w-56 flex-shrink-0 bg-slate-900 flex flex-col">
        <div className="px-4 py-5 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-indigo-500 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.25}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-semibold text-white leading-tight">KPI Pipeline</div>
              <div className="text-[10px] text-slate-500 leading-tight tracking-wide">Data Platform</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 pt-4 space-y-0.5">
          <div className="px-5 mb-2">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-600">Pipeline</span>
          </div>
          {navItem('/sources', 'Data Ingestion', isIngestionActive(), IconDatabase)}
          {navItem('/preprocessing', 'Preprocessing', isPreprocessingActive(), IconFilter)}
          {navItem('/analysis', 'Analysis', isAnalysisActive(), IconChart)}
        </nav>

        <div className="px-5 py-4 border-t border-slate-800">
          <div className="text-[10px] text-slate-600 tracking-wide">quantmatrix.ai</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {isIngestionActive() && (
          <div className="bg-white border-b border-slate-200 px-6">
            <nav className="flex">
              {subTabs.map(({ to, label, match }) => (
                <Link
                  key={to}
                  to={to}
                  className={`py-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                    match
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
                  }`}
                >
                  {label}
                </Link>
              ))}
            </nav>
          </div>
        )}

        <main className="flex-1 overflow-auto bg-slate-50">
          {children}
        </main>
      </div>
    </div>
  )
}
