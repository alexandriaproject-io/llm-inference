import React, { useEffect, useState } from 'react'
import {
  CBadge,
  CButton,
  CForm,
  CFormCheck,
  CFormFeedback,
  CFormLabel,
  CFormTextarea,
} from '@coreui/react'
import Timer from '../../components/Timer'
import { v4 as uuidv4 } from 'uuid'
import GenerationConfig from '../../components/GenerationConfig'
import PromptResponse from '../../components/PromptResponse'

const API_PATH = `${process.env.REACT_APP_BASE_URL || ''}/api/generate-one`

async function readHttpStream(
  url,
  postData,
  onChunk = () => undefined,
  onController = () => undefined,
) {
  const start = new Date().getTime()
  const controller = new AbortController()
  const signal = controller.signal
  const response = await fetch(url, {
    method: 'POST',
    body: JSON.stringify(postData), // Convert the JavaScript object to a JSON string
    signal,
  })
  onController(controller)
  const reader = response.body.getReader()
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    onChunk(new TextDecoder().decode(value))
  }
  return {
    response,
    responseTime: new Date().getTime() - start,
  }
}

function replaceStringAtEnd(str, search, replace) {
  if (str.endsWith(search)) {
    return str.slice(0, -search.length) + replace
  }
  return str
}

const RestApiBatchDashboard = () => {
  const [requestId, setRequestId] = useState(uuidv4())
  const [prompt, setPrompt] = useState(
    '[INST] Generate a very long poem about 1000 cats [/INST]\n\n',
  )
  const [isStop, setIsStop] = useState(false)
  const [autoContinue, setAutoContinue] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const [response, setResponse] = useState(``)
  const [responseController, setResponseController] = useState(null)
  const [lastResponseTime, setLastResponseTime] = useState(0)
  const [responseTimes, setResponseTimes] = useState([])
  const [isError, setIsError] = useState(0)
  const [errorText, setErrorText] = useState('')
  const [isWaiting, setIsWaiting] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [isContinuePrompt, setIsContinuePrompt] = useState(false)
  const [generationConfig, setGenerationConfig] = useState({})

  useEffect(() => {
    if (autoContinue && isContinuePrompt && !isStreaming && !isWaiting && !isStop && !isError) {
      sendPrompt() // need to allow the states to update before continuing
    } else {
      setIsStop(false)
    }
  }, [lastResponseTime])
  const sendPrompt = async (scrollToText) => {
    if (isContinuePrompt) {
      window.scrollLock = scrollToText ?? window.scrollLock
    } else {
      setResponse('')
      window.setTimeout(() => (window.scrollLock = scrollToText ?? window.scrollLock), 250)
    }
    setIsWaiting(true)
    setIsStreaming(false)
    setIsStop(false)
    setErrorText('')
    setIsError(0)
    setLastResponseTime(0)

    let fullResponse = ''
    if (!isContinuePrompt) {
      setResponseTimes([])
    } else {
      fullResponse = generationConfig?.requestConfig?.onlyNewTokens ? response : ''
    }
    let lastStreamChunk = ''
    try {
      const { responseTime, response } = await readHttpStream(
        API_PATH,
        {
          request_id: requestId,
          prompt: prompt,
          only_new_tokens: !!generationConfig?.requestConfig?.onlyNewTokens,
          stream_response: !!generationConfig?.requestConfig?.streamResponse,
          generation_config: generationConfig.llmConfig,
        },
        (text) => {
          lastStreamChunk = text
          fullResponse += text
          setIsWaiting(false)
          setIsStreaming(true)
          setResponse(fullResponse)
        },
        (controller) => setResponseController(controller),
      )
      if (response.status !== 200) {
        setIsError(1)
        window.scrollLock = false
        autoScroll && window.scrollTo(0, 0)
        setResponse(replaceStringAtEnd(fullResponse, lastStreamChunk, ''))
        setErrorText(lastStreamChunk)
      } else {
        if (!isContinuePrompt) {
          setResponseTimes([responseTime])
        } else {
          setResponseTimes([...responseTimes, responseTime])
        }
      }

      setLastResponseTime(responseTime)
    } catch (e) {
      if (e.name === 'AbortError') {
        console.log('Aborting')
        setIsError(2)
      } else {
        console.error(e)
        setIsError(1)
        window.scrollLock = false
        autoScroll && window.scrollTo(0, 0)
        setResponse(replaceStringAtEnd(fullResponse, lastStreamChunk, ''))
        setErrorText(lastStreamChunk)
      }

      setResponseController(null)
      setIsWaiting(false)
      setIsStreaming(false)
      setIsStop(false)
    } finally {
      setResponseController(null)
      setIsWaiting(false)
      setIsStreaming(false)
      const isEos = fullResponse.trimEnd().endsWith('</s>')
      setIsContinuePrompt(!isEos)
      if (isEos) {
        setIsStop(false)
      }
    }
  }

  const abortRequest = () => {
    setIsStop(true)
    console.log(responseController)
    if (responseController) {
      responseController.abort()
    }
  }
  const resetPrompt = () => {
    setRequestId(uuidv4())
    setIsStop(false)
    setResponse('')
    setResponseController(null)
    setLastResponseTime(0)
    setResponseTimes([])
    setIsError(0)
    setErrorText('')
    setIsWaiting(false)
    setIsStreaming(false)
    setIsContinuePrompt(false)
  }

  return (
    <>
      <CForm className="pb-5">
        <GenerationConfig
          config={generationConfig}
          onChange={(newConfig) => setGenerationConfig(newConfig)}
          showStream
        />

        <div className="mb-3">
          <CFormLabel htmlFor="exampleFormControlTextarea1">
            <strong>Write your prompt </strong>- <small>RequestID: {requestId}</small>
          </CFormLabel>
          <CFormTextarea
            placeholder="[INST] Generate a very long poem about 1000 cats [/INST]\n\n"
            disabled={isWaiting || isStreaming || isContinuePrompt}
            value={prompt}
            invalid={!!isError}
            onChange={(e) => setPrompt(e.target.value)}
            id="exampleFormControlTextarea1"
            rows={10}
          ></CFormTextarea>
          <CFormFeedback invalid>
            {isError === 2
              ? 'Aborting might cause some data to be lost, its best to reset after aborting!'
              : errorText || 'Error generating a response, check your console'}
          </CFormFeedback>
        </div>

        {responseTimes.length ? (
          <CFormLabel htmlFor="exampleFormControlTextarea1">
            <strong>Response time history: </strong>
          </CFormLabel>
        ) : (
          ''
        )}
        <div className="pb-3" style={{ overflow: 'auto', whiteSpace: 'nowrap' }}>
          {responseTimes.length
            ? responseTimes.map((time, i) => (
                <CBadge
                  key={`badge-${i}-${time}`}
                  color="dark"
                  shape="rounded-pill"
                  className="me-2"
                >
                  {(time / 1000).toFixed(3)} s
                </CBadge>
              ))
            : ''}
        </div>

        <div className="mb-3 ">
          <CButton
            color="primary"
            disabled={isWaiting || isStreaming || !prompt}
            onClick={() => sendPrompt(autoScroll)}
          >
            {isStop && (isWaiting || isStreaming)
              ? 'Stopping...'
              : isWaiting
                ? 'Waiting...'
                : isStreaming
                  ? 'Streaming...'
                  : isContinuePrompt
                    ? 'Continue'
                    : 'Send Prompt'}
          </CButton>
          {isContinuePrompt && !isWaiting && !isStreaming && ' or '}
          {!isWaiting && !isStreaming && isContinuePrompt && (
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
        <CFormCheck
          style={{ cursor: 'pointer' }}
          checked={autoScroll}
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
      </CForm>

      {response && <PromptResponse requestId={requestId} response={response} />}
    </>
  )
}

export default RestApiBatchDashboard
