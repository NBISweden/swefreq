from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import logging
from datetime import datetime
import peewee
import smtplib
import tornado.web

import db
import handlers
import settings


def build_dataset_structure(dataset_version, user=None, dataset=None):
    if dataset is None:
        dataset = dataset_version.dataset
    r = db.build_dict_from_row(dataset)

    r['version'] = db.build_dict_from_row(dataset_version)
    r['version']['available_from'] = r['version']['available_from'].strftime('%Y-%m-%d')

    r['has_image']  = dataset.has_image()

    if user:
        r['is_admin'] = user.is_admin(dataset)
        if user.has_access(dataset):
            r['authorization_level'] = 'has_access'
        elif user.has_requested_access(dataset):
            r['authorization_level'] = 'has_requested_access'
        else:
            r['authorization_level'] = 'no_access'

    return r


class ListDatasets(handlers.UnsafeHandler):
    def get(self):
        # List all datasets available to the current user, earliear than now OR
        # versions that are available in the future that the user is admin of.
        user = self.current_user

        ret = []
        if user:
            futures = db.DatasetVersion.select(
                    ).join(
                        db.Dataset
                    ).join(
                        db.DatasetAccess
                    ).where(
                        db.DatasetVersion.available_from > datetime.now(),
                        db.DatasetAccess.user == user,
                        db.DatasetAccess.is_admin
                    )
            for f in futures:
                dataset = build_dataset_structure(f, user)
                dataset['future'] = True
                ret.append( dataset )

        for version in db.DatasetVersionCurrent.select():
            dataset = build_dataset_structure(version, user)
            dataset['current'] = True
            ret.append( dataset )

        self.finish({'data':ret})


class GetDataset(handlers.UnsafeHandler):
    def get(self, dataset, version=None):
        user = self.current_user

        current_version = False
        future_version  = False
        dataset = db.get_dataset(dataset)
        if version:
            version = db.DatasetVersion.select().where(
                    db.DatasetVersion.version == version,
                    db.DatasetVersion.dataset == dataset
                ).get()
        else:
            version = dataset.current_version.get()
            current_version = True

        if version.available_from > datetime.now():
            # If it's not available yet, only return if user is admin.
            if not (user and user.is_admin(dataset)):
                self.send_error(status_code=403)
                return
            future_version = True
        elif not current_version:
            # Make another check on whether this is the current version
            cv = dataset.current_version.get()
            current_version = cv.version == version.version

        ret = build_dataset_structure(version, user, dataset)
        ret['current'] = current_version
        ret['future']  = future_version

        self.finish(ret)


class ListDatasetVersions(handlers.UnsafeHandler):
    def get(self, dataset):
        user = self.current_user
        dataset = db.get_dataset(dataset)

        versions = db.DatasetVersion.select(
                db.DatasetVersion.version, db.DatasetVersion.available_from
            ).where(
                db.DatasetVersion.dataset == dataset
            )
        logging.info("ListDatasetVersions")

        data = []
        found_current = False
        for v in reversed(versions):
            current = False
            future  = False

            # Skip future versions unless admin
            if v.available_from > datetime.now():
                if not (user and user.is_admin(dataset)):
                    continue
                future = True

            # Figure out if this is the current version
            if not found_current and v.available_from < datetime.now():
                found_current = True
                current       = True

            data.insert(0, {
                'name':           v.version,
                'available_from': v.available_from.strftime('%Y-%m-%d'),
                'current':        current,
                'future':         future,
            })

        self.finish({'data': data})


class DatasetFiles(handlers.AuthorizedHandler):
    def get(self, dataset, version=None, *args, **kwargs):
        dataset = db.get_dataset(dataset)
        if version:
            dataset_version = dataset.versions.where(db.DatasetVersion.version==version).get()
        else:
            dataset_version = dataset.current_version.get()
        ret = []
        for f in dataset_version.files:
            ret.append(db.build_dict_from_row(f))
        self.finish({'files': ret})


class Collection(handlers.UnsafeHandler):
    def get(self, dataset, *args, **kwargs):
        user = self.current_user
        dataset = db.get_dataset(dataset)

        collections = {}

        for sample_set in dataset.sample_sets:
            collection = sample_set.collection
            if not collection.name in collections:
                collections[collection.name] = {
                        'sample_sets': [],
                        'ethnicity': collection.ethnicity,
                    }
            collections[collection.name]['sample_sets'].append( db.build_dict_from_row(sample_set) )


        ret = {
            'collections': collections,
            'study':       db.build_dict_from_row(dataset.study)
        }
        ret['study']['publication_date'] = ret['study']['publication_date'].strftime('%Y-%m-%d')

        self.finish(ret)


class GetUser(handlers.UnsafeHandler):
    def get(self):
        user = self.current_user

        ret = { 'user': None, 'email': None }
        if user:
            ret = { 'user': user.name, 'email': user.email }

        self.finish(ret)


class CountryList(handlers.UnsafeHandler):
    def get(self, *args, **kwargs):
        self.write({'countries': [{'name': c} for c in self.country_list()]})

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


class RequestAccess(handlers.SafeHandler):
    def get(self, dataset, *args, **kwargs):
        user = self.current_user
        name = user.name
        email = user.email

        logging.info("Request: " + name + ' ' + email)
        self.finish(json.dumps({'user':name, 'email':email}))

    def post(self, dataset, *args, **kwargs):
        dataset = db.get_dataset(dataset)

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
        logging.info("Inserting into database: {}, {}".format(user.name, user.email))

        try:
            with db.database.atomic():
                user.save() # Save to database
                (da,_) = db.DatasetAccess.get_or_create(
                        user    = user,
                        dataset = dataset
                    )
                da.wants_newsletter = newsletter
                da.save()
                db.UserAccessLog.create(
                        user = user,
                        dataset = dataset,
                        action = 'access_requested'
                    )
        except Exception as e:
            logging.error(e)


class LogEvent(handlers.SafeHandler):
    def post(self, dataset, event, target):
        user = self.current_user

        if event == 'consent':
            dv = (db.DatasetVersion
                    .select()
                    .where(db.DatasetVersion.version==target)
                    .get())
            db.UserConsentLog.create(
                    user = user,
                    dataset_version = dv,
                )
        else:
            raise tornado.web.HTTPError(400, reason="Can't log that")


class ApproveUser(handlers.AdminHandler):
    def post(self, dataset, email):
        with db.database.atomic():
            dataset = db.get_dataset(dataset)

            user = db.User.select().where(db.User.email == email).get()

            da = db.DatasetAccess.select().where(
                        db.DatasetAccess.user == user,
                        db.DatasetAccess.dataset == dataset
                ).get()
            da.has_access = True
            da.save()

            db.UserAccessLog.create(
                    user = user,
                    dataset = dataset,
                    action = 'access_granted'
                )

        msg = MIMEMultipart()
        msg['to'] = email
        msg['from'] = settings.from_address
        msg['subject'] = 'Swefreq access granted to {}'.format(dataset.short_name)
        msg.add_header('reply-to', settings.reply_to_address)
        body = """You now have access to the {} dataset

Please visit https://swefreq.nbis.se/dataset/{}/download to download files.
        """.format(dataset.full_name, dataset.short_name,
                dataset.study.contact_name)
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(settings.mail_server)
        server.sendmail(msg['from'], [msg['to']], msg.as_string())


class RevokeUser(handlers.AdminHandler):
    def post(self, dataset, email):
        with db.database.atomic():
            dataset = db.get_dataset(dataset)
            user = db.User.select().where(db.User.email == email).get()

            db.UserAccessLog.create(
                    user = user,
                    dataset = dataset,
                    action = 'access_revoked'
                )

class DatasetUsers():
    def _build_json_response(self, query, access_for):
        json_response = []
        for user in query:
            applyDate = '-'
            access = access_for(user)
            if not access:
                continue
            access = access[0]
            if access.access_requested:
                applyDate = access.access_requested.strftime('%Y-%m-%d')

            data = {
                    'user':        user.name,
                    'email':       user.email,
                    'affiliation': user.affiliation,
                    'country':     user.country,
                    'newsletter':  access.wants_newsletter,
                    'has_access':  access.has_access,
                    'applyDate':   applyDate
                }
            json_response.append(data)
        return json_response


class DatasetUsersPending(handlers.AdminHandler, DatasetUsers):
    def get(self, dataset, *args, **kwargs):
        dataset = db.get_dataset(dataset)
        users = db.User.select()
        access = (db.DatasetAccessPending
                   .select()
                   .where(
                       db.DatasetAccessPending.dataset == dataset,
                   ))
        query = peewee.prefetch(users, access)

        self.finish({'data': self._build_json_response(
            query, lambda u: u.access_pending_prefetch)})


class DatasetUsersCurrent(handlers.AdminHandler, DatasetUsers):
    def get(self, dataset, *args, **kwargs):
        dataset = db.get_dataset(dataset)
        users = db.User.select()
        access = (db.DatasetAccessCurrent
                   .select()
                   .where(
                       db.DatasetAccessCurrent.dataset == dataset,
                   ))
        query = peewee.prefetch(users, access)
        self.finish({'data': self._build_json_response(
            query, lambda u: u.access_current_prefetch)})


class ServeLogo(handlers.UnsafeHandler):
    def get(self, dataset, *args, **kwargs):
        try:
            logo_entry = db.DatasetLogo.select(
                    db.DatasetLogo
                ).join(
                    db.Dataset
                ).where(
                    db.Dataset.short_name == dataset
                ).get()
        except:
            self.send_error(status_code=404)
            return

        self.set_header("Content-Type", logo_entry.mimetype)
        self.write(logo_entry.data)
        self.finish()
