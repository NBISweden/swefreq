import Vue from 'vue';
import VueRouter from 'vue-router';

import DatasetInfo from '../components/DatasetInfo.vue';
import DatasetViewer from '../components/DatasetViewer.vue';
import HomeComponent from '../components/HomeComponent.vue';
import SearchInterface from '../components/SearchInterface.vue';

Vue.use(VueRouter);

const router = new VueRouter({
  mode: 'history',
  base: '/',
  routes: [
    {
      path: '/',
      component: HomeComponent,
    },
    {
      path: '/search',
      component: SearchInterface,
    },
    {
      path: '/dataset/:datasetName',
      component: DatasetViewer,
      props: true,
      children: [
        {
          path: 'about',
          component: DatasetInfo,
          alias: ['']
        }
        ]
    },
    {
      path: '*',
      redirect: '/'
    },
  ]
});

export default router;
