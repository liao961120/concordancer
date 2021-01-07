import Vue from 'vue'
import App from './App.vue'
import VueResource from 'vue-resource'

Vue.use(VueResource)  // http requests

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
