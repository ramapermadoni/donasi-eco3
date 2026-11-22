// Bagikan tautan (navigator.share) atau salin ke clipboard; onCopied dipanggil hanya setelah menyalin.
export async function shareLink(title, url, onCopied) {
  try {
    if (navigator.share) await navigator.share({ title, url })
    else { await navigator.clipboard.writeText(url); onCopied && onCopied() }
  } catch { /* cancelled */ }
}
