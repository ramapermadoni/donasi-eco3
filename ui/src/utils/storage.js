// Akses localStorage/sessionStorage yang aman (private mode / diblokir tidak melempar).
export const lsGet = (k, fb = null) => { try { return localStorage.getItem(k) ?? fb } catch { return fb } }
export const lsSet = (k, v) => { try { localStorage.setItem(k, v); return true } catch { return false } }
export const lsDel = (k) => { try { localStorage.removeItem(k); return true } catch { return false } }
export const ssGet = (k, fb = null) => { try { return sessionStorage.getItem(k) ?? fb } catch { return fb } }
export const ssSet = (k, v) => { try { sessionStorage.setItem(k, v); return true } catch { return false } }
