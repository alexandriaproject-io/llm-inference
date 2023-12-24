import React, { useState, useEffect } from 'react'

function Timer() {
  const [seconds, setSeconds] = useState(0)

  useEffect(() => {
    const timeStart = new Date().getTime()
    const interval = setInterval(() => {
      setSeconds((seconds) => new Date().getTime() - timeStart)
    }, 99)

    // Clear interval on component unmount
    return () => clearInterval(interval)
  }, [])

  return <>{(seconds / 1000).toFixed(3)}</>
}

export default Timer
