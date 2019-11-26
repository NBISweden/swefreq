<template>
<div class="dataset-browser">
  <div class="dataset-panel overflowing">
    <div class="dataset-body overflowing">
      <div class="dropdown">
        <form @submit="doSearch" arrow-select
              items= "suggestions"
              selection="activeSuggestion"
              target="query">
          <input class="form-control input-lg"
                 type="text"
                 placeholder="Search for a gene or variant or region"
                 v-model="query"
                 @change="autoComplete"
                 data-toggle="dropdown"
                 autocomplete="off"/>
          <div class="dropdown-menu" v-if="suggestions.length">
            <a class="dropdown-item" v-for="term in suggestions" :key="term" @click="doFixedsearch($event, term)">{{term}}</a>
          </div>
        </form>
        <div class="warning" v-if="searchError">{{ searchError }}</div>
      </div>
      
      <p class="text-muted">Examples - Gene:
        <a href="" @click="doFixedSearch($event, 'PCSK9')" target="_self">PCSK9</a>, Transcript:
        <a href="" @click="doFixedSearch($event, 'ENST00000407236')" target="_self">ENST00000407236</a>, Variant:
        <a href="" @click="doFixedSearch($event, '22-46615880-T-C')" target="_self">22-46615880-T-C</a>, Reference SNP ID:
        <a href="" @click="doFixedSearch($event, 'rs1800234')" target="_self">rs1800234</a>, Region:
        <a href="" @click="doFixedSearch($event, '22:46615715-46615880')" target="_self">22:46615715-46615880</a>
      </p>
      
      <div class="col-md-12">
        <p> This genome browser displays the variant frequencies obtained from the
          {{ dataset.datasetSize }} individuals of the {{ dataset.shortName }} dataset,
          using software adapted from the Exome Aggregation Consortium (ExAC).</p>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';

export default {
  name: 'BrowserSearch',
  data() {
    return {
      query: '',
      suggestions: [],
      result: null,
      error: null,
      searchError: '',
    }
  },
  props: ['datasetName', 'datasetVersion'],
  computed: {
    ...mapGetters(['dataset']),
  },
  methods: {
    doSearch (event) {
      event.preventDefault();
      let url = '/api/dataset/' + this.$props.datasetName;
      if (this.$props.datasetVersion) {
        url += '/version/' + this.$props.datasetVersion;
      }
      url += '/browser/search/' + this.query;

      axios
        .get(url)
        .then((response) => {
          if ( response.data.type == "not_found" ) {
            this.searchError = "No results found";
          } else if ( response.data.type == "error" ) {
            this.searchError = "Search error";
          } else {
            let url = '/dataset/' + this.$props.datasetName;
            if (this.$props.datasetVersion) {
              url += '/version/' + this.$props.datasetVersion;
            }
            url += '/browser/' + response.data.type + '/' + response.data.value;
            this.$router.push(url);
          }
        })
        .catch((error) => {
          this.error = error;
        });
    },
    doFixedSearch (event, query) {
      event.preventDefault();
      this.query = query;
      this.doSearch(event);
    },
    autoComplete(event) {
      event.preventDefault();
      this.searchError = '';
      let url = '/api/dataset/' + this.$props.datasetName;
      if (this.$props.datasetVersion) {
        url += '/version/' + this.$props.datasetVersion;
      }
      url += '/browser/autocomplete/' + this.query;

      axios
        .get(url)
        .then((response) => {
          this.suggestions = response.data.values;
        })
        .catch((error) => {
          this.error = error;
        });
    }
  }
};
</script>

<style scoped>
</style>
