<template>
<div class="row dataset-row">
  <div class="col-md-1"></div>
  <div class="col-md-10">
    <div class="dataset-panel">
      <div :class="{'dataset-heading': true, 'future-title' : dataset.future}">{{ dataset.fullName }}</div>
      <div class="dataset-body">
        <div v-if="dataset.hasImage">
          <img :src="'/api/dataset/' + dataset.shortName + '/logo'" class="dataset-logo" :alt="dataset.shortName + 'logo'" />
        </div>
        <div v-if="dataset.future" class='future-blurb'>This version will become public at {{ dataset.version.availableFrom }}.</div>
        <div v-html="dataset.version.description" />
      </div>
      <div class="dataset-links">
        <li><a :href="dataset.urlbase">More information</a></li>
        <li><a :href="dataset.urlbase + '/beacon'">Beacon</a></li>
        <li><a :href="dataset.urlbase + '/browser'">Graphical Browser</a></li>
      </div>
    </div>
  </div>
  <div class="col-md-1"></div>
</div>
</template>

<script>
export default {
  name: 'DatasetEntry',
  data() {
    return {
    }
  },
  props: ["dataset"],
};

</script>

<style scoped>

</style>
