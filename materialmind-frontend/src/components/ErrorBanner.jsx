export default function ErrorBanner({ message, onDismiss }) {
  if (!message) return null
  return (
    <div className="mx-auto max-w-5xl px-6 pt-6">
      <div className="border border-rust-500 bg-rust-500/10 rounded-md px-4 py-3 flex items-start justify-between gap-4">
        <p className="font-mono text-sm text-rust-500">{message}</p>
        <button
          onClick={onDismiss}
          className="font-mono text-xs text-rust-500 hover:text-paper shrink-0"
        >
          dismiss
        </button>
      </div>
    </div>
  )
}
