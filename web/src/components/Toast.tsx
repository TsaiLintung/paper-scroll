import { useEffect } from 'react'
import './Toast.css'

export type ToastKind = 'info' | 'error' | 'success'

interface ToastProps {
  message: string
  kind?: ToastKind
  onClose: () => void
  duration?: number
}

export const Toast = ({
  message,
  kind = 'info',
  onClose,
  duration = 4000,
}: ToastProps) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration)
    return () => clearTimeout(timer)
  }, [duration, onClose])

  return (
    <div className={`toast toast--${kind}`}>
      <span>{message}</span>
      <button type="button" onClick={onClose} aria-label="Dismiss">
        ×
      </button>
    </div>
  )
}
