//  Copyright 2014 Rackspace, Inc.
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing,
//  software distributed under the License is distributed on an "AS
//  IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
//  express or implied. See the License for the specific language
//  governing permissions and limitations under the License.

/*
 *  ZeroVM on Swift (Zwift) client.
 */
function ZwiftClient(authUrl, tenant, username, password) {
    this._authUrl = authUrl;
    this._tenant = tenant;
    this._username = username;
    this._password = password;

    this._token = null;
    this._swiftUrl = null;
}

/*
 * Authenticate to Keystone. This will login to Keystone and obtain an
 * authentication token. Call this before calling other methods that
 * talk with Swift.
 *
 * If Keystone and Swift are served from differnet domains, you must
 * install a CORS (Cross-Origin Resource Sharing) middleware in Swift.
 * Otherwise the authentication requests made by this function wont be
 * allowed by the browser.
 */
ZwiftClient.prototype.auth = function (success) {
    var headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json'};
    var payload = {'auth':
                   {'tenantName': this._tenant,
                    'passwordCredentials':
                    {'username': this._username,
                     'password': this._password}}};
    var self = this;
    $.ajax({
        'type': 'POST',
        'url': this._authUrl + '/tokens',
        'data': JSON.stringify(payload),
        'cache': false,
        'success': function (data) {
            self._token = data.access.token.id;
            $.each(data.access.serviceCatalog, function (i, service) {
                if (service.name == 'swift') {
                    self._swiftUrl = service.endpoints[0].publicURL;
                    return false;  // break for-each loop
                }
            });
            (success || $.noop)();
        },
        'dataType': 'json',
        'contentType': 'application/json',
        'accepts': 'application/json'
    });
};

/*
 * Execute a job. The job description will be serialized as JSON and
 * sent to Swift. The "stdout" from the job, if any, will be passed to
 * the success callback function.
 */
ZwiftClient.prototype.execute = function (job, success) {
    var headers = {'X-Auth-Token': this._token,
                   'X-Zerovm-Execute': '1.0'}
    $.ajax({
        'type': 'POST',
        'url': this._swiftUrl,
        'data': JSON.stringify(job),
        'headers': headers,
        'cache': false,
        'success': (success || $.noop),
        'contentType': 'application/json',
    });
};

/*
 * Escape command line argument. Command line arguments in a job
 * description should be separated with spaces after being escaped
 * with this function.
 */
function escapeArg (value) {
    function hexencode (match) {
        return "\\x" + match.charCodeAt(0).toString(16)
    }
    return value.replace(/[\\", \n]/g, hexencode)
}
