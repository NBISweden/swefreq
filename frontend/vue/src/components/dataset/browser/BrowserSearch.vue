<template>
<div class="dataset-browser">
  <div class="dataset-panel overflowing">
    <div class="dataset-body overflowing">
      <div class="dropdown">
        <form @submit="doSearch()" arrow-select
              items= "suggestions"
              selection="activeSuggestion"
              target="query">
          <input class="form-control input-lg"
                 type="text"
                 placeholder="Search for a gene or variant or region"
                 v-model="query"
                 @change="autocomplete()"
                 data-toggle="dropdown"
                 autocomplete="off"/>
          <ul class="dropdown-menu" v-if="suggestions.length">
            <li v-for="term in suggestions" :key="term"
                :class="{'active': $index == activeSuggestion}">
              <a href="" @click="search(term)">{{ term }}</a>
            </li>
          </ul>
        </form>
      </div>

      <p class="text-muted">Examples - Gene:
        <a href="" @click="doSearch('PCSK9')" target="_self">PCSK9</a>, Transcript:
        <a href="" @click="doSearch('ENST00000407236')" target="_self">ENST00000407236</a>, Variant:
        <a href="" @click="doSearch('22-46615880-T-C')" target="_self">22-46615880-T-C</a>, Reference SNP ID:
        <a href="" @click="doSearch('rs1800234')" target="_self">rs1800234</a>, Region:
        <a href="" @click="doSearch('22:46615715-46615880')" target="_self">22:46615715-46615880</a>
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

export default {
  name: 'BrowserSearch',
  data() {
    return {
      query: '',
      suggestions: []
    }
  },
  computed: {
    ...mapGetters(['dataset']),
  },
  methods: {
    doSearch (query) {
      query;
    },
  }
};
</script>

<style scoped>
</style>
