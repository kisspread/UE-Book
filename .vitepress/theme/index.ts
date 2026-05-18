import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ router }) {
    if (typeof window !== 'undefined') {
      // Loading bar for SPA navigation
      const bar = document.createElement('div')
      bar.id = 'vp-loading-bar'
      bar.style.cssText = (
        'position:fixed;top:0;left:0;height:3px;width:0;' +
        'background:var(--vp-c-brand-1,#3b82f6);' +
        'transition:width 0.3s ease;' +
        'z-index:9999'
      )
      document.body.appendChild(bar)

      let timer: any = null

      router.beforeEach(() => {
        clearTimeout(timer)
        bar.style.width = '70%'
        bar.style.opacity = '1'
      })

      router.afterEach(() => {
        bar.style.width = '100%'
        bar.style.opacity = '1'
        timer = setTimeout(() => {
          bar.style.width = '0'
          bar.style.opacity = '0'
        }, 300)
      })
    }
  },
}
