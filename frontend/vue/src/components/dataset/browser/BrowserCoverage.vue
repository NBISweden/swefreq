<template>
<div class="browser-coverage">
  <!-- Loading message -->
  <div v-if="coverage.loaded" class="alert alert-info col-md-4 col-md-offset-4 text-center" >
    <strong>Loading Coverage</strong>
  </div>

  <div v-else-if="error.statusCode">
    <p>Unable to load the coverage information.</p>
    <p>Reason: {{ error.statusCode }} {{ error.statusText }}</p>
  </div>

  <div v-else-if="ctrl.coverage.data.length">
    <h3>Gene summary</h3>
    <p>(Coverage shown for <a href="http://www.ensembl.org/Help/Glossary?id=346" target="_blank">canonical transcript</a>: {
      gene.canonicalTranscript }})</p>
    <p>Mean coverage: {{ dataset.avgSeqDepth }} (entire dataset)</p>
    <div class="row">
      <div class="col-md-6">
        <label>Display:</label>
        <span class="btn-group radio-button-group">
          <input type="radio" id="display-overview" v-model="coverage.zoom" value="overview">
          <label class="btn btn-primary first-button" for="display-overview">
            Overview
          </label>
          <input type="radio" id="display-detail" v-model="coverage.zoom" value="detail">
          <label class="btn btn-primary" for="display-detail">
            Detail
          </label>
        </span>

        <label for="includeUtr">Include UTRs in plot</label>
        <input id="includeUtr" name="includeUtr" type="checkbox" v-model="coverage.includeUTR" />
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
            <select v-model="overValue" v-selected="coverage.overValue">
              <option v-for="cov in [1,5,10,15,20,25,30,50,100]" :key="cov" :value="cov">
                @change="updatedOverValue">
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
        <div id="annotationPanel" class="panel panel-default">
          <div id="annotationInfo" class="panel-body"></div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'BrowserCoverage',
  data() {
    return {
      coverage: {
        data: [],
        loaded: false,
      },
      error: {
        statusCode: undefined,
        statusText: '',
      },
      coverageMetric: undefined,
      zoom: undefined,
      overValue: undefined,
      includeUTR: false,
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
