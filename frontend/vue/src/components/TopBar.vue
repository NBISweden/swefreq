<template>
<div class="top-bar">
  <router-link to="/" class="navigation-link"><span>Search</span></router-link>
  <router-link to="/browse" class="navigation-link"><span>Browse</span></router-link>
</div>
</template>

<script>
export default {
  name: 'TopBar',
  data() {
    return {
    }
  }
}
</script>

<style scoped>
.navigation-bar {
    padding: 5px 0px}
.navigation-link {
    padding: 0px 10px;
}
</style>
