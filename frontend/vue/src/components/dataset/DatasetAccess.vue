<template>
<div class="dataset-access">
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
  <div v-if="authorizationLevel === logged_out">
    <div class="row">
      <div class="col-sm-12">
        <div class="dataset-body padding-tb">You need to login to request access to the summary files.</div>
      </div>
    </div>
  </div>
  <div v-else-if="authorizationLevel === no_access">
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
              <input type="text" class="form-control" id="email" v-model="user.email" v-disabled="true" placeholder="Your e-mail" />
            </div>
          </div>
          <div class="form-group">
            <label for="affiliation" class="col-sm-2 control-label">Affiliation</label>
            <div class="col-sm-4">
              <input type="text" class="form-control" id="affiliation" name="affiliation" required v-model="ctrl.user.affiliation" placeholder="Your affiliation" />
            </div>
          </div>
          <div class="form-group">
            <label for="country" class="col-sm-2 control-label">Country</label>
            <div class="col-sm-4">
              <select name="country" class="form-control" id="country"  v-model="user.country" required>
                <option value="None">Select country</option>
                <option v-for="country in availableCountries" :key="country.name" :value="country.name">{{country.name}}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <div class="col-sm-2"></div>
          </div>
          <div class="form-group">
            <div class="col-sm-offset-2 col-sm-10">
              <input type="submit" class="btn btn-primary" @click="sendRequest(requestForm.$valid)" />
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
  <div v-else-if="authorizationLevel === thank_you">
    <div class="row">
      <div class="col-sm-12">
        <div class="dataset-body padding-tb">Thank you for your application. We will review it as soon as possible, thank you for your patience.</div>
      </div>
    </div>
  </div>
  <div v-else-if='authorizationLevel === has_requested_access'>
    <div class="row">
      <div class="col-sm-12">
        <div class="dataset-body padding-tb">Your access request is currently under review, thank you for your patience.</div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetAccess',
  data() {
    return {
      authorizationLevel: '',
    }
  },
  computed: {
    dataContactIsEmail () {
      return this.dataset.version.dataContactLink.includes("@");
    },
    ...mapGetters(['dataset', 'collections', 'study', 'user', 'avalableCountries'])
  },
  methods: {
    updateAuthorizationLevel() {
      if (!Object.prototype.hasOwnProperty.call(this, "user") || this.user.user == null) {
        this.authorizationLevel = "logged_out";
      }
      else if (Object.prototype.hasOwnProperty.call(this, "dataset")) {
        this.authorizationLevel = this.dataset.authorizationLevel;
      }
    }
  },
  created () {
    this.$store.dispatch('getCountries');
    this.$store.dispatch('getUser');
    this.updateAuthorizationLevel();
  },
};

</script>

<style scoped>
</style>
