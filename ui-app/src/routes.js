import React from 'react'

const Dashboard = React.lazy(() => import('./views/dashboard/Dashboard'))
const RestApiDashboard = React.lazy(() => import('./views/rest-api-single/RestApiDashboard'))

const routes = [
  { path: '/', exact: true, name: 'Home' },
  { path: '/rest-api-single', name: 'Dashboard', element: RestApiDashboard },
  { path: '/websocket', name: 'Dashboard', element: Dashboard },
]

export default routes
