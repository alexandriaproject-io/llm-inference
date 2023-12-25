import React from 'react'

const Dashboard = React.lazy(() => import('./views/dashboard/Dashboard'))
const RestApiDashboard = React.lazy(() => import('./views/rest-api-single/RestApiDashboard'))
const RestApiBatchDashboard = React.lazy(
  () => import('./views/rest-api-batch/RestApiBatchDashboard'),
)

const routes = [
  { path: '/ui/', exact: true, name: 'Home' },
  { path: '/ui/rest-api-single', name: 'Dashboard', element: RestApiDashboard },
  { path: '/ui/rest-api-batch', name: 'Dashboard', element: RestApiBatchDashboard },
  { path: '/ui/websocket', name: 'Dashboard', element: Dashboard },
]

export default routes
