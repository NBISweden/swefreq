import Vue from 'vue';
import VueRouter from 'vue-router';

const BrowserContainer = () => import(/* webpackChunkName: "browser" */ '../components/dataset/browser/BrowserContainer.vue')
const BrowserSearch = () => import(/* webpackChunkName: "browser" */ '../components/dataset/browser/BrowserSearch.vue')
const BrowserVariant = () => import(/* webpackChunkName: "browser" */ '../components/dataset/browser/BrowserVariant.vue')

const DatasetAbout = () => import(/* webpackChunkName: "dataset" */ '../components/dataset/DatasetAbout.vue')
const DatasetAdmin = () => import(/* webpackChunkName: "dataset" */ '../components/dataset/DatasetAdmin.vue')
const DatasetAccess = () => import(/* webpackChunkName: "dataset" */ '../components/dataset/DatasetAccess.vue')
const DatasetBeacon = () => import(/* webpackChunkName: "dataset" */ '../components/dataset/DatasetBeacon.vue')
const DatasetTerms = () => import(/* webpackChunkName: "dataset" */ '../components/dataset/DatasetTerms.vue')
const DatasetViewer = () => import(/* webpackChunkName: "dataset" */ '../components/dataset/DatasetViewer.vue')

import HomeComponent from '../components/HomeComponent.vue';
import UserProfile from '../components/UserProfile.vue';

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
      path: '/profile',
      component: UserProfile,
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
