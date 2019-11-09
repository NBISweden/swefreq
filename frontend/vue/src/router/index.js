import Vue from 'vue';
import VueRouter from 'vue-router';

import DatasetAbout from '../components/dataset/DatasetAbout.vue';
import DatasetAccess from '../components/dataset/DatasetAccess.vue';
import DatasetBeacon from '../components/dataset/DatasetBeacon.vue';
import DatasetBrowser from '../components/dataset/DatasetBrowser.vue';
import DatasetTerms from '../components/dataset/DatasetTerms.vue';
import DatasetViewer from '../components/dataset/DatasetViewer.vue';
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
      path: '/dataset/:datasetName/',
      component: DatasetViewer,
      props: true,
      alias: ['/dataset/:datasetName/version/:datasetVersion?'],
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
          component: DatasetBeacon,
          props: true
        },
        {
          path: 'browser',
          component: DatasetBrowser,
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
