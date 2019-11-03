<template>
<div class="dataset-info">
  <div v-if="dataset.length !== 0">
  <div class="row dataset-row">
    <div class="col-sm-12">
      <div class="dataset-panel">
        <div class="dataset-body">
          <div v-if="dataset.hasImage">
            <img :src="'/api/dataset/' + dataset.shortName + '/logo'" class="dataset-logo" :alt="dataset.shortName + 'logo'" />
          </div>
          <div v-html="dataset.version.description" />
        </div>
      </div>
    </div>
  </div>
  <div class="row dataset-row">
    <div class="col-md-4">
      <div class="dataset-panel dataset-infobox">
        <div class="dataset-heading">Dataset</div>
        <div class="dataset-body">
          Overview
          <ul>
            <li v-if="dataset.seqType">Sequencing type: {{ dataset.seqType }}</li>
            <li v-if="dataset.seqTech">Sequencing tech: {{ dataset.seqTech }}</li>
            <li v-if="dataset.avgSeqDepth">Average Sequencing Depth: {{ dataset.avgSeqDepth }}</li>
            <li v-if="dataset.seqCenter">Sequencing Center: {{ dataset.seqCenter }}</li>
            <li v-if="dataset.datasetSize">Dataset Size: {{ dataset.datasetSize }}</li>
            <li v-if="dataset.version.varCallRef">Variant Calling reference: {{ dataset.version.varCallRef }}</li>
            <li v-if="dataset.version.refDoi">Dataset DOI: <a :href="'https://dx.doi.org/' + dataset.version.refDoi">{{ dataset.version.refDoi }}</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="dataset-panel dataset-infobox">
        <div class="dataset-heading">Study</div>
        <div class="dataset-body">
          {{ study.title }}
          <ul>
            <li v-if="study.piName">Principal Investigator: {{ study.piName }}</li>
            <li v-if="study.refDoi">DOI: <a :href="'https://dx.doi.org/' + study.refDoi">{{ study.refDoi }}</a></li>
            <li v-if="study.publicationDate">Publication date: {{ study.publicationDate }}</li>
            <li v-if="study.contactEmail">Contact: <a :href="'mailto:' + study.contactEmail">{{ study.contactNameUc }}</a></li>
            <li v-if="study.description">Description: {{ study.description }}</li>
          </ul>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="dataset-panel dataset-infobox">
        <div class="dataset-heading">Collection</div>
        <div class="dataset-body">
          <div v-for="(name, coll) in collections" :key="name">
            {{ name }} <span class='ethnicity'>{{coll.ethnicity}}</span>
            <ul v-for="sample in coll.sampleSets" :key="sample" class='samples'>
              <li>Sample size: {{ sample.sampleSize }}</li>
              <li>Phenotype: {{ sample.phenotype }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
 </div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetInfo',
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters(['dataset', 'collections', 'study'])
  },
};

</script>

<style scoped>
.navigation-bar {
    padding: 5px 0px}
.navigation-link {
    padding: 0px 10px;
}
</style>
