import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import Vue2Filters from 'vue2-filters';

Vue.use(Vue2Filters);

Vue.config.productionTip = false

new Vue({
  store,
  router,
  render: h => h(App),
}).$mount('#app')
