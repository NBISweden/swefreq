<template>
<div class="dataset-access" v-if="Object.keys(dataset).length > 0">
  <div class="row">
    <div class="col-sm-12">
      <div class="alert" role="alert">
        <strong>Nota Bene:</strong> You can only request access to, and
        download, summary files here<span v-if="dataset.version.dataContactLink">,
          if you want access to the underlying individual data you need to
          {{ dataContactIsEmail ? "contact" : "visit" }}
          <a :href="dataContactIsEmail ? 'mailto:' : '' + dataset.version.dataContactLink">{{ dataset.version.dataContactName }}</a></span>.
      </div>
    </div>
  </div>
  <div v-if="!user.user">
    <div class="col-sm-12">
      <div class="dataset-body padding-tb">You need to login to request access to the summary files.</div>
    </div>
  </div>
  <div v-else-if="dataset.authorizationLevel === 'no_access'">
    <h3>Request access to summary files</h3>
    <div class="row clearfix">
      <div class="col-md-12 column">
        <form class="form-horizontal" role="form" name="requestForm">
          <div class="form-group">
            <label for="user_name" class="col-sm-2 control-label">Name</label>
            <div class="col-sm-4">
              <input type="text" class="form-control" id="user_name" v-model="user.user" :disabled="true" placeholder="Your name" />
            </div>
          </div>
          <div class="form-group">
            <label for="email" class="col-sm-2 control-label">E-mail</label>
            <div class="col-sm-4">
              <input type="text" class="form-control" id="email" v-model="user.email" :disabled="true" placeholder="Your e-mail" />
            </div>
          </div>
          <div class="form-group">
            <label for="affiliation" class="col-sm-2 control-label">Affiliation</label>
            <div class="col-sm-4">
              <input type="text" class="form-control" id="affiliation" name="affiliation" required v-model="affiliation" placeholder="Your affiliation"/>
            </div>
          </div>
          <div class="form-group">
            <label for="country" class="col-sm-2 control-label">Country</label>
            <div class="col-sm-4">
              <select name="country" class="form-control" id="country"  v-model="country" required>
                <option value="">-- Select country --</option>
                <option v-for="country in availableCountries" :key="country.name" :value="country.name">{{country.name}}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <div class="col-sm-2"></div>
            <div class="col-sm-4">
              <input type="checkbox" id="newsletter" v-model="newsLetter">
              <label class="control-label" for="newsletter">I want a newsletter</label>
            </div>
          </div>
          <div class="form-group">
            <div class="col-sm-2"></div>
          </div>
          <div class="form-group">
            <div class="col-sm-offset-2 col-sm-10">
              <input type="submit" class="btn btn-primary" @click="requestAccess" />
            </div>
          </div>
        </form>
      </div>
    </div>
    <div class="row clearfix">
      <div class="col-md-1 column"></div>
      <div class="col-md-8 column">
        <p>By submitting the application for registration you confirm that the information provided in the application is accurate.</p>
        <p>By submitting the application for registration you also agree to have the information that you submit (Name, affiliation, country and email) handled in accordance with the General Data Protection Regulation ((EU) 2016/679). The stored information will only be used for internal administrative purposes and not shared with other parties.</p>
      </div>
    </div>
  </div>
  <div v-else-if="dataset.authorizationLevel === 'thank_you'">
    <div class="row">
      <div class="col-sm-12">
        <div class="dataset-body padding-tb">
          Thank you for your application. We will review it as soon as possible, thank you for your patience.
        </div>
      </div>
    </div>
  </div>
  <div v-else-if="dataset.authorizationLevel === 'has_requested_access'">
    <div class="row">
      <div class="col-sm-12">
        <div class="dataset-body padding-tb">
          Your access request is currently under review, thank you for your patience.
        </div>
      </div>
    </div>
  </div>
  <div v-else-if="dataset.authorizationLevel === 'has_access'">
    <h2>Terms of use for the {{ dataset.shortName }} dataset (release {{ dataset.version.version }})</h2>
    <div v-html="dataset.version.terms"></div>

    <h2>Consent</h2>

    <p>
      <label for="consent"><b>I hereby consent to the agreement:</b></label>
      <input id="consent" type="checkbox" v-model="checked" @change="consented" :disabled="checked">
    </p>

    <h2>Files</h2>

    <div class='table-responsive'>
      <table class="table file-download">
        <thead>
          <tr>
            <th></th>
            <th>File</th>
            <th>Size</th>
            <th>Temporary link<a class="popup-trigger"
                                 tabindex="0"
                                 data-trigger="focus"
                                 title="Temporary link"
                                 data-placement="top"
                                 data-toggle="popover"
                                 :data-content="'Time-limited link' + (files.length>1?'s':'') + ' that can be used to download the file' + files.length>1?'s':'' + ' without logging in to the site, e.g. with a command line tool'">[?]</a> <span v-if='!temporaries'><a class="btn btn-primary btn-xs" :class="{'disabled': !checked}" href="#" @click="createTemporaryLink">Create</a></span></th>
            <th>Valid Until</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in files" class="table" :key="file.name">
            <td><a class="btn btn-primary btn-download btn-sm" :class="{'disabled': !checked}" :download="file.name" :href="file.uri" target="_self" @click="downloadData" aria-label="Download" title="Download"><span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span></a></td>
            <td>{{file.name}}</td>
            <td class="text-right">{{file.humanSize}}</td>
            <td>
              <div class="temporary-links">
                <input class="input-sm" type="text" :value="file.tempUrl" size="50" readonly>
                <a v-if="canCopy" :class="{'disabled': !temporaries}" class="btn btn-primary btn-sm" @click="copyLink(file.tempUrl)" :aria-label="'Copy' + file.tempUrl + ' to clipboard'" title="Copy to clipboard"><span class="glyphicon glyphicon-copy" aria-hidden="true"></span></a>
              </div>
            <td><nobr>{{ file.expiresOn }}</nobr></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';

export default {
  name: 'DatasetAccess',
  data() {
    return {
      affiliation: '',
      country: '',
      sendError: '',
      newsLetter: false,
      checked: false,
      files: [],
      temporaries: [],
      canCopy: false,
    }
  },
  props: ['datasetName', 'datasetVersion'],
  watch: {
    user: function () {
      this.country = this.user.country;
      this.affiliation = this.user.affiliation;
    }
  },
  computed: {
    dataContactIsEmail () {
      return this.dataset.version.dataContactLink.includes("@");
    },
    ...mapGetters(['dataset', 'user', 'availableCountries'])
  },    
  methods: {
    requestAccess(dataset, user) {
      axios.post("/api/dataset/" + this.$props.datasetName + "/users/" + user.email + "/request",
                 {
                   "email":       this.user.email,
                   "userName":    this.user.userName,
                   "affiliation": this.user.affiliation,
                   "country":     this.country,
                   "_xsrf":       this.getXsrf(),
                   "newsletter":  this.newsLetter ? 1 : 0
                 })
        .then(() => {
          this.$store.dispatch('getUser');
        })
        .catch((error) => {
          this.sendError = error;
        });
    },
    getXsrf() {
      let name = "_xsrf=";
      let decodedCookie = decodeURIComponent(document.cookie);
      let ca = decodedCookie.split(';');
      for(let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
          return c.substring(name.length, c.length);
        }
      }
      return ""
    },
    createTemporaryLink(fileName) {
      fileName;
    },
    downloadData() {
    },
    copyLink(fileUrl) {
      fileUrl;
    },
  },
  created () {
    let url = "/api/dataset/" + this.$props.datasetName;
    if (this.$props.datasetVersion) {
      url += "/versions/" + this.$props.datasetVersion;
    }
    url += "/files";
    axios
      .get(url)
      .then((response) => {
        this.files = response.data.files;
      });
    
    this.$store.dispatch('getCountries');
    this.affiliation = this.user.affiliation;
    this.country = this.user.country;
  },
};
</script>

<style scoped>
  
</style>
