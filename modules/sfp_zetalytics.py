# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         sfp_zetalytics
# Purpose:      Query Zetalytics database for hostname & subdomain information
#
# Author:      Leo Trubach <leotrubach@gmail.com>
#
# Created:     2020-04-21
# Copyright:   (c) Steve Micallef
# Licence:     MIT
# -------------------------------------------------------------------------------

import json
from urllib.parse import urlencode

from spiderfoot import SpiderFootEvent, SpiderFootPlugin


class sfp_zetalytics(SpiderFootPlugin):
    BASE_URL = "https://zonecruncher.com/api/v1"
    meta = {
        "name": "Zetalytics",
        "summary": "Query the Zetalytics database for hosts on your target domain(s).",
        'flags': ["apikey"],
        "useCases": ["Passive"],
        "categories": ["Passive DNS"],
        "dataSource": {
            "website": "https://zetalytics.com/",
            "model": "FREE_AUTH_LIMITED",
            "references": ["https://zonecruncher.com/api-v1-docs/"],
            "apiKeyInstructions": [
                "Visit https://mailchi.mp/zetalytics/trial-access-request",
                "Register a free account and request an API key",
            ],
            "favIcon": "https://zetalytics.com/favicon.ico",
            "logo": "https://zetalytics.com/assets/images/logo.png",
            "description": "Zetalytics database provides several useful endpoints to perform passive DNS analysis",
        },
    }

    opts = {"api_key": "", "verify": True}

    optdescs = {
        "api_key": "Zetalytics API Key.",
        "verify": "Verify that any hostnames found on the target domain still resolve?",
    }

    results = None
    errorState = False

    def setup(self, sfc, userOpts=None):
        self.sf = sfc
        self.results = self.tempStorage()
        if userOpts:
            self.opts.update(userOpts)

    def watchedEvents(self):
        return ["INTERNET_NAME", "DOMAIN_NAME", "EMAILADDR", "IP_ADDRESS"]

    def producedEvents(self):
        return ["INTERNET_NAME", "AFFILIATE_DOMAIN_NAME", "INTERNET_NAME_UNRESOLVED", "IP_ADDRESS"]

    def emit(self, etype, data, pevent):
        if self.checkForStop():
            return None
        evt = SpiderFootEvent(etype, data, self.__name__, pevent)
        self.notifyListeners(evt)
        return evt

    def verify_emit_internet_name(self, hostname, pevent):
        if f"INTERNET_NAME:{hostname}" in self.results:
            return False

        if not self.getTarget().matches(hostname):
            return False

        if self.opts["verify"] and not self.sf.resolveHost(hostname) and not self.sf.resolveHost6(hostname):
            self.debug(f"Host {hostname} could not be resolved")
            self.emit("INTERNET_NAME_UNRESOLVED", hostname, pevent)
            return True

        self.emit("INTERNET_NAME", hostname, pevent)
        if self.sf.isDomain(hostname, self.opts["_internettlds"]):
            self.emit("DOMAIN_NAME", hostname, pevent)

        return True

    def request(self, path, params):
        params = {**params, "token": self.opts["api_key"]}
        qs = urlencode(params)
        res = self.sf.fetchUrl(
            f"{self.BASE_URL}{path}/?{qs}",
            timeout=self.opts["_fetchtimeout"],
            useragent="SpiderFoot",
        )

        if res["content"] is None:
            self.info(f"No Zetalytics info found for {path}?{qs}")
            return None

        try:
            return json.loads(res["content"])
        except Exception as e:
            self.error(f"Error processing JSON response from Zetalytics: {e}")
        return None

    def query_subdomains(self, domain):
        return self.request("/subdomains", {"q": domain, "vvv": "true"})

    def query_hostname(self, hostname):
        return self.request("/hostname", {"q": hostname})

    def query_email_domain(self, email_domain):
        return self.request("/email_domain", {"q": email_domain})

    def query_email_address(self, email_address):
        return self.request("/email_address", {"q": email_address})

    def query_ns2domains(self, ns_domain):
        return self.request("/ns2domain", {"q": ns_domain})

    def query_cname2qname(self, q):
        return self.request("/cname2qname", {"q": q})

    def query_domain2d8s(self, q):
        return self.request("/domain2d8s", {"q": q})

    def query_domain2nsglue(self, q):
        return self.request("/domain2nsglue", {"q": q})

    def query_domain2whois(self, q):
        return self.request("/domain2whois", {"q": q})

    def query_domain2aaaa(self, q):
        return self.request("/domain2aaaa", {"q": q})

    def query_domain2cname(self, q):
        return self.request("/domain2cname", {"q": q})

    def query_domain2ip(self, q):
        return self.request("/domain2ip", {"q": q})

    def query_domain2mx(self, q):
        return self.request("/domain2mx", {"q": q})

    def query_domain2ns(self, q):
        """Query Zetalytics endpoint /domain2ns"""
        return self.request("/domain2ns", {"q": q})

    def query_domain2ptr(self, q):
        """Query Zetalytics endpoint /domain2ptr"""
        return self.request("/domain2ptr", {"q": q})

    def query_domain2rrtypes(self, q):
        """Query Zetalytics endpoint /domain2rrtypes"""
        return self.request("/domain2rrtypes", {"q": q})

    def query_domain2txt(self, q):
        """Query Zetalytics endpoint /domain2txt"""
        return self.request("/domain2txt", {"q": q})

    def query_domain_zone_activity(self, q):
        """Query Zetalytics endpoint /domain-zone-activity"""
        return self.request("/domain-zone-activity", {"q": q})

    def query_email_user(self, q):
        """Query Zetalytics endpoint /email_user"""
        return self.request("/email_user", {"q": q})

    def query_ip2nsglue(self, q):
        """Query Zetalytics endpoint /ip2nsglue"""
        return self.request("/ip2nsglue", {"q": q})

    def query_ip2pwhois(self, q):
        """Query Zetalytics endpoint /ip2pwhois"""
        return self.request("/ip2pwhois", {"q": q})

    def query_ip(self, q):
        """Query Zetalytics endpoint /ip"""
        return self.request("/ip", {"q": q})

    def query_liveDNS(self, q):
        """Query Zetalytics endpoint /liveDNS"""
        return self.request("/liveDNS", {"q": q})

    def query_mx2domain(self, q):
        """Query Zetalytics endpoint /mx2domain"""
        return self.request("/mx2domain", {"q": q})

    def query_ns_zone_activity(self, q):
        """Query Zetalytics endpoint /ns-zone-activity"""
        return self.request("/ns-zone-activity", {"q": q})

    def query_ns2domain(self, q):
        """Query Zetalytics endpoint /ns2domain"""
        return self.request("/ns2domain", {"q": q})


    def generate_subdomains_events(self, data, pevent):
        if not isinstance(data, dict):
            return False

        results = data.get("results", [])
        if not isinstance(results, list):
            return False

        events_generated = False
        for r in results:
            qname = r.get("qname")
            if not isinstance(qname, str):
                continue
            if self.verify_emit_internet_name(qname, pevent):
                events_generated = True

        return events_generated # noqa R504

    def generate_hostname_events(self, data, pevent):
        if not isinstance(data, dict):
            return False

        results = data.get("results")
        if not isinstance(results, list):
            return False

        hostnames = set()
        for r in results:
            qname = r.get("qname")
            if isinstance("qname", str):
                hostnames.add(qname)

        events_generated = False
        for hostname in hostnames:
            if self.verify_emit_internet_name(hostname, pevent):
                events_generated = True

        return events_generated # noqa R504

    def generate_email_events(self, data, pevent):
        if not isinstance(data, dict):
            return False

        results = data.get("results")
        if not isinstance(results, list):
            return False

        events_generated = False
        for r in results:
            domain = r.get("d")
            if isinstance(domain, str):
                self.emit("AFFILIATE_DOMAIN_NAME", domain, pevent)
                events_generated = True

        return events_generated # noqa R504

    def generate_email_domain_events(self, data, pevent):
        if not isinstance(data, dict):
            return False

        results = data.get("results")
        if not isinstance(results, list):
            return False

        events_generated = False
        for r in results:
            domain = r.get("d")
            if isinstance(domain, str):
                self.emit("AFFILIATE_DOMAIN_NAME", domain, pevent)
                events_generated = True

        return events_generated # noqa R504

    def handleEvent(self, event):
        eventName = event.eventType
        srcModuleName = event.module
        eventData = event.data

        if self.errorState:
            return

        if self.checkForStop():
            return

        self.debug(f"Received event, {eventName}, from {srcModuleName}")

        if self.opts["api_key"] == "":
            self.error(
                f"You enabled {self.__class__.__name__} but did not set an API key!"
            )
            self.errorState = True
            return

        if f"{eventName}:{eventData}" in self.results:
            self.debug(f"Skipping {eventName}:{eventData}, already checked.")
            return
        self.results[f"{eventName}:{eventData}"] = True

        if eventName == "INTERNET_NAME":
            data = self.query_hostname(eventData)
            if self.generate_hostname_events(data, event):
                self.emit("RAW_RIR_DATA", json.dumps(data), event)


        elif eventName == "DOMAIN_NAME":
            sd = self.query_subdomains(eventData)
            if sd and isinstance(sd.get("results"), list):
                for entry in sd["results"]:
                    self.emit("AFFILIATE_DOMAIN_NAME", entry['qname'], event)
                    for rec in entry.get("records", []):
                        if rec.get("rrtype") in ("a", "AAAA"):
                            ip = rec.get("value")
                            if isinstance(ip, str):
                                self.emit("IP_ADDRESS", ip, event)
                self.emit("RAW_RIR_DATA", json.dumps(sd), event)
            if self.generate_subdomains_events(sd, event):
                self.emit("RAW_RIR_DATA", json.dumps(sd), event)

            data = self.query_email_domain(eventData)
            if self.generate_email_domain_events(data, event):
                self.emit("RAW_RIR_DATA", json.dumps(data), event)
            ns_data = self.query_ns2domains(eventData)
            if ns_data and isinstance(ns_data.get("results"), list):
                for r in ns_data["results"]:
                    domain = r.get("domain")
                    if isinstance(domain, str) and domain != eventData:
                        self.emit("AFFILIATE_DOMAIN_NAME", domain, event)
                self.emit("RAW_RIR_DATA", json.dumps(ns_data), event)

            a_records = self.query_domain2ip(eventData)
            if a_records:
                self.emit("RAW_RIR_DATA", json.dumps(a_records), event)

            aaaa_records = self.query_domain2aaaa(eventData)
            if aaaa_records:
                self.emit("RAW_RIR_DATA", json.dumps(aaaa_records), event)

            mx_records = self.query_domain2mx(eventData)
            if mx_records:
                self.emit("RAW_RIR_DATA", json.dumps(mx_records), event)

            cname_records = self.query_domain2cname(eventData)
            if cname_records:
                self.emit("RAW_RIR_DATA", json.dumps(cname_records), event)

            whois_records = self.query_domain2whois(eventData)
            if whois_records:
                self.emit("RAW_RIR_DATA", json.dumps(whois_records), event)
                for r in whois_records.get("results", []):
                    email = r.get("response", {}).get("x", {}).get("owner")
                    if email:
                        self.emit("EMAILADDR", email, event)

            d8s_records = self.query_domain2d8s(eventData)
            if d8s_records:
                self.emit("RAW_RIR_DATA", json.dumps(d8s_records), event)

            glue_records = self.query_domain2nsglue(eventData)
            if glue_records:
                self.emit("RAW_RIR_DATA", json.dumps(glue_records), event)
        elif eventName == "IP_ADDRESS":
            ipnsglue = self.query_ip2nsglue(eventData)
            if ipnsglue:
                self.emit("RAW_RIR_DATA", json.dumps(ipnsglue), event)
            pwhois = self.query_ip2pwhois(eventData)
            if pwhois:
                self.emit("RAW_RIR_DATA", json.dumps(pwhois), event)
            ip = self.query_ip(eventData)
            if ip:
                if ip and isinstance(ip.get("results"), list):
                    for r in ip["results"]:
                        domain = r.get("qname")
                        if isinstance(domain, str) and domain != eventData:
                            self.emit("AFFILIATE_DOMAIN_NAME", domain, event)
                self.emit("RAW_RIR_DATA", json.dumps(ip), event)

        elif eventName == "EMAILADDR":
            data = self.query_email_address(eventData)
            if self.generate_email_events(data, event):
                self.emit("RAW_RIR_DATA", json.dumps(data), event)
