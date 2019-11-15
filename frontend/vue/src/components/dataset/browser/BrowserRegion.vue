<template>
<div class="browser-gene">
  <div v-if="error.statusCode">
    Unable to load region information.
  </div>
  <div class="container" v-if="region">
    <!-- HEADER -->
    <div class="col-md-12">
      <h1 v-if="rsid">{{ rsid }}</h1>
      <h1 v-else>Region: {{ region.chrom }}
        <span v-if="region.stop"> / {{ region.start }} / {{ region.stop }}</span>
      </h1>
    </div>

    <!-- WARNINGS -->
    <div v-if='region.statusText==="The region is too large"'>
      <div class="alert alert-danger col-md-offset-3 col-md-6">
        <h3>Region too large!</h3>
        <p>The region is too large. Please submit a region of at most 100 kb.</p>
        <p>If you require larger regions, please see our <a :href="'/dataset/' + dataset.shortName + '/download'">Download</a> page for raw data.</p>
      </div>
    </div>
    <div v-if="region.stop">
      <div v-if="region.stop < region.start">
        <div class="alert alert-danger col-md-offset-3 col-md-6">
          <h3>Invalid region!</h3>
          <p>The region ends ({{ region.stop }}) before it begins ({{ region.start }}).</p>
          <p>Did you mean <router-link :to="browserLink('region/' + region.chrom + '-' + region.stop + '-' + region.start)">{{ region.chrom }}-{{ region.stop }}-{{ region.start }}</router-link>?</p>
        </div>
      </div>
    </div>
    <!-- GENES -->
    <div v-if="region.genes">
      <div class="section_header">Genes</div>
      <ul>
        <li v-for="gene in region.genes" :key="gene.geneId">
          <router-link :to="browserLink('gene/' + gene.geneId)">{{ gene.geneId }}</router-link>
          ({{ gene.fullGeneName }})
        </li>
      </ul>
    </div>
  </div>
  <!-- LOADING MESSAGE -->
  <div v-if="!region" class="alert alert-info col-md-4 col-md-offset-4 text-center" >
    <strong>Loading Region</strong>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';

export default {
  name: 'BrowserGene',
  data() {
    return {
      error: {
        'statusCode': null,
        'statusText': null
      },
      region: null,
      'tmp': null,
    }
  },
  props: ['datasetName', 'datasetVersion', 'identifier'],
  computed: {
    ...mapGetters(['dataset']),
  },
  methods: {
    browserLink (link) {
      if (this.datasetVersion) {
        return "/dataset/" + this.datasetName + "/version/" + this.datasetVersion + "/browser/" + link;
      }
      return "/dataset/" + this.datasetName + "/browser/" + link;
    }
  },
  created () {
    let url = '';
    if (this.$props.datasetVersion) {
      url = '/api/dataset/' + this.$props.datasetName +
        '/version/' + this.$props.datasetVersion +
        '/browser/region/' + this.$props.geneName;
    }
    else {
      url = '/api/dataset/' + this.$props.datasetName +
        '/browser/region/' + this.$props.identifier;
    }
    axios
      .get(url)
      .then((response) => {
        this.region = response.data.region;
      })
      .catch((error) => {
        this.error.statusCode = error.status;
        this.error.statusText = error.statusText;
      });
  },
};
</script>

<style scoped>
</style>
