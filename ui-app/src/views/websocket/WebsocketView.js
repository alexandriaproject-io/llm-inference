import React, { useEffect, useState } from 'react'
import GenerationConfig from '../../components/GenerationConfig'
import WebsocketManager from '../../components/WebsocketManager'
import { v4 as uuidv4 } from 'uuid'
import {
  CBadge,
  CButton,
  CCard,
  CCol,
  CFormInput,
  CFormLabel,
  CFormTextarea,
  CInputGroup,
  CInputGroupText,
  CRow,
} from '@coreui/react'
import PromptResponse from '../../components/PromptResponse'
import Timer from '../../components/Timer'

const API_PATH = `${process.env.REACT_APP_BASE_URL || ''}/api/ws`.replace(/^http/i, 'ws')

const WebsocketView = () => {
  const [generationConfig, setGenerationConfig] = useState({})
  const [ws, setWs] = useState(null)
  const [wsStatus, setWsStatus] = useState('connecting')

  const [prompts, setPrompts] = useState([
    {
      prompt: '[INST] Generate a very long poem about 1000 cats [/INST]\n\n',
      request_id: uuidv4(),
      response: '',
      id: uuidv4(),
    },
  ])

  const [isStop, setIsStop] = useState(false)
  const [autoContinue, setAutoContinue] = useState(false)
  const [isWaiting, setIsWaiting] = useState(false)
  const [isContinuePrompt, setIsContinuePrompt] = useState(false)
  const [isError, setIsError] = useState(0)
  const [errorText, setErrorText] = useState('')
  const [responseTimes, setResponseTimes] = useState([])
  const [lastResponseTime, setLastResponseTime] = useState(0)

  useEffect(() => {
    if (autoContinue && isContinuePrompt && !isWaiting && !isStop && !isError) {
      sendPrompt() // need to allow the states to update before continuing
    } else {
      setIsStop(false)
    }
  }, [lastResponseTime])

  const onStatus = (status) => setWsStatus(status)
  const onClose = () => setWs(null)
  const onConnect = (socket, connetionId) => {
    setWs(socket)
  }

  const removePrompt = (id) => {
    const index = prompts.findIndex((item) => item.id === id)
    prompts.splice(index, 1)
    setPrompts([...prompts])
  }
  const addPrompt = () => {
    setPrompts([
      ...prompts,
      {
        request_id: uuidv4(),
        prompt: '',
        id: uuidv4(),
      },
    ])
  }
  const updatePrompt = (id, prompt) => {
    const index = prompts.findIndex((item) => item.id === id)
    prompts[index] = {
      ...prompts[index],
      ...prompt,
    }
    setPrompts([...prompts])
  }

  const resetPrompt = () => {
    setIsStop(false)
    setPrompts(prompts.map((prompt) => ({ ...prompt, request_id: uuidv4() })))
    setResponseTimes([])
    setIsError(0)
    setErrorText('')
    setIsWaiting(false)
    setIsContinuePrompt(false)
  }
  const sendPrompt = () => {
    if (!ws) {
      return
    }
    ws.send(
      JSON.stringify({
        prompts: prompts.map(({ prompt, request_id }) => ({ request_id, prompt })),
        generation_config: generationConfig?.llmConfig,
        only_new_tokens: !!generationConfig?.requestConfig?.onlyNewTokens,
        stream_response: !!generationConfig?.requestConfig?.streamResponse,
      }),
    )
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

      <CRow>
        {prompts.map(({ prompt, request_id, id }, index) => (
          <CCol sm={prompts.length === 1 ? 12 : 6} className="mt-4" key={`batch-prompt-${id}`}>
            <CCard>
              <CInputGroup>
                <CInputGroupText>RequestId</CInputGroupText>
                <CFormInput
                  disabled={isWaiting || isContinuePrompt}
                  placeholder="request_id"
                  type="text"
                  value={request_id}
                  onChange={(e) => updatePrompt(id, { request_id: e.target.value })}
                />
                {index > 0 && (
                  <CButton color="danger" onClick={() => removePrompt(id)}>
                    <strong>Clear</strong>
                  </CButton>
                )}
              </CInputGroup>
              <CFormTextarea
                placeholder="[INST] Generate a very long poem about 1000 cats [/INST]\n\n"
                disabled={isWaiting || isContinuePrompt}
                value={prompt}
                invalid={!!isError || !prompt}
                onChange={(e) => updatePrompt(id, { prompt: e.target.value })}
                id="exampleFormControlTextarea1"
                rows={10}
              ></CFormTextarea>
            </CCard>
          </CCol>
        ))}
      </CRow>

      {responseTimes.length ? (
        <CFormLabel htmlFor="exampleFormControlTextarea1" className="mt-3">
          <strong>Response time history: </strong>
        </CFormLabel>
      ) : (
        ''
      )}
      <div className="pb-3" style={{ overflow: 'auto', whiteSpace: 'nowrap' }}>
        {responseTimes.length
          ? responseTimes.map((time, i) => (
              <CBadge key={`badge-${i}-${time}`} color="dark" shape="rounded-pill" className="me-2">
                {(time / 1000).toFixed(3)} s
              </CBadge>
            ))
          : ''}
      </div>

      <div className="mb-3 ">
        <CButton
          color="primary"
          disabled={isWaiting || isContinuePrompt}
          onClick={() => addPrompt()}
        >
          {' '}
          +{' '}
        </CButton>
        <CButton
          className="ms-3"
          color="primary"
          disabled={isWaiting || !prompts.every(({ prompt }) => !!prompt)}
          onClick={() => sendPrompt()}
        >
          {isStop && isWaiting
            ? 'Stopping...'
            : isWaiting
              ? 'Waiting...'
              : isContinuePrompt
                ? 'Continue'
                : 'Send Prompt'}
        </CButton>
        {isContinuePrompt && !isWaiting && ' or '}
        {!isWaiting && isContinuePrompt && (
          <CButton color="secondary" disabled={isWaiting} onClick={resetPrompt}>
            reset
          </CButton>
        )}
        {isWaiting ? (
          <CFormLabel>
            <strong>&nbsp;&nbsp;Segment time:&nbsp;</strong>
            <Timer /> seconds
          </CFormLabel>
        ) : lastResponseTime ? (
          <CFormLabel>
            <strong>&nbsp;&nbsp;Generation:&nbsp;</strong>
            {responseTimes.reduce((total, time) => total + time, 0) / 1000} seconds
          </CFormLabel>
        ) : (
          ''
        )}
        <CButton
          color="secondary"
          className="float-end ms-3"
          disabled={!autoContinue}
          onClick={() => setIsStop(true)}
        >
          Stop
        </CButton>
        &nbsp;&nbsp;
      </div>

      <CRow>
        {prompts.map(({ id, request_id, response }) => (
          <CCol sm={prompts.length === 1 ? 12 : 6} className="mt-4" key={`response-${id}`}>
            {response && <PromptResponse requestId={request_id} response={response || ''} />}
          </CCol>
        ))}
      </CRow>
    </>
  )
}

export default WebsocketView
