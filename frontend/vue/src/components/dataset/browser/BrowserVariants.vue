<template>
<div class="browser-variants">
  <div v-if="error">
    <p>Unable to load the variants.</p>
    <p>Reason: {{ error }}</p>
  </div>
  <div class="container" v-else>
    <div class="row">
      <div class="col-md-12">
        <span class="btn-group radio-button-group" @change="filterVariants">
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
        <input type="checkbox" id="variants-filter-non-pass" v-model="filterIncludeNonPass" @change="filterVariants">
        <label for="variants-filter-non-pass">
          Include filtered (non-PASS) variants
        </label>
        <br />
        <a class="btn btn-success" :href="'/api/dataset/' + dataset.shortName +
                                          '/browser/download/' + dataType + '/' + identifier +
                                          '/filter/' + filterVariantsBy + '~' + filterIncludeNonPass"
           target="_self">Export table to CSV</a><br/>
        <span class="label label-info">&dagger; denotes a consequence that is for a non-canonical transcript</span>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <div v-if="loaded">Number of variants: {{filteredVariants.length}} (including filtered: {{variants.length}})</div><div v-else>Loading...</div>
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
          <tbody>
            <tr v-for="variant in orderedVariants" :key="variant.variantId">
              <td :title="variant['variantId']" class="variantId">
                <router-link :to="browserLink('variant/' + variant['variantId'] )">
                  {{formatVariant(variant)}}
                </router-link>
              </td>
              <td :title="variant['chrom']" class="chrom" >{{variant['chrom'] }}</td>
              <td :title="variant['pos']" class="pos" >{{variant['pos'] }}</td>
              <td :title="variant['HGVS']" class="HGVS" >
                {{variant['HGVS'] }}
                <span v-if="variant['HGVS'] && variant['CANONICAL'] != 'YES'" title="Non-canonical">
                  &dagger;
                </span>
              </td>
              <td :title="variant['filter']" class="filter">{{variant['filter'] }}</td>
              <td :title="variant['majorConsequence']" class="majorConsequence">{{variant['majorConsequence'] }}</td>
              <td :title="variant['flags']" class="flags">{{variant['flags'] }}</td>
              <td :title="variant['alleleCount']" class="alleleCount">{{variant['alleleCount'] }}</td>
              <td :title="variant['alleleNum']" class="alleleNum">{{variant['alleleNum'] }}</td>
              <td :title="variant['homCount']" class="homCount">{{variant['homCount'] }}</td>
              <td :title="variant['alleleFreq']" class="alleleFreq">
                <div>{{variant['alleleFreq'].toFixed(4)}}</div>
                <img :src="require('../../../assets/img/steel_blue.png')">
                <img v-for="threshold in variantBoxThresholds" :key="threshold"
                     :src="variant['alleleFreq'] >= threshold && variant['alleleCount'] > 1 
                           ?  require('../../../assets/img/steel_blue.png')
                           : require('../../../assets/img/white.png')">
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';
import Vue2Filters from 'vue2-filters'

export default {
  name: 'BrowserVariants',

  mixins: [Vue2Filters.mixin],

  data() {
    return {
      error: null,
      filterVariantsBy: "all",
      filterIncludeNonPass: false,
      filterVariantsOld: null,
      variantBoxThresholds: [0, 1/10000, 1/1000, 1/100, 1/20, 1/2],
      item: null,
      itemType: null,
      filteredVariants: [],
      orderByField: "pos",
      reverseSort: false,
      variants: [],
      variantHeaders: [],
      loaded: false,
    }
  },

  props: ['datasetName', 'datasetVersion', 'dataType', 'identifier'],
  computed: {
    ...mapGetters(['dataset']),
    orderedVariants: function() {
      return this.orderBy(this.filteredVariants, this.orderByField, this.reverseSort ? -1 : 1);
    }
  },

  methods: {
    formatVariant (variant, len=12) {
      function shortenSeq(input, len=12) {
        let tail = Math.floor((len-5)/2);
        if (input.length >= len) {
          return input.substr(0,tail) + "[...]" + input.substr(input.length-tail,input.length);
        }
        return input;
      }

      let segments = variant["variantId"].split("-");
      let text = "";
      text += segments[0] + "-" + segments[1];
      text += " " + shortenSeq(segments[2], len);
      text += " → ";
      text += " " + shortenSeq(segments[3], len);
      if ( variant["rsid"] ) {
        text += " (" + variant["rsid"] + ")";
      }
      return text;
    },

    reorderVariants (event, field) {
      if (field == this.orderByField) {
        this.reverseSort = !this.reverseSort;
      }
      else {
        this.orderByField = field;
        this.reverseSort = false;
      }
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
    let url = '/api/dataset/' + this.$props.datasetName;
    if (this.$props.datasetVersion) {
      url += '/version/' + this.$props.datasetVersion;
    }
    url += '/browser/variants/' + this.$props.dataType +
      '/' + this.$props.identifier;
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

        this.variants = variants;
        this.variantHeaders = response.data.headers;
        this.filterVariants();
        this.loaded = true;
      })
      .catch((error) => {
        this.error = error;
      });
  }
};
</script>

<style scoped>
</style>
