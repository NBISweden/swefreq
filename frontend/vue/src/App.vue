<template>
<div id="app">
  <TopBar></TopBar>
  <router-view></router-view>
  <FooterBar></FooterBar>
</div>
</template>

<script>
import TopBar from './components/TopBar.vue';
import FooterBar from './components/FooterBar.vue';

export default {
  name: 'App',
  components: {
    TopBar,
    FooterBar
  },
  data() {
    return {
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
