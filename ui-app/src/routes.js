import React from 'react'

const Dashboard = React.lazy(() => import('./views/dashboard/Dashboard'))
const RestApiDashboard = React.lazy(() => import('./views/rest-api-single/RestApiDashboard'))

const routes = [
  { path: '/ui/', exact: true, name: 'Home' },
  { path: '/ui/rest-api-single', name: 'Dashboard', element: RestApiDashboard },
  { path: '/ui/websocket', name: 'Dashboard', element: Dashboard },
]

export default routes
