import React, { useEffect, useState } from 'react'
import {
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CFormCheck,
  CFormInput,
  CInputGroup,
  CInputGroupText,
  CRow,
} from '@coreui/react'

export const defaultGenerationConfig = (overrides = {}) => {
  return {
    llmConfig: {
      num_beams: 1,
      do_sample: true,
      temperature: 1,
      top_p: 1,
      top_k: 50,
      max_new_tokens: 100,
      repetition_penalty: 1,
      length_penalty: 1,
      ...(overrides.llmConfig || {}),
    },
    requestConfig: {
      onlyNewTokens: true,
      streamResponse: true,
      ...(overrides.requestConfig || {}),
    },
  }
}

const GenerationConfig = ({
  onChange = () => undefined,
  showStream = false,
  defaultConfig = {},
  config = {},
}) => {
  const [stateConfig, setStateConfig] = useState(defaultGenerationConfig(defaultConfig))

  useEffect(() => {
    setGenerationConfig({})
  }, [])

  const getLlmConfig = () => ({
    ...stateConfig.llmConfig,
    ...(config?.llmConfig || {}),
  })
  const getRequestConfig = () => ({
    ...stateConfig.requestConfig,
    ...(config?.requestConfig || {}),
  })

  const setGenerationConfig = (newConfig) => {
    const updatedConfig = {
      llmConfig: {
        ...stateConfig.llmConfig,
        ...newConfig.llmConfig,
      },
      requestConfig: {
        ...stateConfig.requestConfig,
        ...newConfig.requestConfig,
      },
    }
    setStateConfig(updatedConfig)
    onChange(updatedConfig)
  }

  const setLlmConfig = (llmConfig) => {
    setGenerationConfig({ llmConfig })
  }

  const setRequestConfig = (requestConfig) => {
    setGenerationConfig({ requestConfig })
  }

  return (
    <CCard className="mb-3 ">
      <CCardHeader>
        Generation Config:
        <CButton
          color="secondary"
          size="sm"
          className="float-end"
          onClick={() => {
            const defaults = defaultGenerationConfig(defaultConfig)
            setStateConfig(defaults)
            onChange(defaults)
          }}
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
                value={getLlmConfig().temperature}
                onChange={(e) => {
                  const value = parseFloat(e.target.value) || 0
                  setLlmConfig({ temperature: value < 0 ? 0 : value })
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
                value={getLlmConfig().max_new_tokens}
                onChange={(e) => {
                  const value = parseInt(e.target.value) || 0
                  setLlmConfig({ max_new_tokens: value < 1 ? 1 : value })
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
                value={getLlmConfig().num_beams}
                onChange={(e) => {
                  const value = parseInt(e.target.value) || 0
                  setLlmConfig({ num_beams: value < 1 ? 1 : value })
                }}
              />
            </CInputGroup>
          </CCol>
          <CCol cm={6}>
            <CInputGroup className="mb-3">
              <CFormCheck
                style={{ cursor: 'pointer' }}
                checked={getLlmConfig().do_sample}
                onChange={(e) => setLlmConfig({ do_sample: !!e.target.checked })}
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
                value={getLlmConfig().top_p}
                onChange={(e) => {
                  const value = parseFloat(e.target.value) || 0
                  setLlmConfig({ top_p: value < 0 ? 0 : value })
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
                value={getLlmConfig().top_k}
                onChange={(e) => {
                  const value = parseInt(e.target.value) || 0
                  setLlmConfig({ top_k: value < 0 ? 0 : value })
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
                value={getLlmConfig().repetition_penalty}
                onChange={(e) => {
                  const value = parseFloat(e.target.value) || 0
                  setLlmConfig({ repetition_penalty: value < 0.000001 ? 0.000001 : value })
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
                value={getLlmConfig().length_penalty}
                onChange={(e) => {
                  const value = parseFloat(e.target.value) || 0
                  setLlmConfig({ length_penalty: value < 0 ? 0 : value })
                }}
              />
            </CInputGroup>
          </CCol>
        </CRow>
        <CRow>
          <CCol cm={6}>
            <CFormCheck
              style={{ cursor: 'pointer' }}
              checked={getRequestConfig().onlyNewTokens}
              onChange={(e) => setRequestConfig({ onlyNewTokens: e.target.checked })}
              className="mt-2"
              type="checkbox"
              id="onlyNewTokensCheck"
              label={
                <span style={{ cursor: 'pointer' }}>
                  Only return new tokens ( or include prompt )
                </span>
              }
            />
          </CCol>
          <CCol cm={6}>
            {showStream && (
              <CFormCheck
                style={{ cursor: 'pointer' }}
                checked={getRequestConfig().streamResponse}
                onChange={(e) => setRequestConfig({ streamResponse: e.target.checked })}
                className="mt-2"
                type="checkbox"
                id="isStreamResponse"
                label={
                  <span style={{ cursor: 'pointer' }}>
                    Stream tokens as they are being generated ( or all at once )
                  </span>
                }
              />
            )}
          </CCol>
        </CRow>

        <div className="invalid-feedback d-block">
          {getLlmConfig().num_beams !== 1 && 'Multiple beams do not support streaming!'}
        </div>
      </CCardBody>
    </CCard>
  )
}

export default GenerationConfig
