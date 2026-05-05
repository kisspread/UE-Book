import DefaultTheme from 'vitepress/theme'
import HomeCards from './components/HomeCards.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('HomeCards', HomeCards)
  }
}
