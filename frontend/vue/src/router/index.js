import Vue from 'vue';
import VueRouter from 'vue-router';

import DatasetAbout from '../components/DatasetAbout.vue';
import DatasetAccess from '../components/DatasetAccess.vue';
import DatasetTerms from '../components/DatasetTerms.vue';
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
          path: '',
          redirect: 'about',
        },
        {
          path: 'about',
          component: DatasetAbout,
        },
        {
          path: 'terms',
          component: DatasetTerms,
        },
        {
          path: 'download',
          component: DatasetAccess,
        },
        {
          path: 'beacon',
          component: DatasetAbout,
        },
        {
          path: 'browser',
          component: DatasetAbout,
        },
        {
          path: 'admin',
          component: DatasetAbout,
        },
        ]
    },
    {
      path: '*',
      redirect: '/'
    },
  ]
});

export default router;
