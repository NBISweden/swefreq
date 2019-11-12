import Vue from 'vue';
import VueRouter from 'vue-router';

import BrowserContainer from '../components/dataset/browser/BrowserContainer.vue';
import BrowserCoverage from '../components/dataset/browser/BrowserCoverage.vue';
import BrowserGene from '../components/dataset/browser/BrowserGene.vue';
import BrowserSearch from '../components/dataset/browser/BrowserSearch.vue';
import BrowserVariants from '../components/dataset/browser/BrowserVariants.vue';

import DatasetAbout from '../components/dataset/DatasetAbout.vue';
import DatasetAccess from '../components/dataset/DatasetAccess.vue';
import DatasetBeacon from '../components/dataset/DatasetBeacon.vue';
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
      alias: ['/dataset/:datasetName/version/:datasetVersion'],
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
          component: BrowserContainer,
          props: true,
          children: [
            {
              path: '',
              redirect: 'search',
            },
            {
              path: 'search',
              components: {default: BrowserSearch},
              props: true,
            },
            {
              path: 'variant/:variantId',
              components: {default: BrowserSearch},
              props: true,
            },
            {
              path: 'gene/:identifier',
              components: {
                default: BrowserGene,
                coverage_plot: BrowserCoverage,
                variant_list: BrowserVariants,
              },
              props: true
            },
            {
              path: 'transcript/:identifier',
              components: {
                default: BrowserGene,
                coverage_plot: BrowserCoverage,
                variant_list: BrowserVariants,
              },
              props: true
            },
            {
              path: 'region/:identifier',
              components: {
                default: BrowserGene,
                coverage_plot: BrowserCoverage,
                variant_list: BrowserVariants,
              },
              props: true
            },
          ]
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
