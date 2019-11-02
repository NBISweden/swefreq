import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const state = {
  user: {},
  loggedIn: false,
}

const mutations = {
  UPDATE_USER (state, payload) {
    state.user = payload;
    state.loggedIn = true;
  }
}

const actions = {
  getUser ({ commit }) {
    axios
      .get('/api/user/me')
      .then((response) => {
        commit('UPDATE_USER', response.data);
      });
  }
}

const getters = {
  user: state => state.user,
  loggedIn: state => state.loggedIn,
}

const store = new Vuex.Store({
  state,
  mutations,
  actions,
  getters
})

export default store
