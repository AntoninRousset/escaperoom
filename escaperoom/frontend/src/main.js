import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import router from './router'
import store from './store'

createApp(App)
  .use(router)
  .use(store)
  .use(vuetify)
  .mount('#app')
