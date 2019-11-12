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

  <div class="container" v-else>
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
        <a v-if="item" class="btn btn-success" _href="'/api/dataset/' + dataset.shortName + '/browser/download/' + itemType + '/' + item + '/filter/' + filterVariantsBy + '~' + ctrl.filterIncludeNonPass" target="_self">Export table to CSV</a><br/>
        <span class="label label-info">&dagger; denotes a consequence that is for a non-canonical transcript</span>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        Number of variants: {{filteredVariants.length}} (including filtered: {{variants.length}})
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
      filterVariantsBy: null,
      filterIncludeNonPass: false,
      item: null,
      itemType: null,
      filteredVariants: null,
      orderByField: null,
      headers: null,
      reverseSort: null,
    }
  },
  props: ['datasetName', 'datasetVersion', 'geneName'],
  computed: {
    ...mapGetters(['variants', 'variantHeaders']),
  },
  methods: {
    reorderVariants (event) {
      event;
    },
    filterVariants (event) {
      event;
    },
    browserLink (link) {
      if (this.datasetVersion) {
        return "/dataset/" + this.datasetName + "/version/" + this.datasetVersion + "/browser/" + link;
      }
      return "/dataset/" + this.datasetName + "/browser/" + link;
    }
  },
};
</script>

<style scoped>
</style>
