/**
 * Time utilities for consistent MST formatting across the application
 */

/**
 * Get current local date in YYYY-MM-DD format (MST)
 */
export const getLocalDateString = (date: Date = new Date()): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Format a datetime string or Date to MST with nice formatting
 * @param dateTime - ISO string, Date object, or null
 * @returns Formatted string like "Nov 27, 2025 2:30 PM" or "—" if null
 */
export const formatMST = (dateTime: string | Date | null | undefined): string => {
  if (!dateTime) return '—'
  
  try {
    const date = typeof dateTime === 'string' ? new Date(dateTime) : dateTime
    
    // Format in MST (Mountain Standard Time - UTC-7)
    const options: Intl.DateTimeFormatOptions = {
      timeZone: 'America/Denver',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }
    
    return new Intl.DateTimeFormat('en-US', options).format(date)
  } catch (e) {
    return String(dateTime)
  }
}

/**
 * Get current MST timestamp as ISO string for server submission
 */
export const getMSTNow = (): string => {
  // Create a date in MST timezone and return ISO format
  const now = new Date()
  const mstDate = new Date(now.toLocaleString('en-US', { timeZone: 'America/Denver' }))
  return mstDate.toISOString()
}

/**
 * Get an ISO-like timestamp that preserves the Mountain local date (no UTC shift).
 * Returns UTC timestamp representing the current MST time
 */
export const getMSTLocalNow = (): string => {
  const now = new Date()
  
  // Get the current time in Denver timezone
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Denver',
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit', 
    hour12: false
  })
  
  const parts = formatter.formatToParts(now)
  const lookup: Record<string, string> = {}
  parts.forEach(p => { if (p.type !== 'literal') lookup[p.type] = p.value })
  
  // Create a UTC timestamp that represents this MST time
  // When displayed with formatMST (which converts to Denver time), it will show correctly
  const mstTime = `${lookup.year}-${lookup.month}-${lookup.day}T${lookup.hour}:${lookup.minute}:${lookup.second}`
  
  // Convert this MST time to UTC by adding the offset
  const mstDate = new Date(mstTime + '-07:00') // MST is UTC-7
  
  return mstDate.toISOString()
}

/**
 * Format date only (no time) in MST
 */
export const formatMSTDate = (dateTime: string | Date | null | undefined): string => {
  if (!dateTime) return '—'
  
  try {
    const date = typeof dateTime === 'string' ? new Date(dateTime) : dateTime
    
    const options: Intl.DateTimeFormatOptions = {
      timeZone: 'America/Denver',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }
    
    return new Intl.DateTimeFormat('en-US', options).format(date)
  } catch (e) {
    return String(dateTime)
  }
}
