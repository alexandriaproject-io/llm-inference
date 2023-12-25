import React, { useEffect, useState } from 'react'
import {
  CBadge,
  CButton,
  CCard,
  CCol,
  CForm,
  CFormCheck,
  CFormInput,
  CFormLabel,
  CFormTextarea,
  CInputGroup,
  CInputGroupText,
  CRow,
} from '@coreui/react'
import Timer from '../../components/Timer'
import { v4 as uuidv4 } from 'uuid'
import GenerationConfig from '../../components/GenerationConfig'
import PromptResponse from '../../components/PromptResponse'

const API_PATH = `${process.env.REACT_APP_BASE_URL || ''}/api/generate-batch`

async function postHttp(url, postData, onController = () => undefined) {
  const start = new Date().getTime()
  const controller = new AbortController()
  const signal = controller.signal
  onController(controller)
  const response = await fetch(url, {
    method: 'POST',
    body: JSON.stringify(postData), // Convert the JavaScript object to a JSON string
    signal,
  })
  return {
    json:
      response.status === 200 || response.status === 206
        ? await response.json()
        : await response.text(),
    response,
    responseTime: new Date().getTime() - start,
  }
}

const RestApiBatchDashboard = () => {
  const [prompts, setPrompts] = useState([
    {
      prompt: '[INST] Generate a very long poem about 1000 cats [/INST]\n\n',
      requestId: uuidv4(),
      id: uuidv4(),
    },
    {
      prompt: '[INST] Generate a very short poem about 1000 dogs [/INST]\n\n',
      requestId: uuidv4(),
      id: uuidv4(),
    },
  ])
  const [isStop, setIsStop] = useState(false)
  const [autoContinue, setAutoContinue] = useState(false)
  const [responses, setResponses] = useState([])
  const [responseController, setResponseController] = useState(null)
  const [lastResponseTime, setLastResponseTime] = useState(0)
  const [responseTimes, setResponseTimes] = useState([])
  const [isError, setIsError] = useState(0)
  const [errorText, setErrorText] = useState('')
  const [isWaiting, setIsWaiting] = useState(false)
  const [isContinuePrompt, setIsContinuePrompt] = useState(false)
  const [generationConfig, setGenerationConfig] = useState({})

  useEffect(() => {
    if (autoContinue && isContinuePrompt && !isWaiting && !isStop && !isError) {
      sendPrompt() // need to allow the states to update before continuing
    } else {
      setIsStop(false)
    }
  }, [lastResponseTime])

  const sendPrompt = async () => {
    setIsWaiting(true)
    setIsStop(false)
    setErrorText('')
    setIsError(0)
    setLastResponseTime(0)

    let fullResponses = prompts.map(({ requestId }) => ({
      request_id: requestId,
      response: '',
    }))
    if (!isContinuePrompt) {
      setResponseTimes([])
      setResponses([])
    } else {
      if (generationConfig?.requestConfig?.onlyNewTokens) {
        fullResponses = [...responses]
      }
    }

    try {
      const { responseTime, response, json } = await postHttp(
        API_PATH,
        {
          prompts: prompts.map(({ requestId, prompt }) => ({ request_id: requestId, prompt })),
          only_new_tokens: !!generationConfig?.requestConfig?.onlyNewTokens,
          generation_config: generationConfig.llmConfig,
        },
        (controller) => {
          setResponseController(controller)
        },
      )
      if (response.status === 200 || response.status === 206) {
        setResponses(
          json.map((data, index) => {
            const full = fullResponses.find(({ request_id }) => request_id === data.request_id) || {
              response: '',
            }
            return {
              ...data,
              response: (full.response += data.response),
            }
          }),
        )
        if (!isContinuePrompt) {
          setResponseTimes([responseTime])
        } else {
          setResponseTimes([...responseTimes, responseTime])
        }
        setLastResponseTime(responseTime)
        const isEos = response.status === 200
        setIsContinuePrompt(!isEos)
        if (isEos) {
          setIsStop(false)
        }
      } else {
        setIsError(1)
        setErrorText(json)
      }
    } catch (e) {
      if (e.name === 'AbortError') {
        setIsError(2)
      } else {
        console.error(e)
        setIsError(1)
        setErrorText(e.message)
      }

      setResponseController(null)
      setIsWaiting(false)
      setIsStop(false)
    } finally {
      setResponseController(null)
      setIsWaiting(false)
    }
  }

  const abortRequest = () => {
    setIsStop(true)
    if (responseController) {
      responseController.abort()
    }
  }
  const resetPrompt = () => {
    setIsStop(false)
    setResponses([])
    setPrompts(prompts.map((prompt) => ({ ...prompt, requestId: uuidv4() })))
    setResponseController(null)
    setLastResponseTime(0)
    setResponseTimes([])
    setIsError(0)
    setErrorText('')
    setIsWaiting(false)
    setIsContinuePrompt(false)
  }
  const removePrompt = (index) => {
    prompts.splice(index, 1)
    setPrompts([...prompts])
  }
  const addPrompt = () => {
    setPrompts([
      ...prompts,
      {
        requestId: uuidv4(),
        prompt: '',
        id: uuidv4(),
      },
    ])
  }
  const updatePrompt = (index, prompt) => {
    prompts[index] = prompt
    setPrompts([...prompts])
  }
  return (
    <>
      <CForm className="pb-5">
        <GenerationConfig
          config={generationConfig}
          onChange={(newConfig) => setGenerationConfig(newConfig)}
          showStream
        />
        <CRow>
          {prompts.map(({ prompt, requestId, id }, index) => (
            <CCol sm={6} className="mt-4" key={`batch-prompt-${id}`}>
              <CCard>
                <CInputGroup>
                  <CInputGroupText>RequestId</CInputGroupText>
                  <CFormInput
                    disabled={isWaiting || isContinuePrompt}
                    placeholder="requestId"
                    type="text"
                    value={requestId}
                    onChange={(e) => updatePrompt(index, { prompt, requestId: e.target.value })}
                  />
                  {index > 1 && (
                    <CButton color="danger" onClick={() => removePrompt(index)}>
                      <strong>Clear</strong>
                    </CButton>
                  )}
                </CInputGroup>
                <CFormTextarea
                  placeholder="[INST] Generate a very long poem about 1000 cats [/INST]\n\n"
                  disabled={isWaiting || isContinuePrompt}
                  value={prompt}
                  invalid={!!isError}
                  onChange={(e) => updatePrompt(index, { requestId, prompt: e.target.value })}
                  id="exampleFormControlTextarea1"
                  rows={10}
                ></CFormTextarea>
              </CCard>
            </CCol>
          ))}
        </CRow>

        {!!isError && (
          <div className="invalid-feedback d-block mt-0">
            {isError === 2
              ? 'Aborting might cause some data to be lost, its best to reset after aborting!'
              : errorText || 'Error generating a response, check your console'}
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
            disabled={isWaiting || isContinuePrompt}
            onClick={() => addPrompt()}
          >
            {' '}
            +{' '}
          </CButton>
          <CButton
            className="ms-3"
            color="primary"
            disabled={isWaiting}
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
          <CButton
            color="secondary"
            className="float-end"
            disabled={!isWaiting}
            onClick={abortRequest}
          >
            Abort
          </CButton>
          &nbsp;&nbsp;
        </div>
        <CFormCheck
          style={{ cursor: 'pointer' }}
          checked={autoContinue}
          disabled={isWaiting}
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
      <CRow>
        {responses.map(({ request_id, response }) => (
          <CCol sm={6} className="mt-4" key={`batch-prompt-${request_id}`}>
            <PromptResponse key={request_id} requestId={request_id} response={response} />
          </CCol>
        ))}
      </CRow>
    </>
  )
}

export default RestApiBatchDashboard
