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
  queryResponses: [],
  currentBeacon: '',
  tmp: null,
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
  ADD_BEACON_RESPONSE (state, payload) {
    state.queryResponses.push(payload);
  },
  UPDATE_CURRENT_BEACON (state, payload) {
    state.currentBeacon = payload;
    state.queryResponses = [];
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

  updateCurrentBeacon(context, current_dataset) {
    state.cur
    if (state.currentBeacon !== current_dataset) {
      context.commit('UPDATE_CURRENT_BEACON', current_dataset);
    }
  },
  
  search (query, dataset, version) {
    axios
      .get(this.baseUrl(dataset, version) + 'search/' + query)
      .then((response) => {
        response;
      });
  },

  makeBeaconQuery (context, payload) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/beacon-elixir/query',
             {
               "params": {
                 "referenceName":   payload.chromosome,
                 "start":           payload.position - 1, // Beacon is 0-based
                 "alternateBases":  payload.allele,
                 "referenceBases":  payload.referenceAllele,
                 "datasetIds":      payload.beaconInfo.datasetId,
                 "assemblyId":      payload.beaconInfo.reference,
               }
             })
        .then((response) => {
          let queryResponse = {
            "query": {
              "chromosome":      payload.chromosome,
              "position":        payload.position,
              "allele":          payload.allele,
              "referenceAllele": payload.referenceAllele,
            }
          };

          if (response.data.exists===false) { // value may be null -> error
            queryResponse.response = { "state": "Absent" };
          }
          else if (response.data.exists===true) {
            queryResponse.response = { "state": "Present" };
          }
          else {
            queryResponse.response = { "state": "Error" };
          }
          context.commit('ADD_BEACON_RESPONSE', queryResponse);
          resolve(response);
        })
        .catch( (err) => {
          context.commit('ADD_BEACON_RESPONSE', {
            "response": { "state": "Error" },
            "query": {
              "chromosome":      payload.chromosome,
              "position":        payload.position,
              "allele":          payload.allele,
              "referenceAllele": payload.referenceAllele,
            }
          });
          reject(err);
        });
    });
  }               
}

const getters = {
  collections: state => state.collections,
  currentBeacon: state => state.currentBeacon,
  dataset: state => state.dataset,
  datasets: state => state.datasets,
  error: state => state.error,
  loggedIn: state => state.loggedIn,
  study: state => state.study,
  user: state => state.user,
  variants: state => state.variants,
  queryResponses: state => state.queryResponses,
  tmp: state => state.tmp
}

const store = new Vuex.Store({
  state,
  mutations,
  actions,
  getters
})

export default store
