import React, { useEffect, useState } from 'react'
import GenerationConfig from '../../components/GenerationConfig'
import WebsocketManager from '../../components/WebsocketManager'
import { v4 as uuidv4 } from 'uuid'
import {
  CBadge,
  CButton,
  CCard,
  CCol,
  CFormCheck,
  CFormInput,
  CFormLabel,
  CFormTextarea,
  CInputGroup,
  CInputGroupText,
  CRow,
} from '@coreui/react'
import PromptResponse from '../../components/PromptResponse'
import Timer from '../../components/Timer'

const hostname = window.location.href.split('/')[0] + '//' + window.location.host
const API_PATH = `${process.env.REACT_APP_BASE_URL || hostname}/api/ws`.replace(/^http/i, 'ws')

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
  const [isStreaming, setIsStreaming] = useState(false)
  const [isQueued, setIsQueued] = useState(false)

  const [isContinuePrompt, setIsContinuePrompt] = useState(false)
  const [responseTimes, setResponseTimes] = useState([])
  const [lastResponseTime, setLastResponseTime] = useState(0)
  const [nonce, setNonce] = useState(0)
  const [executionStart, setExecutionStart] = useState(0)
  const [autoScroll, setAutoScroll] = useState(true)

  const [isError, setIsError] = useState(0)
  const [errorText, setErrorText] = useState('')

  useEffect(() => {
    if (autoContinue && isContinuePrompt && !isWaiting && !isStop && !isError) {
      sendPrompt() // need to allow the states to update before continuing
    } else {
      setIsStop(false)
    }
  }, [nonce])

  const onStatus = (status) => setWsStatus(status)
  const onClose = () => {
    setWs(null)
    abortRequest()
  }
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
    setPrompts(prompts.map((prompt) => ({ ...prompt, request_id: uuidv4(), response: '' })))
    setResponseTimes([])
    setIsError(0)
    setErrorText('')
    setIsWaiting(false)
    setIsQueued(false)
    setIsContinuePrompt(false)
  }

  const abortRequest = () => {
    setIsStop(true)
    setIsQueued(false)
    setIsWaiting(false)
    setIsStreaming(false)
  }

  const sendPrompt = (scrollToText) => {
    if (!ws) {
      return
    }
    setIsWaiting(true)
    if (!isContinuePrompt) {
      setResponseTimes([])
      setPrompts([
        ...prompts.map((prompt) => {
          prompt.response = ''
          return prompt
        }),
      ])
    }
    ws.send(
      JSON.stringify({
        prompts: prompts.map(({ prompt, request_id }) => ({ request_id, prompt })),
        generation_config: generationConfig?.llmConfig,
        only_new_tokens: !!generationConfig?.requestConfig?.onlyNewTokens,
        stream_response: !!generationConfig?.requestConfig?.streamResponse,
      }),
    )
    if (isContinuePrompt) {
      window.scrollLock = scrollToText ?? window.scrollLock
    } else {
      window.setTimeout(() => (window.scrollLock = scrollToText ?? window.scrollLock), 250)
    }
  }

  const onMessage = (data) => {
    if (!data.length) {
      console.log('Got empty events array, this is normal...')
      return
    }
    const type = data[0].type
    const eventsHash = data.reduce((res, item) => {
      res[item.request_id] = item
      return res
    }, {})

    switch (type) {
      case 'ACCEPTED':
        setIsQueued(true)
        break
      case 'STARTED':
        setExecutionStart(new Date().getTime())
        setIsQueued(false)
        break
      case 'INITIALIZED':
        if (isWaiting) {
          setIsWaiting(false)
          setIsStreaming(true)
        }
        if (!generationConfig?.requestConfig?.onlyNewTokens) {
          setPrompts([
            ...prompts.map((prompt) => {
              prompt.response = eventsHash[prompt.request_id]?.text || ''
              return prompt
            }),
          ])
        }
        break
      case 'PROGRESS':
        if (isWaiting) {
          setIsWaiting(false)
          setIsStreaming(true)
        }
        setPrompts([
          ...prompts.map((prompt) => {
            prompt.response += eventsHash[prompt.request_id]?.text || ''
            return prompt
          }),
        ])
        break
      case 'COMPLETE':
        setIsWaiting(false)
        setIsStreaming(false)
        if (!isStreaming) {
          setPrompts([
            ...prompts.map((prompt) => {
              if (generationConfig?.requestConfig?.onlyNewTokens) {
                prompt.response += eventsHash[prompt.request_id]?.text || ''
              } else {
                prompt.response = eventsHash[prompt.request_id]?.text || ''
              }
              return prompt
            }),
          ])
        }
        const isAllEos = data.every(({ is_eos }) => is_eos)
        setIsContinuePrompt(!isAllEos)
        const lastResponseTime = new Date().getTime() - executionStart
        setLastResponseTime(lastResponseTime)
        setResponseTimes([...responseTimes, lastResponseTime])
        setNonce(nonce + 1)
        break
      case 'ERROR':
        setIsWaiting(false)
        setIsStreaming(false)
        setIsQueued(false)
        setIsError(true)
        setErrorText(data[0].error)
        break
      default:
        console.warn(`Type ${type} is not handled!`)
    }
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
                  disabled={isWaiting || isStreaming || isContinuePrompt}
                  placeholder="request_id"
                  type="text"
                  value={request_id}
                  onChange={(e) => updatePrompt(id, { request_id: e.target.value })}
                />
                {index > 0 && (
                  <CButton
                    color="danger"
                    disabled={isContinuePrompt}
                    onClick={() => removePrompt(id)}
                  >
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
      {!!isError && (
        <div className="invalid-feedback d-block mt-2">
          {isError && (errorText || 'Error generating a response, check your console')}
        </div>
      )}
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

      <div>
        <CButton
          color="primary"
          disabled={isWaiting || isStreaming || isContinuePrompt}
          onClick={() => addPrompt()}
        >
          {' '}
          +{' '}
        </CButton>
        <CButton
          className="ms-3"
          color="primary"
          disabled={
            wsStatus !== 'connected' ||
            isWaiting ||
            isStreaming ||
            !prompts.every(({ prompt }) => !!prompt)
          }
          onClick={() => sendPrompt(autoScroll && prompts.length < 3)}
        >
          {isStop && (isWaiting || isStreaming || isQueued)
            ? 'Stopping...'
            : isQueued
              ? 'In Queue...'
              : isWaiting
                ? 'Waiting...'
                : isStreaming
                  ? 'Streaming...'
                  : isContinuePrompt
                    ? 'Continue'
                    : 'Send Prompt'}
        </CButton>
        {isContinuePrompt && !isWaiting && !isStreaming && ' or '}
        {isContinuePrompt && !isWaiting && !isStreaming && (
          <CButton color="secondary" disabled={isWaiting || isStreaming} onClick={resetPrompt}>
            reset
          </CButton>
        )}
        {isWaiting || isStreaming ? (
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
        <CButton
          color="secondary"
          className="float-end"
          disabled={!isWaiting && !isStreaming}
          onClick={abortRequest}
        >
          Abort
        </CButton>
        &nbsp;&nbsp;
      </div>
      {wsStatus !== 'connected' && (
        <div className="valid-feedback d-block mt-1 mb-3">Websocket is not connected</div>
      )}

      <CFormCheck
        style={{ cursor: 'pointer' }}
        checked={autoScroll && prompts.length < 3}
        disabled={prompts.length > 2}
        onChange={(e) => setAutoScroll(e.target.checked)}
        className="mt-2"
        type="checkbox"
        id="setAutoScroll"
        label={
          <span style={{ cursor: 'pointer' }}>Auto scroll to follow the generated response</span>
        }
      />
      <CFormCheck
        style={{ cursor: 'pointer' }}
        checked={autoContinue}
        disabled={isWaiting || isStreaming}
        onChange={(e) => setAutoContinue(e.target.checked)}
        className="mt-2"
        type="checkbox"
        id="autoContinueCheck"
        label={
          <span style={{ cursor: 'pointer' }}>
            Automatically continue prompt generation when didnt reach EOS
          </span>
        }
      />

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
