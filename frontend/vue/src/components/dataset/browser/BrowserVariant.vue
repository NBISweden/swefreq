<template>
<div class="browser-variant">
  <div v-if="error">
    <p>Unable to load the variant.</p>
    <p>Reason: {{error}} </p>
  </div>
  <div v-if="!variant && !error" class="alert alert-info col-md-4 col-md-offset-4 text-center">
    <p>Loading variant </p>
  </div>
  <div class="container" v-if="variant && !error">
    <!-- HEADER -->
    <div class="col-md-12">
      <div class="col-md-8">
        <h1><span class="hidden-xs">Variant: </span>
          {{ variant.chrom }}:{{ variant.pos }} {{ variant.ref }} / {{ variant.alt }}
        </h1>
      </div>
      <div v-if="variant.origAltAlleles.length > 1" class="col-md-4">
        <h5>
          <p>
            <span class="label label-info">Note:</span> This variant is multiallelic!
          </p>
          The other alt alleles are:
        </h5>
        <ul>
          <li v-for="allele in variant.origAltAlleles" :key="allele">
            <a :href="browserLink('variant/' + allele)">{{ allele }}</a>
          </li>
        </ul>
      </div>
    </div>
    <hr> <!-- END HEADER -->

    <!-- TOP PANES -->
    <!--  Left top pane -->
    <div class="alert alert-warning" v-if="variant.alleleNum < dataset.datasetSize * 1.6">
      <h4>Warning!</h4>
      <p>This variant is only covered in {{ (variant.alleleNum/2) | number:0 }} individuals (adjusted allele number = {{ variant.alleleNum }}).</p>
      <p>This means that the site is covered in fewer than 80% of the individuals in {{ dataset.shortName }}, which may indicate a low-quality site.</p>
    </div>
    <div class="col-md-6">
      <dl class="dl-horizontal">
        <dt><span :class="{'label': true, 'label-danger': variant.filter != 'PASS'}">Filter Status</span></dt>
        <dd>{{ variant.filter }}</dd>
        <dt>dbSNP</dt>
        <dd v-if="variant.rsid && variant.rsid != '.'">
          <a :href="'http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=' + variant.rsid" target="_blank">
            {{ variant.rsid }}
          </a>
        </dd>
        <dd v-if="!variant.rsid || variant.rsid == '.'">rsID not available</dd>
        <dt>Allele Frequency</dt>
        <dd v-if="variant.alleleFreq">{{ variant.alleleFreq.toFixed(4) }}</dd>
        <dd v-else>NA (Allele Number = 0)</dd>
        <dt>Allele Count</dt>
        <dd>{{ variant.alleleCount }} / {{ variant.alleleNum }}</dd>
        <dt>UCSC</dt>
        <dd>
          <a :href="'http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&highlight=hg19.chr' + variant.chrom + 
                    '%3A' + variant.pos + '-' + (variant.pos + variant.ref.length) + 
                    '&position=chr' + variant.chrom + '%3A' + (variant.pos - 25) + '-' + (variant.pos + variant.ref.length - 1 + 25)" target="_blank">
            {{ variant.variantId }}
            <i class="fa fa-external-link"></i>
          </a>
        </dd>
        <dt>ClinVar</dt>
        <dd v-if="!variant.rsid || variant.rsid == '.'">
          <a :href="'http://www.ncbi.nlm.nih.gov/clinvar?term=(' + variant.chrom + '%5BChromosome%5D)%20AND%20' + variant.pos + '%5BBase%20Position%20for%20Assembly%20GRCh37%5D'" target="_blank" />
        </dd>
        <dd v-if="variant.rsid && variant.rsid != '.'">
          <a :href="'http://www.ncbi.nlm.nih.gov/clinvar?term=' + variant.rsid + '%5BVariant%20ID%5D'" target="_blank">
            Click to search for variant in Clinvar
            <i class="fa fa-external-link"></i>
          </a>
        </dd>
      </dl>
    </div>

    <!-- top right pane -->
    <div class="col-md-6">
      <div class="panel panel-default">
        <div class="panel-heading">
          <span class="text-center"><strong>Site Quality Metrics</strong></span>
        </div>

        <div class="panel-body">
          <div class="alert alert-info alert-dismissable"
               ng-if="variant.origAltAlleles.length > 1" role="alert">
            <strong>Note:</strong>
            These are site-level quality metrics: they may be unpredictable for multi-allelic sites.
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <small>
            <div class="col-md-6">
              <table class="mini-table">
                <tr><th>Site Quality</th><td>{{ variant.siteQuality }}</td></tr>
                <tr v-for="(value, metric, index) in variant.qualityMetrics" :key="metric">
                  <th v-if="index%2">{{ metric }}</th><td v-if="index%2">{{ value }}</td>
                </tr>
              </table>
            </div>
            <div class="col-md-6">
              <table class="mini-table">
                <tr v-for="(value, metric, index) in variant.qualityMetrics" :key="metric">
                  <th v-if="index%2+1">{{ metric }}</th><td v-if="index%2+1">{{ value }}</td>
                </tr>
              </table>
            </div>
          </small>

        </div>
      </div>
    </div>
    <!-- TOP PANES -->

    <!-- MIDDLE PANES -->
    <!-- Left middle pane -->
    <div class="col-md-6">
      <div v-if="variant.variantId">
        <h2>Annotations</h2>
        <div v-if="variant.annotations">
          <p>This variant falls on {{ variant.transcripts.length }} transcripts in {{ variant.genes.length }}</p>
          <div class="col-md-6" v-for="(annotation, type) in variant.annotations" :key="type">
            <h5>{{ type }}</h5>

            <table class="table table-sm table-striped table-condensed small">
              <tr>
                <th>Gene</th>
                <td><a :href="browserLink('gene/' + annotation.gene.id)">
                    {{ annotation.gene.name }}
                  </a>
                </td>

                <td>
                  <div class="dropdown">
                    <button class="btn btn-xs btn-info dropdown-toggle" type="button" data-toggle="dropdown">
                      Transcripts<span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                      <li v-for="transcript in annotation.transcripts" :key=transcript.id>
                        <a :href="browserLink('transcript/' + transcript.id)">
                          {{ transcript.id }}
                          <span v-if="transcript.modification">
                            ({{ transcript.modification }})
                          </span>
                          <br/>
                          <span ng-if="transcript.polyphen">
                            Polyphen: <span>{{ transcript.polyphen }}</span>
                          </span>
                          <span ng-if="transcript.sift">
                            , SIFT: <span>{{ transcript.sift }}</span>
                          </span>
                        </a>
                      </li>
                    </ul>
                  </div>
                </td>
              </tr>
            </table>
          </div>

        </div> <!-- variant.annotations -->
        <small><span class="label label-info">Note:</span> This list may not include additional transcripts in the same gene that the variant does not overlap.</small>

        <div v-if="!variant.annotations">
          No annotations were found for this variant.
        </div>
      </div> <!-- if variantId -->
      <div v-if="!variant.variantId">
        <h3>This variant is not found in SweGen.</h3>
      </div>
    </div> <!-- col-md-6 -->

    <!-- Right middle pane -->
    <div class="col-md-6">
      <h2>Dataset Frequencies</h2>
      For all available datasets using the same reference set as {{ dataset.shortName }}.
      <div v-if="variant.popFreq">
        <table class="table table-sm table-striped table-condensed small">
          <thead>
            <tr>
              <th v-for="header in variant.popFreq.headers" :key="header[0]">{{ header[1] }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(value, dataset) in variant.popFreq.datasets" :key="dataset">
              <td v-for="header in variant.popFreq.headers" :key="header[1]">
                <span v-if="header[1] === 'freq'">{{ value[header[1]].toFixed(4) }}</span>
                <span v-else>{{ value[header[1]] }}</span>
              </td>
            </tr>
            <tr>
              <th v-for="header in variant.popFreq.headers" :key="header[1]">
                <span v-if="header[1] === 'pop'">Total</span>
                <span v-else-if="header[1] === 'freq'">{{ variant.popFreq.total[header[1]].toFixed(4) }}</span>
                <span v-else>{{ variant.popFreq.total[header[1]] }}</span>
              </th>
            </tr>
          </tbody>
        </table>
      </div> <!-- if popFreq -->
      <div v-if="!variant.popFreq">
        <p>No Dataset Frequencies available</p>
      </div> <!-- if popFreq -->
    </div>

    <!-- MIDDLE PANES -->
  </div> <!-- container -->  
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';

export default {
  name: 'BrowserVariant',
  data() {
    return {
      error: null,
      variant: null,
    }
  },
  props: ['datasetName', 'datasetId', 'variantId'],
  computed: {
    ...mapGetters(['dataset']),
  },
  methods: {
    browserLink (link) {
      if (this.datasetVersion) {
        return "/dataset/" + this.datasetName + "/version/" + this.datasetVersion + "/browser/" + link;
      }
      return "/dataset/" + this.datasetName + "/browser/" + link;
    }
  },
  created () {
    let url = '';
    if (this.$props.datasetVersion) {
      url = '/api/dataset/' + this.$props.datasetName +
        '/version/' + this.$props.datasetVersion +
        '/browser/variant/' + this.$props.variantId;
    }
    else {
      url = '/api/dataset/' + this.$props.datasetName +
        '/browser/variant/' + this.$props.variantId;
    }
    axios
      .get(url)
      .then((response) => {
        this.variant = response.data.variant;
      })
      .catch((error) => {
        this.error = error;
      });
  },
};
</script>

<style scoped>
</style>
