import Vue from 'vue';
import VueRouter from 'vue-router';

import BrowserContainer from '../components/dataset/browser/BrowserContainer.vue';
import BrowserSearch from '../components/dataset/browser/BrowserSearch.vue';
import BrowserVariant from '../components/dataset/browser/BrowserVariant.vue';

import DatasetAbout from '../components/dataset/DatasetAbout.vue';
import DatasetAdmin from '../components/dataset/DatasetAdmin.vue';
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
    props: true,
  },
  {
    path: 'admin',
    component: DatasetAdmin,
    props: true,
  },
  {
    path: 'terms',
    component: DatasetTerms,
    props: true,
  },
  {
    path: 'download',
    component: DatasetAccess,
    props: true,
  },
  {
    path: 'beacon',
    component: DatasetBeacon,
    props: true,
  },
  {
    path: 'browser/',
    redirect: 'browser/search',
  },
  {
    path: 'browser/search',
    component: BrowserSearch,
    props: true,
  },
    {
      path: 'browser/variant/:variantId',
      component: BrowserVariant,
      props: true,
    },
  {
    path: 'browser/gene/:identifier',
    component: BrowserContainer,
    props: true,
  },
  {
    path: 'browser/region/:identifier',
    component: BrowserContainer,
    props: true,
  },
  {
    path: 'browser/transcript/:identifier',
    component: BrowserContainer,
    props: true,
  },
  {
    path: 'browser/*',
    redirect: 'browser/search',
  },
];

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
      children: datasetStructure
    },
    {
      path: '/dataset/:datasetName/version/:datasetVersion',
      component: DatasetViewer,
      props: true,
      children: datasetStructure
    },
    {
      path: '/dataset/:datasetName/version/:datasetVersion/*',
      redirect: '/dataset/:datasetName/version/:datasetVersion/about',
    },
    {
      path: '/dataset/:datasetName/*',
      redirect: '/dataset/:datasetName/about',
    },
    {
      path: '*',
      redirect: '/'
    },
  ]
});

export default router;
