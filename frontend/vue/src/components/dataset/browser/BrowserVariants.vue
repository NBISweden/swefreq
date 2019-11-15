<template>
<div class="browser-variants">
  <div v-if="error.statusCode">
    <p>Unable to load the variants.</p>
    <p>Reason: {{ error.statusCode }} {{ error.statusText }}</p>
  </div>
  <!-- LOADING MESSAGE -->
  <div v-if="!variants" class="alert alert-info col-md-4 col-md-offset-4 text-center" >
    <strong>Loading Variants</strong>
  </div>
  <div class="container" v-if="variants && !error.statusCode">
    <div class="row">
      <div class="col-md-12">
        <span class="btn-group radio-button-group" @click="filterVariants">
          <input type="radio" id="variants-filter-all" v-model="filterVariantsBy" value="all">
          <label class="btn btn-primary first-button" for="variants-filter-all">
            All
          </label>
          <input type="radio" id="variants-filter-mislof" v-model="filterVariantsBy" value='mislof'>
          <label class="btn btn-primary" for="variants-filter-mislof">
            Missense + LoF
          </label>
          <input type="radio" id="variants-filter-lof" v-model="filterVariantsBy" value='lof'>
          <label class="btn btn-primary" for="variants-filter-lof">
            LoF
          </label>
        </span>
        <input type="checkbox" id="variants-filter-non-pass" v-model="filterIncludeNonPass" @click="filterVariants">
        <label for="variants-filter-non-pass">
          Include filtered (non-PASS) variants
        </label>
        <br />
        <a v-if="item" class="btn btn-success" :_href="'/api/dataset/' + dataset.shortName + '/browser/download/' + itemType + '/' + item + '/filter/' + filterVariantsBy + '~' + filterIncludeNonPass" target="_self">Export table to CSV</a><br/>
        <span class="label label-info">&dagger; denotes a consequence that is for a non-canonical transcript</span>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        Number of variants: {{filteredVariants.length}} (including filtered: {{variants.length}})
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <table class="table table-sm table-condensed small variant-table">
          <thead>
            <tr>
              <th v-for="header in variantHeaders" :key="header[0]" :class="header[0]">
                <a @click="reorderVariants($event, header[0])">
                  <span v-if="orderByField === header[0]">
                    <span v-if="!reverseSort" class="glyphicon glyphicon-triangle-top"></span>
                    <span v-else class="glyphicon glyphicon-triangle-bottom"></span>
                  </span>
                  {{ header[1] }}
                </a>
              </th>
            </tr>
          </thead>
        </table>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'BrowserVariants',
  data() {
    return {
      error: {
        'statusCode': null,
        'statusText': null
      },
      filterVariantsBy: "all",
      filterIncludeNonPass: false,
      filterVariantsOld: null,
      item: null,
      itemType: null,
      filteredVariants: [],
      orderByField: null,
      headers: null,
      reverseSort: null,
    }
  },
  props: ['datasetName', 'datasetVersion', 'dataType', 'identifier'],
  computed: {
    ...mapGetters(['variants', 'variantHeaders']),
  },
  methods: {
    reorderVariants (event) {
      event.preventDefault();
    },
    filterVariants () {
      let filterAsText = this.filterVariantsBy + this.filterIncludeNonPass;
      if (this.filterVariantsOld == filterAsText) {
        return;
      }
      this.filterVariantsOld = filterAsText;
      let localThis = this;

      let filterFunction = function(variant) {
        // Remove variants that didn't PASS QC
        if (! (localThis.filterIncludeNonPass || variant.isPass )) {
          return false;
        }
        switch(localThis.filterVariantsBy) {
        case "all":
          return true;
        case "lof":
          return variant.isLof;
        case "mislof":
          return variant.isLof || variant.isMissense;
        default:
          return false;
        }
      }
      this.filteredVariants = this.variants.filter( filterFunction );
    },
    browserLink (link) {
      if (this.datasetVersion) {
        return "/dataset/" + this.datasetName + "/version/" + this.datasetVersion + "/browser/" + link;
      }
      return "/dataset/" + this.datasetName + "/browser/" + link;
    }
  },
  created () {
    this.$store.dispatch('getVariants', {'dataset': this.$props.datasetName,
                                         'version': this.$props.datasetVersion,
                                         'datatype': this.dataType,
                                         'identifier': this.$props.identifier})
      .then(() => {
        this.filterVariants();
      });
  }
};
</script>

<style scoped>
</style>
