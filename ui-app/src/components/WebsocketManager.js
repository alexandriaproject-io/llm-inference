import React, { useEffect, useState } from 'react'
import { CButton, CCard, CCardHeader } from '@coreui/react'
import { v4 as uuidv4 } from 'uuid'

const getWsColor = (wsStatus) => {
  switch (wsStatus) {
    case 'connecting':
      return 'yellow'
    case 'connected':
      return 'green'
    case 'closed':
      return 'gray'
    case 'error':
      return 'red'
    default:
      return ''
  }
}

const wsCallbackHash = {}

const WebsocketManager = ({
  wsUrl,
  onConnecting = () => undefined,
  onConnect = () => undefined,
  onError = () => undefined,
  onClose = () => undefined,
  onMessage = () => undefined,
  onStatus = () => undefined,
}) => {
  const [connectionId, setConnectionId] = useState(uuidv4())
  const [ws, setWs] = useState(null)
  const [wsStatus, setWsStatus] = useState('connecting')

  // Required workarround so react won't lose the parent state on callbacks
  wsCallbackHash[connectionId] = {
    onConnecting,
    onConnect,
    onError,
    onClose,
    onMessage,
    onStatus,
  }

  const onWsMessage = (event) => {
    let data = event.data
    try {
      data = JSON.parse(event.data)
    } catch (e) {}
    wsCallbackHash[connectionId].onMessage(data, event)
  }

  const closeSocket = (ws) => {
    if (ws) {
      ws.removeEventListener('message', onWsMessage)
      ws.close()
      setWs(null)
    }
  }

  const setStatus = (status) => {
    setWsStatus(status)
    onStatus(status)
  }

  useEffect(() => {
    const socket = new WebSocket(wsUrl)
    setStatus('connecting')
    socket.status = 'connecting'
    setWs(socket)
    wsCallbackHash[connectionId].onConnecting(socket, connectionId)

    socket.addEventListener('open', function (event) {
      setStatus('connected')
      socket.status = 'connected'
      wsCallbackHash[connectionId].onConnect(socket, connectionId)
    })

    socket.addEventListener('close', function (event) {
      socket.status !== 'connecting' && socket.status !== 'closing' && setStatus('closed')
      socket.status = 'closed'
      wsCallbackHash[connectionId].onClose(socket, connectionId)
    })

    socket.addEventListener('error', function (event) {
      socket.status = 'error'
      setStatus('error')
      wsCallbackHash[connectionId].onError(socket, connectionId)
    })

    socket.addEventListener('message', onWsMessage)
    return () => {
      delete wsCallbackHash[connectionId]
      closeSocket(ws)
    }
  }, [connectionId])

  return (
    <CCard className="mb-3 ">
      <CCardHeader style={{ lineHeight: '2rem' }}>
        Websocket Status :&nbsp;
        <strong
          style={{
            color: getWsColor(wsStatus),
          }}
        >
          {wsStatus}
        </strong>
        {wsStatus === 'connected' && (
          <CButton
            size="sm"
            color="danger"
            className="float-end ms-3"
            onClick={() => closeSocket(ws)}
          >
            Close
          </CButton>
        )}
        {(wsStatus === 'error' || wsStatus === 'connected') && (
          <CButton
            size="sm"
            color="secondary"
            className="float-end ms-3"
            onClick={() => {
              ws.status = 'closing'
              setConnectionId(uuidv4())
            }}
          >
            Reconnect
          </CButton>
        )}
        {(wsStatus === 'closed' || wsStatus === 'connecting') && (
          <CButton
            size="sm"
            disabled={wsStatus === 'connecting'}
            color="success"
            className="float-end ms-3"
            onClick={() => setConnectionId(uuidv4())}
          >
            {wsStatus === 'closed' ? 'Connect' : 'Connecting...'}
          </CButton>
        )}
      </CCardHeader>
    </CCard>
  )
}

export default WebsocketManager
