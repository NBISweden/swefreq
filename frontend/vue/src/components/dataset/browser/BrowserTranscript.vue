<template>
<div class="browser-transcript">
  <div v-if="error">
    <p>Unable to load the transcript information.</p>
    <p>Reason: {{ error }}</p>
  </div>

  <div class="container" v-if="transcript">
    <h1>{{ gene.name }}</h1>
    <h4>{{ gene.fullName }}</h4>
    <h3>Transcript: {{ transcript.id }} ({{ transcript.numberOfCDS }} coding exons)</h3>
    <div class="dropdown">
      <button class="btn btn-default dropdown-toggle" type="button" data-toggle="dropdown">
        Other transcripts in this gene
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu" role="menu" aria-labelledby="transcript_dropdown">
        <li v-for="transcript in gene.transcripts" role="presentation" :key="transcript">
          <a role="menuitem" tabindex="-1" :href="browserLink('transcript/' + transcript)">
            {{ transcript }}
            <span v-if="transcript === gene.canonicalTranscript">*</span>
          </a>
        </li>
      </ul>
    </div>
  </div>
  <!-- LOADING MESSAGE -->
  <div v-if="!transcript && !error" class="alert alert-info col-md-4 col-md-offset-4 text-center">
    <strong>Loading Transcript</strong>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';

export default {
  name: 'BrowserTranscript',
  data() {
    return {
      error: null,
      transcript: null,
      gene: null,
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
        '/browser/transcript/' + this.$props.geneName;
    }
    else {
      url = '/api/dataset/' + this.$props.datasetName +
        '/browser/transcript/' + this.$props.identifier;
    }
    axios
      .get(url)
      .then((response) => {
        this.transcript = response.data.transcript;
        this.gene = response.data.gene;
      })
      .catch((error) => {
        this.error = error;
      });
  },
};
</script>

<style scoped>
</style>
