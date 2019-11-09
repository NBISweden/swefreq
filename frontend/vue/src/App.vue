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
  },
  created () {
    this.$store.dispatch('getUser');
  }
}
</script>

<style>
html {
  position: relative;
  min-height: 100%;
}

body {
  /* Margin bottom by footer height */
  margin-bottom: 80px;
}

.navbar {
  border-radius: 0px;
}
.navbar img {
  margin-top: -15px;
}

.hidden-blurb {
  display: none;
  transition: all 0.5s ease-in-out;
}

.blurb {
  padding-top: 30px;
  padding-bottom: 20px;
  margin-top: -20px;
  margin-bottom: 20px;
  background-color: #666;
  box-shadow: 0 5px 10px -5px #000 inset, 0 -5px 10px -5px #000 inset;
  color: #fff;
  font-size: 14pt;
}
.blurb a {
  color: #63aae7;
}

/* For beacon form validation */
input.ng-dirty.ng-valid, select.ng-dirty.ng-valid {
  border: 1px solid Green;
  background-color: #F5FFF5;
}

input.ng-dirty.ng-invalid, select.ng-dirty.ng-invalid {
  border: 1px solid Red;
  background-color: #FFF5F5;
}

/* Dataset box CSS */
.dataset-row {
  padding-bottom: 40px;
}

.dataset-infobox ul {
  font-size: 90%;
  list-style-type: none;
  margin: 0;
  margin-left: 10px;
  padding: 0;
}

.dataset-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 20px;
}
.dataset-panel .future-blurb {
  font-style: italic;
  font-size: 90%;
  color: #900;
}
.dataset-panel .future-title {
  background-color: #BE8542;
}
.dataset-panel .dataset-links {
  display: flex;
}
.dataset-panel .dataset-links li {
  display: block;
  text-align: center;
  font-size: 21px;
  font-weight: 200;
  flex-grow: 1;
  background-color: #e8e8e8;
}
.dataset-panel .dataset-links li a {
  color: #000;
}
.dataset-panel .dataset-links li:hover {
  background-color: #F47D20;
}
.dataset-panel .dataset-links .glyphicon {
  font-size: 75%;
}
.dataset-panel .dataset-links li:first-child {
  border-radius: 0 0 0 5px;
}
.dataset-panel .dataset-links li:last-child {
  border-radius: 0 0 5px 0;
}
.dataset-panel .dataset-heading {
  background-color: #85BE42;
  border-radius: 5px 5px 0 0;
  color: #fff;
  font-size: 18pt;
  padding: 2px 0 2px 7px;
}
.dataset-panel .dataset-body {
  overflow: hidden;
  height: 100%;
  width: 100%;
  padding: 15px 15px 7px 15px;
  font-size: 14pt;
  background-color: #f8f8f8;
}
.dataset-panel .dataset-body img.dataset-logo {
  max-width: 150px;
  max-height: 300px;
  float: right;
  margin: 15px;
}
.dataset-panel .dataset-body .ethnicity {
  font-style: italic;
  font-size: 80%;
}
.dataset-panel .dataset-body ul.samples {
  margin-left: 20px;
}
.dataset-panel .dataset-body ul.samples li:first-child {
  list-style-type: disc;
}

.overflowing {
  overflow: visible !important;
}

.alert-future {
  font-size: 200%;
}

.padding-tb {
  padding-top: 5em;
  padding-bottom: 3em;
}

.nav-tabs li.admin-tab a, .nav-tabs li.admin-tab a:hover {
  background-color: #337ab7;
  color: black;
}
.nav-tabs li.future {
  font-style: italic;
  background-color: #f2dede;
}

div.admin-bar ul li a.active {
  padding: 10px 15px;
  border-left: solid 1px #ddd;
  border-right: solid 1px #ddd;
  border-top: none;
  background: #fff;
  top: -1px;
}
div.admin-bar ul li a {
  border-radius: 0 0 4px 4px;
  padding: 10px 15px;
  top: -1px;
}
div.admin-bar ul.nav-tabs {
  border-bottom: none;
}

table.file-download tr td {
  vertical-align: middle;
}
table.file-download .temporary-links {
  position: relative;
  display: inline-block;
  vertical-align: middle;
}
table.file-download .temporary-links .btn {
  border-radius: 0 3px 3px 0;
  float: left;
  position: relative;
}
table.file-download .temporary-links input {
  border: 1px solid #e7e7e7;
  border-radius: 3px 0 0 3px;
  border-right: 0px;
  box-shadow: inset 0 1px 2px rgba(27, 31, 35, 0.075);
  float: left;
  outline: none;
  padding-right: 2px;
  position: relative;
}

.popup-trigger {
  font-size: 80%;
  vertical-align: super;
  cursor: pointer;
}

button .glyphicon {
  top: 2px;
}

input.btn-sm {
  float: left;
}

table.mini-table th {
  padding-right: 15px;
  text-align: right;
}

table.variant-table {
  table-layout: fixed;
  /* Allele frequency visualisation */
  /* Shorten some of the table columns */
}
table.variant-table td.alleleFreq div {
  float: left;
  margin-right: 0.5em;
}
table.variant-table td.alleleFreq img {
  border-right: 1px solid steelblue;
  border-bottom: 1px solid steelblue;
  border-top: 1px solid steelblue;
  width: 7px;
  height: 15px;
  display: block;
  float: left;
}
table.variant-table th {
  width: 8em;
}
table.variant-table td {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
table.variant-table th.alleleFreq {
  width: 12em;
}
table.variant-table th.variantId {
  width: 20em;
}

/* text for search button */
.alert-text {
  color: #900;
}

.left-margin {
  margin-left: 5px;
}

#annotationPanel {
  position: absolute;
  visibility: hidden;
}

.radio-button-group .first-button {
  border-top-left-radius: 4px !important;
  border-bottom-left-radius: 4px !important;
}
.radio-button-group label {
  display: inherit;
  max-width: inherit;
  margin-bottom: inherit;
  font-weight: inherit;
}
.radio-button-group input[type=radio] {
  display: none;
}
.radio-button-group input[type=radio]:checked + .btn {
  color: #fff;
  background-color: #286090;
  border-color: #204d74;
  box-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125);
  -webkit-box-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125);
}

/* Affiliate footer */
.footer-bar {
  padding-top: 30px;
}
.footer-bar .container {
  background-color: #f8f8f8;
  border-top: solid 1px #e7e7e7;
  margin-bottom: 0px;
  position: absolute;
  height: 110px;
  bottom: 0px;
  width: 100%;
}
.footer-bar .container img.logo {
  display: block;
  position: relative;
  top: 30px;
  margin-left: auto;
  margin-right: auto;
}
.footer-bar .container img.logo.scilife {
  top: 38px;
}
.footer-bar .container img.logo.elixir {
  top: 17px;
}
</style>
