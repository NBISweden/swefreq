import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const state = {
  error: {},
  user: {},
  datasets: {},
  dataset: {},
  study: {},
  collections: {},
  variants: {},
}

const mutations = {
  UPDATE_USER (state, payload) {
    state.user = payload;
  },
  UPDATE_COLLECTIONS (state, payload) {
    state.collections = payload;
  },
  UPDATE_DATASET (state, payload) {
    state.dataset = payload;
  },
  UPDATE_DATASETS (state, payload) {
    state.datasets = payload;
  },
  UPDATE_STUDY (state, payload) {
    state.study = payload;
  },
  UPDATE_VARIANTS (state, payload) {
    state.variants = payload;
  },
}

const actions = {
  baseUrl(dataset, version) {
    var url = "/api/dataset/" + dataset + "/";
    if ( version ) {
      url += "version/" + version + "/";
    }
    url += "browser/";

    return url;                                                                                                       
  },
  getUser ({ commit }) {
    axios
      .get('/api/users/me')
      .then((response) => {
        commit('UPDATE_USER', response.data);
      });
  },
  getDatasetList ({ commit }) {
    axios
      .get('/api/dataset')
      .then((response) => {
        commit('UPDATE_DATASETS', response.data.data);
      });
  },
  getDataset (context, ds_name) {
    axios
      .get('/api/dataset/' + ds_name)
      .then((response) => {
        context.commit('UPDATE_DATASET', response.data);
      });
    axios
      .get('/api/dataset/' + ds_name + '/collection')
      .then((response) => {
        context.commit('UPDATE_COLLECTIONS', response.data.collections);
        context.commit('UPDATE_STUDY', response.data.study);
      });
  },
  search (query, dataset, version) {
    axios
      .get(this.baseUrl(dataset, version) + 'search/' + query)
      .then((response) => {
        response;
      });
  }
}

const getters = {
  collections: state => state.collections,
  dataset: state => state.dataset,
  datasets: state => state.datasets,
  error: state => state.error,
  loggedIn: state => state.loggedIn,
  study: state => state.study,
  user: state => state.user,
  variants: state => state.variants,
}

const store = new Vuex.Store({
  state,
  mutations,
  actions,
  getters
})

export default store
