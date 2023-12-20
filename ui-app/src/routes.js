import React from 'react'

const Dashboard = React.lazy(() => import('./views/dashboard/Dashboard'))

const routes = [
  { path: '/', exact: true, name: 'Home' },
  { path: '/rest-api', name: 'Dashboard', element: Dashboard },
  { path: '/websocket', name: 'Dashboard', element: Dashboard },
]

export default routes
