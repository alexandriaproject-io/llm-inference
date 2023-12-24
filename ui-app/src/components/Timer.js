import React, { useState, useEffect } from 'react'

function Timer() {
  const [seconds, setSeconds] = useState(0)

  useEffect(() => {
    const timeStart = new Date().getTime()
    const interval = setInterval(() => {
      setSeconds((seconds) => new Date().getTime() - timeStart)
    }, 299)

    // Clear interval on component unmount
    return () => clearInterval(interval)
  }, [])

  return <>{seconds / 1000}</>
}

export default Timer
