import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp() {
    if (typeof window !== 'undefined') {
      const bar = document.createElement('div')
      bar.id = 'vp-loading-bar'
      bar.style.cssText = (
        'position:fixed;top:0;left:0;height:3px;width:0;' +
        'background:var(--vp-c-brand-1,#3b82f6);' +
        'transition:width 0.3s ease;' +
        'z-index:9999;opacity:0'
      )
      document.body.appendChild(bar)

      let timer: any = null
      const show = () => { bar.style.width = '70%'; bar.style.opacity = '1' }
      const hide = () => {
        bar.style.width = '100%'
        timer = setTimeout(() => { bar.style.width = '0'; bar.style.opacity = '0' }, 300)
      }

      // Intercept link clicks for SPA navigation
      document.addEventListener('click', (e) => {
        const link = (e.target as HTMLElement).closest('a')
        if (link && link.href && link.href.startsWith(window.location.origin)) {
          clearTimeout(timer); show()
          // Hide after SPA content swap (popstate fires on route change)
          const onDone = () => { hide(); window.removeEventListener('popstate', onDone) }
          window.addEventListener('popstate', onDone)
          // Fallback: hide after 5s if popstate never fires
          setTimeout(onDone, 5000)
        }
      })

      // Hide on initial page load
      window.addEventListener('load', () => hide())
    }
  },
}
