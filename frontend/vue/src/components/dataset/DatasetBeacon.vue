<template>
<div class="dataset-beacon">
  <h2>Search</h2>
  <div class="alert alert-danger" v-if="!newQuery.beaconInfo.reference">
    <h3>Beacon error</h3>
    <p>Unable to retrieve the reference set from the Beacon.</p>
    <p>Either the dataset version is not available or the service is down.</p>
  </div>

  <form role="form" name="beacon_form" class="form-horizontal" @submit="makeQuery">
    <div class="form-group">
      <label for="chromosome" class="col-sm-3 control-label">Chromosome</label>
      <div class="col-sm-3">
        <input type="text" required class="form-control" id="chromosome" name="chromosome" v-model="newQuery.chromosome" placeholder="Chromosome" :disabled="!newQuery.beaconInfo.reference">
      </div>

      <label for="position" class="col-sm-3 control-label">Position</label>
      <div class="col-sm-3">
        <input type="number" min="0" required class="form-control" id="position" v-model="newQuery.position" placeholder="Position" :disabled="!newQuery.beaconInfo.reference">
      </div>
    </div>

    <div class="form-group">
      <label for="referenceAllele" class="col-sm-3 control-label">Reference Allele</label>
      <div class="col-sm-3">
        <input type="text" required  class="form-control" id="referenceAllele" v-model="newQuery.referenceAllele" name='referenceAllele' placeholder="Reference Allele" :disabled="!newQuery.beaconInfo.reference">
      </div>
    
      <label for="allele" class="col-sm-3 control-label">Alternate Allele</label>
      <div class="col-sm-3">
        <input type="text" required class="form-control" id="allele" v-model="newQuery.allele" name='allele' placeholder="Alternate Allele" :disabled="!newQuery.beaconInfo.reference">
      </div>
    </div>

    <div class="form-group">
      <div class="col-sm-offset-3 col-sm-7">
        <button class="btn btn-primary" :disabled="!(newQuery.chromosome && newQuery.position && newQuery.referenceAllele && newQuery.allele && newQuery.beaconInfo.reference)">Search</button>
        <span class="left-margin alert-text" v-if="!(newQuery.chromosome && newQuery.position && newQuery.referenceAllele && newQuery.allele) && newQuery.beaconInfo.reference">Need to fill in all values before searching</span>
      </div>
      <div class="col-sm-2">
        <a style='cursor: pointer' @click="showDetails = !showDetails" class="pull-right">
          <span v-if="! showDetails">Show</span>
          <span v-if="showDetails">Hide</span>
          Help
        </a>
      </div>
      <div class="col-sm-2">
        <a style='cursor: pointer' @click="fillExample" class="pull-right">Show example</a>
      </div>
    </div>
  </form>
  <div class="row" v-if="showDetails">
    <div class="col-xs-12">
      <p><small>Reference and Alternate allele follows the
          <a href="https://samtools.github.io/hts-specs/VCFv4.2.pdf">VCF 4.2 specification</a>.</small></p>
    
      <p><small><em>Example</em>: an insertion of TA on position 45
          would be specified as CTA on position 44 as alternate
          allele and C as reference allele (given that C is what is
          on the position prior to the insertion).</small></p>
    </div>
  </div>

  <h2>Results</h2>
  <div class="table-responsive">
    <table class="table table-striped">
      <tbody>
        <tr>
          <th></th>
          <th>Chromosome</th>
          <th>Position</th>
          <th>Reference Allele</th>
          <th>Alternate Allele</th>
        </tr>
        <tr v-for="row in queryResponses" :key="row">
          <td>{{row.response.state}}</td>
          <td>{{row.query.chromosome}}</td>
          <td>{{row.query.position}}</td>
          <td>{{row.query.referenceAllele}}</td>
          <td>{{row.query.allele}}</td>
        </tr>
      </tbody>
    </table>
  </div>
 </div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';

export default {
  name: 'DatasetBeacon',

  data() {
    return {
      newQuery: {'chromosome': '',
                 'position': null,
                 'referenceAllele': '',
                 'allele': '',
                 'beaconInfo': {}},
      showDetails: false,
      localResponses: [],
    }
  },
  
  props: ['datasetName', 'datasetVersion'],

  computed: {
    ...mapGetters(['dataset', 'queryResponses', 'currentBeacon']),
  },

  methods: {
    makeQuery (event) {
      event.preventDefault();
      this.$store.dispatch('makeBeaconQuery', this.newQuery);
    },
    fillExample (event) {
      event.preventDefault();
      this.newQuery.chromosome = "22";
      this.newQuery.position = 46615880;
      this.newQuery.referenceAllele = "T";
      this.newQuery.allele = "C"
    }
  },

  created () {
    axios
      .get('/api/beacon-elixir/')
      .then((response) => {
        let d = response.data.datasets;
        let references = [];
        for (let i = 0; i < d.length; i++) {
          let dataset = d[i].id;
          let ds_name = this.$props.datasetName;
          if (dataset.includes(ds_name)) {
            references.push(dataset);
          }
        }
        let beaconId = "";
        let reference = "";

        if (this.$props.datasetVersion) {
          for (let i = 0; i < references.length; i++) {
            if (references[i].split(":")[2] === this.$props.datasetVersion) {
              reference = references[i].split(":")[0].substring(0, 6);
              beaconId = references[i];
            }
          }
        }
        else {
          let highestVer = 0;
          for (let i = 0; i < references.length; i++) {
            let ver = parseInt(references[i].split(":")[2]);
            if (ver > highestVer) {
              highestVer = ver;
              reference = references[i].split(":")[0].substring(0, 6);
              beaconId = references[i];
            }
          }
        }
        this.newQuery.beaconInfo = {
          "reference": reference,
          "datasetId": beaconId,
        };
        this.$store.dispatch('updateCurrentBeacon', beaconId);
      })
      .catch(() => {
        this.newQuery.beaconInfo = {
          'reference': '',
          'datasetId': '',
        }
        this.$store.dispatch('updateCurrentBeacon', this.$props.datasetName);
      });
  }
};
</script>

<style scoped>
.navigation-bar {
    padding: 5px 0px}
.navigation-link {
    padding: 0px 10px;
}
</style>
