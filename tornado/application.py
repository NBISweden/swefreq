import tornado.template as template
import tornado.gen
import logging
import applicationTemplate
import auth
import json
import secrets
import torndb as database
import pymongo

db = database.Connection(host = secrets.mysqlHost,
                         database = secrets.mysqlSchema,
                         user = secrets.mysqlUser,
                         password = secrets.mysqlPasswd)

class query(auth.UnsafeHandler):
    def get(self, *args, **kwargs):
        sChr = self.get_argument('chrom', '')
        iPos = self.get_argument('pos', '')
        dataset = self.get_argument('dataset', '')
        allele = self.get_argument('allele', '')
        reference = self.get_argument('ref', 'dummy')

        if sChr == '' or iPos == '' or not iPos.isdigit() or allele == '' or dataset == '':
            self.send_error(400)
            return
        exists = lookupAllele(sChr.upper(), int(iPos), allele.upper(), reference, dataset)
        if self.get_argument('format', '') == 'text':
            self.set_header('Content-Type', 'text/plain')
            self.write(str(exists))
        else:
            self.write({
                'response': {
                    'exists': exists,
                    'observed': 0,
                    },
                'query': {
                    'chromosome': sChr,
                    'position': iPos,
                    'allele': allele,
                    'dataset': dataset,
                    'reference': reference
                    },
                'beacon': 'nbis-beacon'
                })

class info(auth.UnsafeHandler):
    def get(self, *args, **kwargs):
        query_uri = "%s://%s/query?" % (self.request.protocol, self.request.host)
        self.write({
            'id': u'nbis-beacon',
            'name': u'NBIS Beacon',
            'organization': u'NBIS',
            'api': u'0.2',
            #'description': u'Swefreq beacon from NBIS',
            'datasets': [
                {
                    'id': 'exac',
                    # 'description': 'Description',
                    # 'size': { 'variants': 1234, 'samples': 12 },
                    # 'data_uses': [] # Data use limitations
                    'reference': 'hg20'
                },
            ],
            'homepage':  "%s://%s" % (self.request.protocol, self.request.host),
            #'email': u'swefreq-beacon@nbis.se',
            #'auth': 'None', # u'oauth2'
            'queries': [
                query_uri + 'chrom=1&pos=13372&dataset=exac&allele=C',
                query_uri + 'dataset=exac&chrom=2&pos=46199&allele=ICAG&format=text',
                query_uri + 'dataset=exac&chrom=2&pos=45561&allele=D3'
                ] #
            })

def lookupAllele(chrom, pos, allele, reference, dataset):
    """CHeck if an allele is present in the database
    Args:
        chrom: The chromosome, format matches [1-22XY]
        pos: Coordinate within a chromosome. Position is a number and is 1-based
        allele: Any string of nucleotides A,C,T,G or D, I for deletion and insertion, respectively.
        reference: The human reference build that was used (currently unused)
        dataset: Dataset to look in (currently used to select Mongo database)
    Returns:
        The string 'true' if the allele was found, otherwise the string 'false'
    """
    client = pymongo.MongoClient(host=secrets.mongodbhost, port=secrets.monogdbport)
    mdb = client[dataset]

    if allele[0] == 'D' or allele[0] == 'I':
        pos -= 1

    res = mdb.variants.find_one({'chrom': chrom, 'pos': pos})
    if not res:
        return False

    # Just a (point) mutation
    if allele[0] != 'D' and allele[0] != 'I':
        return res['alt'] == allele

    # Insertion. Inserted sequence is from second position and onwards and
    # should match allele
    if allele[0] == 'I':
        return res['alt'][1:] == allele[1:]

    # Deletion. Just check that the length of the ref is one more than the
    # length of the deletion.
    if allele[0] == 'D':
        return int(allele[1:])+1 == len(res['ref'])

    raise Exception("Can't find the thingy") # Should probably be a 4XX response

class home(auth.UnsafeHandler):
    def get(self, *args, **kwargs):
        t = template.Template(applicationTemplate.indexHead)
        self.write(t.generate())
        if self.get_current_token() != None:
            t = template.Template(applicationTemplate.indexHtml)
        elif self.get_current_user() != None:
            t = template.Template(applicationTemplate.indexNoAccess)
        else:
            t = template.Template(applicationTemplate.notAuthorizedHtml)
            logging.info(self.get_current_user())
        self.write(t.generate(user_name=self.get_current_user(),
                              email=self.get_current_email(),
                              ExAC=secrets.ExAC_server))

class getUser(auth.UnsafeHandler):
    def get(self, *args, **kwargs):
        sUser = self.get_current_user()
        sEmail = self.get_current_email()

        tRes = db.query("""select full_user from swefreq.users where
                           email='%s' and full_user='YES'""" % sEmail)
        lTrusted = True if len(tRes)==1 else False

        tRes = db.query("""select full_user from swefreq.users where
                              email='%s'""" % sEmail)
        lDatabase = True if len(tRes) == 1 else False
        tRes = db.query("""select full_user from swefreq.users where
                              email='%s' and swefreq_admin='YES'""" % sEmail)
        lAdmin = True if len(tRes) == 1 else False

        logging.info("getUser: " + str(sUser) + ' ' + str(sEmail))
        self.finish(json.dumps({'user':sUser,
                                'email':sEmail,
                                'trusted':lTrusted,
                                'isInDatabase':lDatabase,
                                'admin':lAdmin}))

class requestAccess(auth.UnsafeHandler):
    def get(self, *args, **kwargs):
        sUser = self.get_current_user()
        sEmail = self.get_current_email()
        logging.info("Request: " + sUser + ' ' + sEmail)
        self.finish(json.dumps({'user':sUser, 'email':sEmail}))

    def post(self, *args, **kwargs):
        try:
            userName = self.get_argument("userName", default='', strip=False)
            email = self.get_argument("email", default='', strip=False)
            affiliation = self.get_argument("affiliation", default='', strip=False)
        except:
            return
        # This is the only chance for XSRF in the application
        # avoid it by checking that the email sent by google is the same as
        # supplied by the form post
        sEmail = self.get_current_email()
        if sEmail != email:
            return

        sSql = """
        insert into swefreq.users (username, email, affiliation, full_user)
        values ('%s', '%s', '%s', '%s')
        """ % (userName, email, affiliation, 'NO')
        try:
            db.execute(sSql)
        except:
            logging.error("Error inserting " + userName + ' ' + email)

class logEvent(auth.SafeHandler):
    def get(self, sEvent):
        sEmail=self.get_current_email()
        sSql = """insert into swefreq.user_log (email, action) values ('%s', '%s')
        """ % (sEmail, sEvent)
        db.execute(sSql)
        if sEvent == 'download':
            tRes = db.query("""select ifnull(download_count, 0) as download_count
                               from swefreq.users where email = '%s'""" % sEmail)
            db.execute("""update swefreq.users set download_count='%s'
                          where email='%s'""" % (int(tRes[0].download_count)+1, sEmail))

class approveUser(auth.SafeHandler):
    def get(self, sEmail):
        sLoggedInEmail = self.get_current_email()
        tRes = db.query("""select full_user from swefreq.users where
                              email='%s' and swefreq_admin='YES'""" % sLoggedInEmail)
        if len(tRes) == 0:
            return
        db.update("""update swefreq.users set full_user = 'YES'
        where email = '%s'""" % sEmail)

class deleteUser(auth.SafeHandler):
    def get(self, sEmail):
        sLoggedInEmail = self.get_current_email()
        tRes = db.query("""select email from swefreq.users where
                              email='%s' and swefreq_admin='YES'""" % sLoggedInEmail)
        if len(tRes) == 0:
            return
        if sLoggedInEmail == sEmail:
            # Don't let the admin delete hens own account
            return
        db.execute("""update swefreq.users set full_user = 'NO'
        where email = '%s'""" % sEmail)

class denyUser(auth.SafeHandler):
    def get(self, sEmail):
        sLoggedInEmail = self.get_current_email()
        tRes = db.query("""select email from swefreq.users where
                              email='%s' and swefreq_admin='YES'""" % sLoggedInEmail)
        if len(tRes) == 0:
            return
        if sLoggedInEmail == sEmail:
            # Don't let the admin delete hens own account
            return
        db.execute("""delete from swefreq.users where email = '%s'""" % sEmail)

class getOutsandingRequests(auth.SafeHandler):
    def get(self, *args, **kwargs):
        tRes = db.query("""select username, email, affiliation, create_date
        from swefreq.users where full_user = 'NO'""")
        jRes = []
        for row in tRes:
            sDate = str(row.create_date).split(' ')[0]
            jRes.append({'user' : row.username,
                         'email' : row.email,
                         'affiliation' : row.affiliation,
                         'applyDate' : sDate
            })
        self.finish(json.dumps(jRes))

class getApprovedUsers(auth.SafeHandler):
    def get(self, *args, **kwargs):
        tRes = db.query("""select username, email, affiliation,
        IFNULL(download_count, 0) as download_count
        from swefreq.users where full_user = 'YES'""")
        jRes = []
        for row in tRes:
            jRes.append({'user' : row.username,
                         'email' : row.email,
                         'affiliation' : row.affiliation,
                         'downloadCount' : row.download_count
            })
        self.finish(json.dumps(jRes))

class StaticFileHandler(tornado.web.StaticFileHandler):
    def get(self, path, include_body=True):
        if path.endswith('woff'):
            self.set_header('Content-Type','application/font-woff')
        super(StaticFileHandler, self).get(path, include_body)
