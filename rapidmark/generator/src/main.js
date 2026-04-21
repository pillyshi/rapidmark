import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'

// Create and mount Vue app
const app = createApp(App)

app.use(vuetify)

app.mount('#app')