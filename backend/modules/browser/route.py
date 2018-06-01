from . import browser_handlers as handlers

# Browser links
routes = [  (r"/api/datasets/(?P<dataset>[^\/]+)/browser/gene/(?P<gene>[^\/]+)",                                handlers.GetGene),
            (r"/api/datasets/(?P<dataset>[^\/]+)/browser/region/(?P<region>[^\/]+)",                            handlers.GetRegion),
            (r"/api/datasets/(?P<dataset>[^\/]+)/browser/transcript/(?P<transcript>[^\/]+)",                    handlers.GetTranscript),
            (r"/api/datasets/(?P<dataset>[^\/]+)/browser/variant/(?P<variant>[^\/]+)",                          handlers.GetVariant),
            (r"/api/datasets/(?P<dataset>[^\/]+)/browser/variants/(?P<datatype>[^\/]+)/(?P<item>[^\/]+)",       handlers.GetVariants),
            (r"/api/datasets/(?P<dataset>[^\/]+)/browser/coverage/(?P<datatype>[^\/]+)/(?P<item>[^\/]+)",       handlers.GetCoverage),
            (r"/api/datasets/(?P<dataset>[^\/]+)/browser/coverage_pos/(?P<datatype>[^\/]+)/(?P<item>[^\/]+)",   handlers.GetCoveragePos),
            (r"/api/datasets/(?P<dataset>[^\/]+)/browser/autocomplete/(?P<query>[^\/]+)",                       handlers.Autocomplete),
            (r"/api/datasets/(?P<dataset>[^\/]+)/browser/search/(?P<query>[^\/]+)",                             handlers.Search),
            (r"/api/datasets/(?P<dataset>[^\/]+)/browser/download/(?P<datatype>[^\/]+)/(?P<item>[^\/]+)",       handlers.Download),
        ]
