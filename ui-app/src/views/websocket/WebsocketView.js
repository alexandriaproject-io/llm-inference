import React, { useState } from 'react'
import GenerationConfig from '../../components/GenerationConfig'
import WebsocketManager from '../../components/WebsocketManager'

const API_PATH = `${process.env.REACT_APP_BASE_URL || ''}/api/ws`.replace(/^http/i, 'ws')

const WebsocketView = () => {
  const [generationConfig, setGenerationConfig] = useState({})
  const [ws, setWs] = useState(null)
  const [wsStatus, setWsStatus] = useState('connecting')

  const onStatus = (status) => setWsStatus(status)
  const onClose = () => setWs(null)
  const onConnect = (socket, connetionId) => {
    setWs(socket)
    socket.send(connetionId)
  }

  const onMessage = (event) => {
    console.log('Message from server ', event.data)
  }
  return (
    <>
      <WebsocketManager
        wsUrl={API_PATH}
        onMessage={onMessage}
        onConnect={onConnect}
        onStatus={onStatus}
        onClose={onClose}
        onError={onClose}
      />
      <GenerationConfig
        config={generationConfig}
        onChange={(newConfig) => setGenerationConfig(newConfig)}
        showStream
      />
    </>
  )
}

export default WebsocketView
