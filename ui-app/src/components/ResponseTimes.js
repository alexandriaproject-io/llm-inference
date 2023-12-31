import React from 'react'
import { CBadge, CFormLabel } from '@coreui/react'

const ResponseTimes = ({ responseTimes }) => {
  return (
    <>
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
    </>
  )
}

export default ResponseTimes
