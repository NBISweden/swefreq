<template>
<div class="browser-coverage">
  <!-- Loading message -->
  <div v-if="!coverage.loaded" class="alert alert-info col-md-4 col-md-offset-4 text-center" >
    <strong>Loading Coverage</strong>
  </div>

  <div v-else-if="cov_error || covpos_error">
    <p>Unable to load the coverage information.</p>
    <p>Reason (coverage): {{ cov_error }}</p>
    <p>Reason (coverage position): {{ covpos_error }}</p>
  </div>

  <div v-else-if="coverage.data.length">
    <div v-if="gene">
      <h3>Gene summary</h3>
      <p>(Coverage shown for <a href="http://www.ensembl.org/Help/Glossary?id=346" target="_blank">canonical transcript</a>:
        {{ gene.canonicalTranscript }})</p>
    </div>
    <p>Mean coverage: {{ dataset.avgSeqDepth }} (entire dataset)</p>
    <div class="row">
      <div class="col-md-6">
        <label>Display:</label>
        <span class="btn-group radio-button-group">
          <input type="radio" id="display-overview" v-model="zoom" value="overview">
          <label class="btn btn-primary first-button" for="display-overview">
            Overview
          </label>
          <input type="radio" id="display-detail" v-model="zoom" value="detail">
          <label class="btn btn-primary" for="display-detail">
            Detail
          </label>
        </span>

        <label for="includeUtr">Include UTRs in plot</label>
        <input id="includeUtr" name="includeUtr" type="checkbox" v-model="includeUTR" />
      </div>

      <div class="col-md-6">
        <label>Coverage metrics:</label>
        <span>
          <label>
            <input type="radio" v-model="coverageMetric" value="mean">
            Mean
          </label>
          <label>
            <input type="radio" v-model="coverageMetric" value="median">
            Median
          </label>
          <label>
            <input type="radio" v-model="coverageMetric" value="over">
            Individuals over
            <select v-model="overValue" @change="updatedOverValue">
              <option v-for="cov in [1,5,10,15,20,25,30,50,100]" :key="cov" :value="cov">
                {{ cov }}
              </option>
            </select> X coverage
          </label>
        </span>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <canvas id="canvas" width="1000" height="300" coverage></canvas>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';

export default {
  name: 'BrowserCoverage',
  props: ['datasetName',
          'datasetVersion̈́',
          'dataType',
          'identifier'],
  data() {
    return {
      gene: null,
      coverage: {
        data: [],
        loaded: false,
      },
      region: {'start': null,
               'stop': null,
               'chrom': null},
      cov_error: undefined,
      covpos_error: undefined,
      coverageMetric: "mean",
      zoom: undefined,
      overValue: 50,
      includeUTR: false,
    }
  },
  computed: {
    ...mapGetters(['dataset']),
  },
  methods: {
    updatedOverValue (event) {
      event.preventDefault();
      this.coverageMetric = "over";
    },
  },
  created () {
    let url = '/api/dataset/' + this.$props.datasetName;
    if (this.$props.datasetVersion) {
      url += '/version/' + this.$props.datasetVersion;
    }
    url += '/browser/coverage/' + this.$props.dataType +
      '/' +  this.$props.identifier;
    axios
      .get(url)
      .then((response) => {
        this.coverage.data = response.data.coverage;
        this.coverage.loaded = true;
      })
      .catch((error) => {
        this.error = error;
        this.coverage.loaded = true;
      });
    url = '/api/dataset/' + this.$props.datasetName;
    if (this.$props.datasetVersion) {
      url += '/version/' + this.$props.datasetVersion;
    }
    url += '/browser/coverage_pos/' + this.$props.dataType +
      '/' +  this.$props.identifier;
    axios
      .get(url)
      .then((response) => {
        this.region.start = response.data.start;
        this.region.stop = response.data.stop;
        this.region.chrom = response.data.chrom;
      })
      .catch((error) => {
        this.error = error;
      });
  },

};
</script>

<style scoped>
</style>
