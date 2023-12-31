import React from 'react'

const RestApiDashboard = React.lazy(() => import('./views/rest-api-single/RestApiDashboard'))
const RestApiBatchDashboard = React.lazy(
  () => import('./views/rest-api-batch/RestApiBatchDashboard'),
)
const WebsocketDashboard = React.lazy(() => import('./views/websocket/WebsocketView'))

const routes = [
  { path: '/ui/', exact: true, name: 'Home' },
  { path: '/ui/rest-api-single', name: 'Dashboard', element: RestApiDashboard },
  { path: '/ui/rest-api-batch', name: 'Dashboard', element: RestApiBatchDashboard },
  { path: '/ui/websocket', name: 'Dashboard', element: WebsocketDashboard },
]

export default routes
