import React, { Suspense, useEffect } from 'react'
import { Route, Routes, BrowserRouter } from 'react-router-dom'
import { useSelector } from 'react-redux'

import { CSpinner, useColorModes } from '@coreui/react'
import './scss/style.scss'

window.scrollLock = false
let lastScrollY = window.scrollY
window.addEventListener('scroll', (e) => {
  if (window.scrollLock) {
    if (window.scrollY < lastScrollY) {
      window.scrollLock = false
    }
  } else {
    window.scrollLock = document.body.offsetHeight - (window.innerHeight + window.scrollY) < 50
  }
  lastScrollY = window.scrollY
})

const scroller = () => {
  if (window.scrollLock && window.scrollY < document.body.scrollHeight) {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: 'auto',
    })
  }
  let timer = document.body.scrollHeight - window.scrollY
  timer = timer < 50 ? 50 : timer > 250 ? 250 : timer
  window.setTimeout(scroller, !window.scrollLock ? 50 : timer)
}
window.setTimeout(scroller, 0)

// Containers
const DefaultLayout = React.lazy(() => import('./layout/DefaultLayout'))

const App = () => {
  const { isColorModeSet, setColorMode } = useColorModes('coreui-free-react-admin-template-theme')
  const storedTheme = useSelector((state) => state.theme)

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.href.split('?')[1])
    const theme = urlParams.get('theme') && urlParams.get('theme').match(/^[A-Za-z0-9\s]+/)[0]
    if (theme) {
      setColorMode(theme)
    }

    if (isColorModeSet()) {
      return
    }

    setColorMode(storedTheme)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <BrowserRouter>
      <Suspense
        fallback={
          <div className="pt-3 text-center">
            <CSpinner color="primary" variant="grow" />
          </div>
        }
      >
        <Routes>
          <Route path="*" name="Home" element={<DefaultLayout />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App
