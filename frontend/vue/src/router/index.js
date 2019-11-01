import Vue from 'vue';
import VueRouter from 'vue-router';

import SearchInterface from '../components/SearchInterface.vue';

Vue.use(VueRouter);

const router = new VueRouter({
  mode: 'history',
  base: '/',
  routes: [
    {
      path: '/',
      component: SearchInterface,
      props: { list_type: 'solna' },
      alias: ['/search']
    },
  ]
});

export default router;
