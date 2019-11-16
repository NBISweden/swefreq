<template>
<div class="dataset-bar">
  <ul class="nav nav-tabs">
    <li :class="{'active': this.$route.path.endsWith('/about')}"><router-link :to="'/dataset/' + datasetName + '/about'">Information</router-link></li>
    <li :class="{'active': this.$route.path.endsWith('/terms')}"><router-link :to="'/dataset/' + datasetName + '/terms'">Terms</router-link></li>
    <li :class="{'active': this.$route.path.endsWith('/download')}"><router-link :to="'/dataset/' + datasetName + '/download'">Dataset Access</router-link></li>
    <li :class="{'active': this.$route.path.endsWith('/beacon')}"><router-link :to="'/dataset/' + datasetName + '/beacon'">Beacon</router-link></li>
    <li :class="{'active': this.$route.path.includes('/browser')}"><router-link :to="'/dataset/' + datasetName + '/browser'">Browser</router-link></li>
    <li class="dropdown">
      <a href="" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Version <span class="caret"></span></a>
      <ul class="dropdown-menu">
        <li v-for="v in datasetVersions" :key="v.name" :class="{'active': v.active, 'future': v.future}">
          <router-link :to="makeVersionUrl(v.name)">{{ v.name }}{{ v.current ? " (current)" : ""}}</router-link>
        </li>
      </ul>
    <li v-if="'isAdmin' in dataset && dataset.isAdmin" :class="{'active': this.$route.path.endsWith('/admin'), 'pull-right': true, 'admin-tab': true}"><router-link :to="'/dataset/' + datasetName + '/admin'">Admin</router-link></li>
  </ul>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetViewerBar',
  data() {
    return {
    }
  },
  props: [
    "datasetName",
    "datasetVersion"
  ],
  computed: {
    ...mapGetters(['dataset', 'datasetVersions']),
  },
  methods: {
    makeVersionUrl(dsVersion) {
      let suffixIndex = 3;
      let url = '/dataset/' + this.$props.datasetName +
          '/version/' + dsVersion + '/';
      if (this.$props.datasetVersion) {
        suffixIndex = 5;
      }
      let parts = this.$route.path.split('/');
      return url + parts.slice(suffixIndex, parts.length).join('/');
    }
  }
};

</script>

<style scoped>

</style>
