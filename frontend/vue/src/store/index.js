import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const state = {
  availableCountries: [],
  error: {},
  user: {},
  datasets: {},
  dataset: {},
  datasetVersions: [],
  study: {},
  collections: {},
  variants: [],
  variantHeaders: [],
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
  UPDATE_COUNTRIES (state, payload) {
    state.countries = payload;
  },
  UPDATE_DATASET (state, payload) {
    state.dataset = payload;
  },
  UPDATE_DATASET_VERSIONS (state, payload) {
    state.datasetVersions = payload;
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
  UPDATE_VARIANT_HEADERS (state, payload) {
    state.variantHeaders = payload;
  },
  ADD_BEACON_RESPONSE (state, payload) {
    state.queryResponses.push(payload);
  },
  UPDATE_CURRENT_BEACON (state, payload) {
    state.currentBeacon = payload;
    state.queryResponses = [];
  },
  TMP (state, payload) {
    state.tmp = payload;
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

  getCountries ({ commit }) {
    axios
      .get('/api/countries')
      .then((response) => {
        commit('UPDATE_COUNTRIES', response.data);
      });
  },

  getDatasetList ({ commit }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/dataset')
        .then((response) => {
          commit('UPDATE_DATASETS', response.data.data);
          resolve(response);
        })
        .catch((error) => {
          reject(error);
        });
    });
  },

  getDataset (context, payload) {
    return new Promise((resolve, reject) => {
      let baseUrl = '/api/dataset/' + payload.datasetName;
      if (payload.datasetVersion) {
        baseUrl += '/versions/' + payload.datasetVersion;
      }
      axios
        .get(baseUrl)
        .then((response) => {
          context.commit('UPDATE_DATASET', response.data);
          axios
            .get('/api/dataset/' + payload.datasetName + '/versions') 
            .then((response) => {
              context.commit('UPDATE_DATASET_VERSIONS', response.data.data);
              axios
                .get(baseUrl + '/collection')
                .then((response) => {
                  context.commit('UPDATE_COLLECTIONS', response.data.collections);
                  context.commit('UPDATE_STUDY', response.data.study);
                  resolve();
                })
                .catch((error) => {
                  reject(error);
                });
            })
            .catch((error) => {
              reject(error);
            });
        })
        .catch((error) => {
          reject(error);
        });
    });
  },

  updateCurrentBeacon(context, current_dataset) {
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

  getVariants(context, payload) {
    return new Promise((resolve, reject) => {
      let url = '';
      if (payload.version) {
        url = '/api/dataset/' + payload.dataset +
          '/version/' + payload.version +
          '/browser/variants/' + payload.datatype +
          '/' + payload.identifier;
      }
      else {
        url = '/api/dataset/' + payload.dataset +
          '/browser/variants/' + payload.datatype +
          '/' + payload.identifier;
      }
      axios
        .get(url)
        .then((response) => {
          let variants = response.data.variants;

          let mapFunction = function(variant) {
            variant.isPass = variant.filter == "PASS";
            if (variant.flags.indexOf("LoF") === -1)
              variant.isLof = false;
            else
              variant.isLof = true;
            variant.isMissense = variant.majorConsequence == "missense";
          };

          variants.map(mapFunction);

          context.commit('UPDATE_VARIANTS', variants);
          context.commit('UPDATE_VARIANT_HEADERS', response.data.headers);
          resolve(response);
        })
        .catch((error) => {
          reject(error);
          context.commit('UPDATE_VARIANTS', []);
        });
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
  availableCountries: state => state.availableCountries,
  collections: state => state.collections,
  currentBeacon: state => state.currentBeacon,
  dataset: state => state.dataset,
  datasetVersions: state => state.datasetVersions,
  datasets: state => state.datasets,
  error: state => state.error,
  loggedIn: state => state.loggedIn,
  study: state => state.study,
  user: state => state.user,
  variants: state => state.variants,
  variantHeaders: state => state.variantHeaders,
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
