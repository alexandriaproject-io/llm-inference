import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { CButton, CCard, CCardBody, CCardHeader, CCol, CRow } from '@coreui/react'
import SyntaxHighlighter from 'react-syntax-highlighter'
import atomDark from 'react-syntax-highlighter/dist/cjs/styles/hljs/atom-one-dark'
import docco from 'react-syntax-highlighter/dist/cjs/styles/hljs/docco'
import { useSelector } from 'react-redux'

const PromptResponse = ({ requestId, response }) => {
  const [rawResponse, setRawResponse] = useState(false)
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
  return (
    <CCard className="mb-5 ">
      <CCardHeader>
        <CRow>
          <CCol sm={8}>
            <div>Response to requestID:</div>
            <small>{requestId}</small>
          </CCol>
          <CCol sm={4}>
            <CButton
              size="sm"
              color={rawResponse ? 'info' : 'light'}
              className="float-end mt-2"
              onClick={() => setRawResponse(!rawResponse)}
            >
              {rawResponse ? 'View markdown' : 'View raw response'}
            </CButton>
          </CCol>
        </CRow>
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
  )
}

export default PromptResponse
