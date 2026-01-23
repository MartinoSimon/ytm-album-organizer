import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'


function App() {
  const [count, setCount] = useState(0)
  const [backendStatus, setBackendStatus] = useState<'idle'|'checking'|'ok'|'error'>('idle')
  const [backendResult, setBackendResult] = useState<unknown>(null)


  async function handleCheckBackend() {
    setBackendStatus('checking')
    setBackendResult(null)
    
    try {
      const res = await fetch('/api/health')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data = await res.json()
      setBackendResult(data)
      setBackendStatus('ok')
    } catch (err) {
      setBackendStatus('error')
      setBackendResult(String(err))
    }
  }

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
      <button onClick={handleCheckBackend} disabled={backendStatus === 'checking'}>
        Check Backend
      </button>
      <div>Status: {backendStatus}</div>
      <pre>{backendResult ? JSON.stringify(backendResult, null, 2) : ''}</pre>
    </>
  )
}

export default App
