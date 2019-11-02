import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const state = {
  user: {},
  datasets: {},
  loggedIn: false,
}

const mutations = {
  UPDATE_USER (state, payload) {
    state.user = payload;
  },
  UPDATE_DATASETS (state, payload) {
    state.datasets = payload;
  },
}

const actions = {
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
  }
}

const getters = {
  user: state => state.user,
  loggedIn: state => state.loggedIn,
  datasets: state => state.datasets,
}

const store = new Vuex.Store({
  state,
  mutations,
  actions,
  getters
})

export default store
