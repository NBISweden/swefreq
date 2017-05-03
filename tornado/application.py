import applicationTemplate
import email.mime.multipart
from email.MIMEText import MIMEText
import json
import logging
import peewee
import pymongo
import smtplib
import tornado.template as template
import tornado.web

import db
import handlers
import secrets


class query(handlers.UnsafeHandler):
    def make_error_response(self):
        ret_str = ""

        checks = {
                'dataset': lambda x: "" if x == 'SweGen' else "dataset has to be SweGen\n",
                'ref': lambda x: "" if x == 'hg19' else "ref has to be hg19\n",
                'pos': lambda x: "" if x.isdigit() else "pos has to be digit\n",
        }

        for arg in ['chrom', 'pos', 'dataset', 'referenceAllele', 'allele', 'ref']:
            try:
                val = self.get_argument(arg)
                if checks.has_key(arg):
                    ret_str += checks[arg](val)
            except:
                ret_str += arg + " is missing\n"
                if checks.has_key(arg):
                    ret_str += checks[arg]("")

        dataset = self.get_argument('dataset', 'MISSING')

        return ret_str

    def get(self, *args, **kwargs):
        the_errors = self.make_error_response()
        if len(the_errors) > 0:
            self.set_status(400);
            self.set_header('Content-Type', 'text/plain');
            self.write(the_errors);
            return

        sChr      = self.get_argument('chrom', '').upper()
        iPos      = self.get_argument('pos', '')
        dataset   = self.get_argument('dataset', '')
        referenceAllele = self.get_argument('referenceAllele', '').upper()
        allele = self.get_argument('allele', '').upper()
        reference = self.get_argument('ref', '').upper()

        exists = lookupAllele(sChr, int(iPos), referenceAllele, allele, reference, dataset)

        if self.get_argument('format', '') == 'text':
            self.set_header('Content-Type', 'text/plain')
            self.write(str(exists))
        else:
            self.write({
                'response': {
                    'exists': exists,
                    'observed': 0,
                    'externalUrl': "%s://%s" % ('https', self.request.host),
                    },
                'query': {
                    'chromosome': sChr,
                    'position': iPos,
                    'referenceAllele': referenceAllele,
                    'allele': allele,
                    'dataset': dataset,
                    'reference': reference
                    },
                'beacon': 'swefreq-beacon'
                })

class info(handlers.UnsafeHandler):
    def get(self, *args, **kwargs):
        query_uri = "%s://%s/query?" % ('https', self.request.host)
        self.write({
            'id': u'swefreq-beacon',
            'name': u'Swefreq Beacon',
            'organization': u'SciLifeLab',
            'api': u'0.3',
            #'description': u'Swefreq beacon from NBIS',
            'datasets': [
                {
                    'id': 'SweGen',
                    # 'description': 'Description',
                    # 'size': { 'variants': 1234, 'samples': 12 },
                    # 'data_uses': [] # Data use limitations
                    'reference': 'hg19'
                },
            ],
            'homepage':  "%s://%s" % ('https', self.request.host),
            #'email': u'swefreq-beacon@nbis.se',
            #'auth': 'None', # u'oauth2'
            'queries': [
                query_uri + 'dataset=SweGen&ref=hg19&chrom=1&pos=55500975&referenceAllele=C&allele=T',
                query_uri + 'dataset=SweGen&ref=hg19&chrom=1&pos=55505551&referenceAllele=A&allele=ACTG&format=text',
                query_uri + 'dataset=SweGen&ref=hg19&chrom=2&pos=41936&referenceAllele=AG&allele=A'
                ] #
            })

def lookupAllele(chrom, pos, referenceAllele, allele, reference, dataset):
    """CHeck if an allele is present in the database
    Args:
        chrom: The chromosome, format matches [1-22XY]
        pos: Coordinate within a chromosome. Position is a number and is 0-based
        allele: Any string of nucleotides A,C,T,G
        alternate: Any string of nucleotides A,C,T,G
        reference: The human reference build that was used (currently unused)
        dataset: Dataset to look in (currently used to select Mongo database)
    Returns:
        The string 'true' if the allele was found, otherwise the string 'false'
    """
    client = pymongo.MongoClient(host=secrets.mongo_host, port=secrets.mongo_port)

    # The name of the dataset in the database is exac as required by the
    # exac browser we are using.
    if dataset == 'SweGen':
        dataset = 'exac'

    mdb = client[dataset]
    mdb.authenticate(secrets.mongo_user, secrets.mongo_password)

    # Beacon is 0-based, our database is 1-based in coords.
    pos += 1
    res = mdb.variants.find({'chrom': chrom, 'pos': pos})
    for r in res:
        if r['alt'] == allele and r['ref'] == referenceAllele:
            return True

    return False

class home(handlers.UnsafeHandler):
    def get(self, *args, **kwargs):
        t = template.Template(applicationTemplate.index)

        has_access = self.is_authorized()
        is_admin   = self.is_admin()

        name = None
        email = None
        if self.current_user:
            name = self.current_user.name
            email = self.current_user.email

        self.write(t.generate(user_name  = name,
                              has_access = has_access,
                              email      = email,
                              is_admin   = is_admin,
                              ExAC       = secrets.exac_server))

class getUser(handlers.UnsafeHandler):
    def get(self, *args, **kwargs):
        user = self.current_user

        ret = {
                'user': None,
                'email': None,
                'trusted': False,
                'admin': False,
                'isInDatabase': False
        }
        if user:
            ret = {
                    'user':         user.name,
                    'email':        user.email,
                    'trusted':      self.is_authorized(),
                    'admin':        self.is_admin(),
                    'isInDatabase': not user.is_dirty() # Not exactly in database
            }

        logging.info("getUser: " + str(ret['user']) + ' ' + str(ret['email']))
        self.finish(json.dumps(ret))

class country_list(handlers.UnsafeHandler):
    def get(self, *args, **kwargs):
        self.write({'countries': map( lambda c: {'name': c}, self.country_list())})

    def country_list(self):
        return ["Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra",
                "Angola", "Anguilla", "Antarctica", "Antigua and Barbuda",
                "Argentina", "Armenia", "Aruba", "Australia", "Austria",
                "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados",
                "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan",
                "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil",
                "British Indian Ocean Territory", "British Virgin Islands",
                "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia",
                "Cameroon", "Canada", "Cape Verde", "Cayman Islands",
                "Central African Republic", "Chad", "Chile", "China",
                "Christmas Island", "Cocos Islands", "Colombia", "Comoros",
                "Cook Islands", "Costa Rica", "Croatia", "Cuba", "Curacao",
                "Cyprus", "Czech Republic", "Democratic Republic of the Congo",
                "Denmark", "Djibouti", "Dominica", "Dominican Republic",
                "East Timor", "Ecuador", "Egypt", "El Salvador",
                "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia",
                "Falkland Islands", "Faroe Islands", "Fiji", "Finland", "France",
                "French Polynesia", "Gabon", "Gambia", "Georgia", "Germany",
                "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guam",
                "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana",
                "Haiti", "Honduras", "Hong Kong", "Hungary", "Iceland", "India",
                "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel",
                "Italy", "Ivory Coast", "Jamaica", "Japan", "Jersey", "Jordan",
                "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait",
                "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia",
                "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau",
                "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives",
                "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius",
                "Mayotte", "Mexico", "Micronesia", "Moldova", "Monaco",
                "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique",
                "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands",
                "Netherlands Antilles", "New Caledonia", "New Zealand",
                "Nicaragua", "Niger", "Nigeria", "Niue", "North Korea",
                "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau",
                "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru",
                "Philippines", "Pitcairn", "Poland", "Portugal", "Puerto Rico",
                "Qatar", "Republic of the Congo", "Reunion", "Romania", "Russia",
                "Rwanda", "Saint Barthelemy", "Saint Helena",
                "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin",
                "Saint Pierre and Miquelon",
                "Saint Vincent and the Grenadines", "Samoa", "San Marino",
                "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
                "Seychelles", "Sierra Leone", "Singapore", "Sint Maarten",
                "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
                "South Africa", "South Korea", "South Sudan", "Spain",
                "Sri Lanka", "Sudan", "Suriname", "Svalbard and Jan Mayen",
                "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan",
                "Tajikistan", "Tanzania", "Thailand", "Togo", "Tokelau", "Tonga",
                "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan",
                "Turks and Caicos Islands", "Tuvalu", "U.S. Virgin Islands",
                "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
                "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican",
                "Venezuela", "Vietnam", "Wallis and Futuna", "Western Sahara",
                "Yemen", "Zambia", "Zimbabwe" ];


class requestAccess(handlers.SafeHandler):
    def get(self, *args, **kwargs):
        user = self.current_user
        name = user.name
        email = user.email

        logging.info("Request: " + name + ' ' + email)
        self.finish(json.dumps({'user':name, 'email':email}))

    def post(self, *args, **kwargs):
        userName    = self.get_argument("userName", default='',strip=False)
        email       = self.get_argument("email", default='', strip=False)
        affiliation = self.get_argument("affiliation", strip=False)
        country     = self.get_argument("country", strip=False)
        newsletter  = self.get_argument("newsletter", strip=False)

        # This is the only chance for XSRF in the application
        # avoid it by checking that the email sent by google is the same as
        # supplied by the form post
        user = self.current_user
        if user.email != email:
            return

        user.affiliation = affiliation
        user.country = country
        logging.info(u"Inserting into database: {}, {}".format(user.name, user.email))

        try:
            with db.database.atomic():
                user.save() # Save to database
                db.DatasetAccess.create(
                        user             = user,
                        dataset          = self.dataset,
                        wants_newsletter = newsletter
                    )
        except Exception as e:
            logging.error(e)


class logEvent(handlers.SafeHandler):
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

class approveUser(handlers.SafeHandler):
    def get(self, sEmail):
        sLoggedInEmail = self.get_current_email()
        tRes = db.query("""select full_user from swefreq.users where
                              email='%s' and swefreq_admin""" % sLoggedInEmail)
        if len(tRes) == 0:
            return
        db.update("""update swefreq.users set full_user = '1'
        where email = '%s'""" % sEmail)

        msg = email.mime.multipart.MIMEMultipart()
        msg['to'] = sEmail
        msg['from'] = secrets.from_address
        msg['subject'] = 'Swefreq account created'
        msg.add_header('reply-to', secrets.reply_to_address)
        body = "Your Swefreq account has been activated."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(secrets.mail_server)
        server.sendmail(msg['from'], [msg['to']], msg.as_string())


class revokeUser(handlers.SafeHandler):
    def get(self, sEmail):
        sLoggedInEmail = self.get_current_email()
        tRes = db.query("""select email from swefreq.users where
                              email='%s' and swefreq_admin""" % sLoggedInEmail)
        if len(tRes) == 0:
            return
        if sLoggedInEmail == sEmail:
            # Don't let the admin delete hens own account
            return
        db.execute("""update swefreq.users set full_user = '0'
                      where email = '%s'""" % sEmail)

class deleteUser(handlers.SafeHandler):
    def get(self, sEmail):
        sLoggedInEmail = self.get_current_email()
        tRes = db.query("""select email from swefreq.users where
                              email='%s' and swefreq_admin""" % sLoggedInEmail)
        if len(tRes) == 0:
            return
        if sLoggedInEmail == sEmail:
            # Don't let the admin delete hens own account
            return
        db.execute("""delete from swefreq.users where email = '%s'""" % sEmail)

class getOutstandingRequests(handlers.SafeHandler):
    def get(self, *args, **kwargs):
        q = db.User.select(db.User).join(
                db.DatasetAccess
            ).switch(
                db.User
            ).join(
                db.UserLog,
                on=(   (db.UserLog.user    == db.User.user)
                     & (db.UserLog.dataset == db.DatasetAccess.dataset)
                )
            ).where(
                db.DatasetAccess.dataset    == self.dataset,
                db.DatasetAccess.has_access == 0,
                db.UserLog.action           == 'access_requested'
            ).annotate(
                db.UserLog,
                peewee.fn.Max(db.UserLog.ts).alias('apply_date')
            )

        json_response = []
        for user in q:
            apply_date = user.apply_date.strftime('%Y-%m-%d')
            json_response.append({
                'user':        user.name,
                'email':       user.email,
                'affiliation': user.affiliation,
                'country':     user.country,
                'applyDate':   apply_date
            })

        self.finish(json.dumps(json_response))

class getApprovedUsers(handlers.SafeHandler):
    def get(self, *args, **kwargs):
        ## All users that have access to the dataset and how many times they have
        ## downloaded it
        query = db.User.select(
                db.User, db.DatasetAccess.wants_newsletter
            ).join(
                db.DatasetAccess
            ).switch(
                db.User
            ).join(
                db.UserLog,
                peewee.JOIN.LEFT_OUTER,
                on=(   (db.User.user        == db.UserLog.user)
                     & (db.UserLog.action   == 'download')
                     & (db.UserLog.dataset  == db.DatasetAccess.dataset)
                )
            ).where(
                db.DatasetAccess.dataset    == self.dataset,
                db.DatasetAccess.has_access == 1
            ).annotate(db.UserLog)

        json_response = []
        for user in query:
            json_response.append({
                    'user':          user.name,
                    'email':         user.email,
                    'affiliation':   user.affiliation,
                    'country':       user.country,
                    'downloadCount': user.count,
                    'newsletter':    user.dataset_access.wants_newsletter
                })

        self.finish(json.dumps(json_response))
