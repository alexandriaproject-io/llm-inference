import React, { useEffect, useState } from 'react'
import {
  CBadge,
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CForm,
  CFormCheck,
  CFormFeedback,
  CFormInput,
  CFormLabel,
  CFormTextarea,
  CInputGroup,
  CInputGroupText,
  CRow,
} from '@coreui/react'
import Timer from '../../components/Timer'
import { v4 as uuidv4 } from 'uuid'
import ReactMarkdown from 'react-markdown'
import SyntaxHighlighter from 'react-syntax-highlighter'
import docco from 'react-syntax-highlighter/dist/esm/styles/hljs/docco'
import atomDark from 'react-syntax-highlighter/dist/esm/styles/hljs/atom-one-dark'
import { useSelector } from 'react-redux'

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

const defaultGenerationConfig = () => {
  return {
    num_beams: 1,
    do_sample: false,
    temperature: 1,
    top_p: 1,
    top_k: 50,
    max_new_tokens: 100,
    repetition_penalty: 1,
    length_penalty: 1,
  }
}

let scrollLock = false
let lastScrollY = window.scrollY
window.addEventListener('scroll', (e) => {
  if (scrollLock) {
    if (window.scrollY < lastScrollY) {
      scrollLock = false
    }
  } else {
    scrollLock = document.body.offsetHeight - (window.innerHeight + window.scrollY) < 50
  }
  lastScrollY = window.scrollY
})

const scroller = () => {
  if (scrollLock && window.scrollY < document.body.scrollHeight) {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: 'auto',
    })
  }
  let timer = document.body.scrollHeight - window.scrollY
  timer = timer < 100 ? 100 : timer > 250 ? 250 : timer
  window.setTimeout(scroller, !scrollLock ? 100 : timer)
}
window.setTimeout(scroller, 0)

const Dashboard = () => {
  const [requestId, setRequestId] = useState(uuidv4())
  const [prompt, setPrompt] = useState(
    '[INST] Generate a very long poem about 1000 cats [/INST]\n\n',
  )
  const [isStop, setIsStop] = useState(false)
  const [autoContinue, setAutoContinue] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const [isOnlyNewTokens, setIsOnlyNewTokens] = useState(true)
  const [response, setResponse] = useState(``)
  const [responseController, setResponseController] = useState(null)
  const [lastResponseTime, setLastResponseTime] = useState(0)
  const [responseTimes, setResponseTimes] = useState([])
  const [isError, setIsError] = useState(0)
  const [errorText, setErrorText] = useState('')
  const [isWaiting, setIsWaiting] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [rawResponse, setRawResponse] = useState(false)
  const [isContinuePrompt, setIsContinuePrompt] = useState(false)
  const [generationConfig, setGenerationConfig] = useState(defaultGenerationConfig())
  const theme = useSelector(({ theme }) => {
    return theme === 'auto'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      : theme
  })

  const components = {
    // Custom component for text
    code: ({ node, ...props }) => {
      return (
        <span>
          <SyntaxHighlighter language={props.language} style={theme === 'dark' ? atomDark : docco}>
            {props.children}
          </SyntaxHighlighter>
        </span>
      )
    },
  }

  useEffect(() => {
    if (autoContinue && isContinuePrompt && !isStreaming && !isWaiting && !isStop && !isError) {
      sendPrompt() // need to allow the states to update before continuing
    } else {
      setIsStop(false)
    }
  }, [lastResponseTime])
  const sendPrompt = async (scrollToText) => {
    scrollLock = scrollToText ?? scrollLock
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
      fullResponse = isOnlyNewTokens ? response : ''
    }
    let lastStreamChunk = ''
    try {
      const { responseTime, response } = await readHttpStream(
        API_PATH,
        {
          request_id: requestId,
          prompt: prompt,
          only_new_tokens: isOnlyNewTokens,
          generation_config: generationConfig,
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
        scrollLock = false
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
        scrollLock = false
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
        <CCard className="mb-3 ">
          <CCardHeader>
            Generation Config:
            <CButton
              color="secondary"
              size="sm"
              className="float-end"
              onClick={() => setGenerationConfig(defaultGenerationConfig())}
            >
              reset defaults
            </CButton>
          </CCardHeader>
          <CCardBody>
            <small>
              <br />
            </small>
            <CRow>
              <CCol cm={6}>
                <CInputGroup className="mb-3">
                  <CInputGroupText style={{ width: 205 }}>
                    Temperature - <strong>&nbsp;Float</strong>
                  </CInputGroupText>
                  <CFormInput
                    placeholder="temperature"
                    type="number"
                    value={generationConfig.temperature}
                    onChange={(e) => {
                      const value = parseFloat(e.target.value) || 0
                      setGenerationConfig({
                        ...generationConfig,
                        temperature: value < 0 ? 0 : value,
                      })
                    }}
                  />
                </CInputGroup>
              </CCol>
              <CCol cm={6}>
                <CInputGroup className="mb-3">
                  <CInputGroupText style={{ width: 205 }}>
                    Max new Tokens - <strong>&nbsp;Int</strong>
                  </CInputGroupText>
                  <CFormInput
                    placeholder="max_new_tokens"
                    type="number"
                    value={generationConfig.max_new_tokens}
                    onChange={(e) => {
                      const value = parseInt(e.target.value) || 0
                      setGenerationConfig({
                        ...generationConfig,
                        max_new_tokens: value < 1 ? 1 : value,
                      })
                    }}
                  />
                </CInputGroup>
              </CCol>
            </CRow>
            <CRow>
              <CCol cm={6}>
                <CInputGroup className="mb-3">
                  <CInputGroupText style={{ width: 205 }}>
                    Number of Beams - <strong>&nbsp;Int</strong>
                  </CInputGroupText>
                  <CFormInput
                    placeholder="num_beams"
                    type="number"
                    value={generationConfig.num_beams}
                    onChange={(e) => {
                      const value = parseInt(e.target.value) || 0
                      setGenerationConfig({
                        ...generationConfig,
                        num_beams: value < 1 ? 1 : value,
                      })
                    }}
                  />
                </CInputGroup>
              </CCol>
              <CCol cm={6}>
                <CInputGroup className="mb-3">
                  <CFormCheck
                    style={{ cursor: 'pointer' }}
                    checked={generationConfig.do_sample}
                    onChange={(e) =>
                      setGenerationConfig({
                        ...generationConfig,
                        do_sample: !!e.target.checked,
                      })
                    }
                    className="mt-2"
                    type="checkbox"
                    id="doSample"
                    label={<span style={{ cursor: 'pointer' }}>Do sample ( Bool )</span>}
                  />
                </CInputGroup>
              </CCol>
            </CRow>
            <CRow>
              <CCol cm={6}>
                <CInputGroup className="mb-3">
                  <CInputGroupText style={{ width: 205 }}>
                    Top 'P' - <strong>&nbsp;Float</strong>
                  </CInputGroupText>
                  <CFormInput
                    placeholder="top_p"
                    type="number"
                    value={generationConfig.top_p}
                    onChange={(e) => {
                      const value = parseFloat(e.target.value) || 0
                      setGenerationConfig({
                        ...generationConfig,
                        top_p: value < 0 ? 0 : value,
                      })
                    }}
                  />
                </CInputGroup>
              </CCol>
              <CCol cm={6}>
                <CInputGroup className="mb-3">
                  <CInputGroupText style={{ width: 205 }}>
                    Top 'K' - <strong>&nbsp;Int</strong>
                  </CInputGroupText>
                  <CFormInput
                    placeholder="top_k"
                    type="number"
                    value={generationConfig.top_k}
                    onChange={(e) => {
                      const value = parseInt(e.target.value) || 0
                      setGenerationConfig({
                        ...generationConfig,
                        top_k: value < 0 ? 0 : value,
                      })
                    }}
                  />
                </CInputGroup>
              </CCol>
            </CRow>
            <CRow>
              <CCol cm={6}>
                <CInputGroup className="mb-3">
                  <CInputGroupText style={{ width: 205 }}>
                    Repetition penalty - <strong>&nbsp;Float</strong>
                  </CInputGroupText>
                  <CFormInput
                    placeholder="repetition_penalty"
                    type="number"
                    value={generationConfig.repetition_penalty}
                    onChange={(e) => {
                      const value = parseFloat(e.target.value) || 0
                      setGenerationConfig({
                        ...generationConfig,
                        repetition_penalty: value < 0.000001 ? 0.000001 : value,
                      })
                    }}
                  />
                </CInputGroup>
              </CCol>
              <CCol cm={6}>
                <CInputGroup className="mb-3">
                  <CInputGroupText style={{ width: 205 }}>
                    Length penalty - <strong>&nbsp;Float</strong>
                  </CInputGroupText>
                  <CFormInput
                    placeholder="length_penalty"
                    type="number"
                    value={generationConfig.length_penalty}
                    onChange={(e) => {
                      const value = parseFloat(e.target.value) || 0
                      setGenerationConfig({
                        ...generationConfig,
                        length_penalty: value < 0 ? 0 : value,
                      })
                    }}
                  />
                </CInputGroup>
              </CCol>
            </CRow>
            <div className="invalid-feedback d-block">
              {generationConfig.num_beams !== 1 && 'Multiple beams do not support streaming!'}
            </div>
          </CCardBody>
        </CCard>

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
                  {time / 1000} s
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
            {isStop
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
            disabled={(!isWaiting && !isStreaming) || isStop}
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
        <CFormCheck
          style={{ cursor: 'pointer' }}
          checked={isOnlyNewTokens}
          disabled={isWaiting || isStreaming}
          onChange={(e) => setIsOnlyNewTokens(e.target.checked)}
          className="mt-2"
          type="checkbox"
          id="onlyNewTokensCheck"
          label={
            <span style={{ cursor: 'pointer' }}>
              Only return new tokens, if disabled returns response including prompt
            </span>
          }
        />
      </CForm>

      {response && (
        <CCard className="mb-5 ">
          <CCardHeader>
            Response to requestID {requestId}:
            <CButton
              color={rawResponse ? 'info' : 'light'}
              className="float-end"
              onClick={() => setRawResponse(!rawResponse)}
            >
              {rawResponse ? 'View markdown' : 'View raw response'}
            </CButton>
          </CCardHeader>
          <CCardBody>
            {rawResponse ? (
              <span className="markdown-llm">{response}</span>
            ) : (
              <ReactMarkdown components={components} skipHtml className="markdown-llm">
                {response.replace(/ /g, '\u00a0')}
              </ReactMarkdown>
            )}
          </CCardBody>
        </CCard>
      )}
    </>
  )
}

export default Dashboard
