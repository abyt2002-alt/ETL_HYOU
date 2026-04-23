import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Sources from './pages/Sources'
import Runs from './pages/Runs'
import RunDetail from './pages/RunDetail'
import DataPreview from './pages/DataPreview'
import Preprocessing from './pages/Preprocessing'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/sources" element={<Sources />} />
          <Route path="/runs" element={<Runs />} />
          <Route path="/runs/:runId" element={<RunDetail />} />
          <Route path="/data/:tableName" element={<DataPreview />} />
          <Route path="/preprocessing" element={<Preprocessing />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
