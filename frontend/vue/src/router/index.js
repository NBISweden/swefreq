import Vue from 'vue';
import VueRouter from 'vue-router';

import BrowserContainer from '../components/dataset/browser/BrowserContainer.vue';
import BrowserSearch from '../components/dataset/browser/BrowserSearch.vue';

import DatasetAbout from '../components/dataset/DatasetAbout.vue';
import DatasetAccess from '../components/dataset/DatasetAccess.vue';
import DatasetBeacon from '../components/dataset/DatasetBeacon.vue';
import DatasetTerms from '../components/dataset/DatasetTerms.vue';
import DatasetViewer from '../components/dataset/DatasetViewer.vue';

import HomeComponent from '../components/HomeComponent.vue';

import SearchInterface from '../components/SearchInterface.vue';

Vue.use(VueRouter);

let datasetStructure = [
  {
    path: '',
    redirect: 'about',
  },
  {
    path: 'about',
    component: DatasetAbout,
    props: true
  },
  {
    path: 'terms',
    component: DatasetTerms,
    props: true
  },
  {
    path: 'download',
    component: DatasetAccess,
    props: true
  },
  {
    path: 'beacon',
    component: DatasetBeacon,
    props: true
  },
  {
    path: 'browser',
    redirect: 'browser/search',
    props: true
  },
  {
    path: 'browser/search',
    component: BrowserSearch,
    props: true,
  },
  {
    path: 'browser/variant/:variantId',
    components: BrowserSearch,
    props: true,
  },
  {
    path: 'browser/gene/:identifier',
    component: BrowserContainer,
    props: true
  },
  {
    path: 'browser/transcript/:identifier',
    component: BrowserContainer,
    props: true
  },
  {
    path: 'browser/region/:identifier',
    component: BrowserContainer,
    props: true
  },
  {
    path: 'admin',
    component: DatasetAbout,
  },
]


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
      children: datasetStructure
    },
    {
      path: '/dataset/:datasetName/version/:datasetVersion',
      component: DatasetViewer,
      props: true,
      children: datasetStructure
    },
    {
      path: '*',
      redirect: '/'
    },
  ]
});

export default router;
