<template>
<div class="browser-gene">
  <div v-if="error.statusCode">
    <p>Unable to load the gene information.</p>
    <p>Reason: {{ error.statusCode }} {{ error.statusText }}</p>
  </div>

  <div class="container-fluid" v-if="gene">
    <div class="row">
      <div class="col-md-12">
        <h1>Gene: {{ gene.geneName }}</h1>
      </div>
    </div>
    <div class="row">
      <!-- HEADER -->
      <div class="col-md-6 col-xs-12">
        <dl class="dl-horizontal">
          <dt>{{ gene.geneName }}</dt>
          <dd>{{ gene.fullGeneName }}</dd>

          <dt>UCSC Browser</dt>
          <dd class="hidden-xs">
            <a :href="'http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&position=chr' + gene.chrom + '%3A' + (gene.start - 1) + '-' + (ctrl.gene.stop - 1) + '&hgt.customText=http://personal.broadinstitute.org/ruderfer/exac/exac-final.autosome-1pct-sq60-qc-prot-coding.cnv.bed'" target="_blank">
              {{ gene.chrom }}:{{ gene.start - 1 }}-{{ gene.stop - 1 }}
              <i class="fa fa-external-link"></i>
            </a>
          </dd>

          <dt>GeneCards</dt>
          <dd class="hidden-xs">
            <a :href="'http://www.genecards.org/cgi-bin/carddisp.pl?gene=' + gene.geneName" target="_blank">
              {{ gene.geneName }}
              <i class="fa fa-external-link"></i>
            </a>
          </dd>
          <!-- DROPDOWN -->
          <dt>Other</dt>
          <dd>
            <div class="dropdown">
              <button class="btn btn-default dropdown-toggle" type="button" id="external_ref_dropdown" data-toggle="dropdown">
                External References
                <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" role="menu" aria-labelledby="external_ref_dropdown">
                <li role="presentation">
                  <a :href="'http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&position=chr' + gene.chrom + '%3A' + (gene.start - 1) + '-' + (ctrl.gene.stop - 1)">
                    UCSC Browser
                    <i class="fa fa-external-link"></i>
                  </a>
                </li>
                <li role="presentation">
                  <a :href="'http://www.genecards.org/cgi-bin/carddisp.pl?gene=' + gene.geneName" target="_blank">
                    GeneCards
                    <i class="fa fa-external-link"></i>
                  </a>
                </li>
                <li role="presentation">
                  <a role="menuitem" tabindex="-1" :href="'http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?g=' + gene.geneId" target="_blank">
                    Ensembl <i class="fa fa-external-link"></i>
                  </a>
                </li>
                <li role="presentation">
                  <a role="menuitem" tabindex="-1" :href="'http://en.wikipedia.org/wiki/' + gene.geneName" target="_blank">
                    Wikipedia <i class="fa fa-external-link"></i>
                  </a>
                </li>
                <li role="presentation">
                  <a role="menuitem" tabindex="-1" :href="'http://www.ncbi.nlm.nih.gov/pubmed?term=' + gene.geneName" target="_blank">
                    PubMed Search <i class="fa fa-external-link"></i>
                  </a>
                </li>
                <li role="presentation">
                  <a role="menuitem" tabindex="-1" :href="'http://www.wikigenes.org/?search=' + gene.geneName" target="_blank">
                    Wikigenes <i class="fa fa-external-link"></i>
                  </a>
                </li>
                <li role="presentation">
                  <a role="menuitem" tabindex="-1" :href="'http://www.gtexportal.org/home/gene/' + gene.geneName" target="_blank">
                    GTEx (Expression) <i class="fa fa-external-link"></i>
                  </a>
                </li>
                <li role="presentation">
                  <a role="menuitem" tabindex="-1" :href="'https://www.proteinatlas.org/' + gene.geneId + '-' + gene.geneName + '/tissue'" target="_blank">
                    Human Protein Atlas
                    <i class="fa fa-external-link"></i>
                  </a>
                </li>
              </ul>
            </div>
          </dd>
        </dl>
      </div> <!-- END HEADER -->

        <div class="col-md-1 hidden-xs">
            <div class="dropdown">
                <button class="btn btn-default dropdown-toggle" type="button" id="transcript_dropdown" data-toggle="dropdown">
                    Transcripts
                    <span class="caret"></span>
                </button>
                <ul class="dropdown-menu" role="menu" aria-labelledby="transcript_dropdown">
                    <li f-for="transcript in transcripts" role="presentation">
                        <a role="menuitem" tabindex="-1" :href="browserLink('transcript/' + transcript.transcriptId)">
                          {{ transcript.transcriptId }}
                          <span v-if="transcript.transcriptId == ctrl.gene.canonicalTranscript">*</span>
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </div> <!-- END row -->
  </div>
  <!-- LOADING MESSAGE -->
  <div v-if="!gene" class="alert alert-info col-md-4 col-md-offset-4 text-center" >
    <strong>Loading Gene</strong>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'BrowserGene',
  data() {
    return {
      error: {
        'statusCode': null,
        'statusText': null
      },
      'gene': null,
    }
  },
  props: ['datasetName', 'datasetVersion', 'geneName'],
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
};
</script>

<style scoped>
</style>
