!(function (t, e) {
    "use strict";
    "object" == typeof module && module.exports ? (module.exports = e(require("moment"))) : "function" == typeof define && define.amd ? define(["moment"], e) : e(t.moment);
})(this, function (i) {
    "use strict";
    var e,
        s = {},
        f = {},
        u = {},
        a = {},
        c = {};
    (i && "string" == typeof i.version) || D("Moment Timezone requires Moment.js. See https://momentjs.com/timezone/docs/#/use-it/browser/");
    var t = i.version.split("."),
        n = +t[0],
        o = +t[1];
    function l(t) {
        return 96 < t ? t - 87 : 64 < t ? t - 29 : t - 48;
    }
    function r(t) {
        var e = 0,
            n = t.split("."),
            o = n[0],
            r = n[1] || "",
            i = 1,
            s = 0,
            f = 1;
        for (45 === t.charCodeAt(0) && (f = -(e = 1)); e < o.length; e++) s = 60 * s + l(o.charCodeAt(e));
        for (e = 0; e < r.length; e++) (i /= 60), (s += l(r.charCodeAt(e)) * i);
        return s * f;
    }
    function h(t) {
        for (var e = 0; e < t.length; e++) t[e] = r(t[e]);
    }
    function p(t, e) {
        var n,
            o = [];
        for (n = 0; n < e.length; n++) o[n] = t[e[n]];
        return o;
    }
    function m(t) {
        var e = t.split("|"),
            n = e[2].split(" "),
            o = e[3].split(""),
            r = e[4].split(" ");
        return (
            h(n),
            h(o),
            h(r),
            (function (t, e) {
                for (var n = 0; n < e; n++) t[n] = Math.round((t[n - 1] || 0) + 6e4 * t[n]);
                t[e - 1] = 1 / 0;
            })(r, o.length),
            { name: e[0], abbrs: p(e[1].split(" "), o), offsets: p(n, o), untils: r, population: 0 | e[5] }
        );
    }
    function d(t) {
        t && this._set(m(t));
    }
    function z(t, e) {
        (this.name = t), (this.zones = e);
    }
    function v(t) {
        var e = t.toTimeString(),
            n = e.match(/\([a-z ]+\)/i);
        "GMT" === (n = n && n[0] ? ((n = n[0].match(/[A-Z]/g)) ? n.join("") : void 0) : (n = e.match(/[A-Z]{3,5}/g)) ? n[0] : void 0) && (n = void 0), (this.at = +t), (this.abbr = n), (this.offset = t.getTimezoneOffset());
    }
    function b(t) {
        (this.zone = t), (this.offsetScore = 0), (this.abbrScore = 0);
    }
    function g(t, e) {
        for (var n, o; (o = 6e4 * (((e.at - t.at) / 12e4) | 0)); ) (n = new v(new Date(t.at + o))).offset === t.offset ? (t = n) : (e = n);
        return t;
    }
    function _(t, e) {
        return t.offsetScore !== e.offsetScore
            ? t.offsetScore - e.offsetScore
            : t.abbrScore !== e.abbrScore
            ? t.abbrScore - e.abbrScore
            : t.zone.population !== e.zone.population
            ? e.zone.population - t.zone.population
            : e.zone.name.localeCompare(t.zone.name);
    }
    function w(t, e) {
        var n, o;
        for (h(e), n = 0; n < e.length; n++) (o = e[n]), (c[o] = c[o] || {}), (c[o][t] = !0);
    }
    function y() {
        try {
            var t = Intl.DateTimeFormat().resolvedOptions().timeZone;
            if (t && 3 < t.length) {
                var e = a[O(t)];
                if (e) return e;
                D("Moment Timezone found " + t + " from the Intl api, but did not have that data loaded.");
            }
        } catch (t) {}
        var n,
            o,
            r,
            i = (function () {
                var t,
                    e,
                    n,
                    o = new Date().getFullYear() - 2,
                    r = new v(new Date(o, 0, 1)),
                    i = [r];
                for (n = 1; n < 48; n++) (e = new v(new Date(o, n, 1))).offset !== r.offset && ((t = g(r, e)), i.push(t), i.push(new v(new Date(t.at + 6e4)))), (r = e);
                for (n = 0; n < 4; n++) i.push(new v(new Date(o + n, 0, 1))), i.push(new v(new Date(o + n, 6, 1)));
                return i;
            })(),
            s = i.length,
            f = (function (t) {
                var e,
                    n,
                    o,
                    r = t.length,
                    i = {},
                    s = [];
                for (e = 0; e < r; e++) for (n in (o = c[t[e].offset] || {})) o.hasOwnProperty(n) && (i[n] = !0);
                for (e in i) i.hasOwnProperty(e) && s.push(a[e]);
                return s;
            })(i),
            u = [];
        for (o = 0; o < f.length; o++) {
            for (n = new b(M(f[o]), s), r = 0; r < s; r++) n.scoreOffsetAt(i[r]);
            u.push(n);
        }
        return u.sort(_), 0 < u.length ? u[0].zone.name : void 0;
    }
    function O(t) {
        return (t || "").toLowerCase().replace(/\//g, "_");
    }
    function S(t) {
        var e, n, o, r;
        for ("string" == typeof t && (t = [t]), e = 0; e < t.length; e++) (r = O((n = (o = t[e].split("|"))[0]))), (s[r] = t[e]), (a[r] = n), w(r, o[2].split(" "));
    }
    function M(t, e) {
        t = O(t);
        var n,
            o = s[t];
        return o instanceof d ? o : "string" == typeof o ? ((o = new d(o)), (s[t] = o)) : f[t] && e !== M && (n = M(f[t], M)) ? ((o = s[t] = new d())._set(n), (o.name = a[t]), o) : null;
    }
    function j(t) {
        var e, n, o, r;
        for ("string" == typeof t && (t = [t]), e = 0; e < t.length; e++) (o = O((n = t[e].split("|"))[0])), (r = O(n[1])), (f[o] = r), (a[o] = n[0]), (f[r] = o), (a[r] = n[1]);
    }
    function A(t) {
        var e = "X" === t._f || "x" === t._f;
        return !(!t._a || void 0 !== t._tzm || e);
    }
    function D(t) {
        "undefined" != typeof console && "function" == typeof console.error && console.error(t);
    }
    function T(t) {
        var e = Array.prototype.slice.call(arguments, 0, -1),
            n = arguments[arguments.length - 1],
            o = M(n),
            r = i.utc.apply(null, e);
        return o && !i.isMoment(t) && A(r) && r.add(o.parse(r), "minutes"), r.tz(n), r;
    }
    (n < 2 || (2 == n && o < 6)) && D("Moment Timezone requires Moment.js >= 2.6.0. You are using Moment.js " + i.version + ". See momentjs.com"),
        (d.prototype = {
            _set: function (t) {
                (this.name = t.name), (this.abbrs = t.abbrs), (this.untils = t.untils), (this.offsets = t.offsets), (this.population = t.population);
            },
            _index: function (t) {
                var e,
                    n = +t,
                    o = this.untils;
                for (e = 0; e < o.length; e++) if (n < o[e]) return e;
            },
            countries: function () {
                var e = this.name;
                return Object.keys(u).filter(function (t) {
                    return -1 !== u[t].zones.indexOf(e);
                });
            },
            parse: function (t) {
                var e,
                    n,
                    o,
                    r,
                    i = +t,
                    s = this.offsets,
                    f = this.untils,
                    u = f.length - 1;
                for (r = 0; r < u; r++) if (((e = s[r]), (n = s[r + 1]), (o = s[r ? r - 1 : r]), e < n && T.moveAmbiguousForward ? (e = n) : o < e && T.moveInvalidForward && (e = o), i < f[r] - 6e4 * e)) return s[r];
                return s[u];
            },
            abbr: function (t) {
                return this.abbrs[this._index(t)];
            },
            offset: function (t) {
                return D("zone.offset has been deprecated in favor of zone.utcOffset"), this.offsets[this._index(t)];
            },
            utcOffset: function (t) {
                return this.offsets[this._index(t)];
            },
        }),
        (b.prototype.scoreOffsetAt = function (t) {
            (this.offsetScore += Math.abs(this.zone.utcOffset(t.at) - t.offset)), this.zone.abbr(t.at).replace(/[^A-Z]/g, "") !== t.abbr && this.abbrScore++;
        }),
        (T.version = "0.5.28"),
        (T.dataVersion = ""),
        (T._zones = s),
        (T._links = f),
        (T._names = a),
        (T._countries = u),
        (T.add = S),
        (T.link = j),
        (T.load = function (t) {
            S(t.zones),
                j(t.links),
                (function (t) {
                    var e, n, o, r;
                    if (t && t.length) for (e = 0; e < t.length; e++) (n = (r = t[e].split("|"))[0].toUpperCase()), (o = r[1].split(" ")), (u[n] = new z(n, o));
                })(t.countries),
                (T.dataVersion = t.version);
        }),
        (T.zone = M),
        (T.zoneExists = function t(e) {
            return t.didShowError || ((t.didShowError = !0), D("moment.tz.zoneExists('" + e + "') has been deprecated in favor of !moment.tz.zone('" + e + "')")), !!M(e);
        }),
        (T.guess = function (t) {
            return (e && !t) || (e = y()), e;
        }),
        (T.names = function () {
            var t,
                e = [];
            for (t in a) a.hasOwnProperty(t) && (s[t] || s[f[t]]) && a[t] && e.push(a[t]);
            return e.sort();
        }),
        (T.Zone = d),
        (T.unpack = m),
        (T.unpackBase60 = r),
        (T.needsOffset = A),
        (T.moveInvalidForward = !0),
        (T.moveAmbiguousForward = !1),
        (T.countries = function () {
            return Object.keys(u);
        }),
        (T.zonesForCountry = function (t, e) {
            if (
                !(t = (function (t) {
                    return (t = t.toUpperCase()), u[t] || null;
                })(t))
            )
                return null;
            var n = t.zones.sort();
            return e
                ? n.map(function (t) {
                      return { name: t, offset: M(t).utcOffset(new Date()) };
                  })
                : n;
        });
    var x,
        C = i.fn;
    function Z(t) {
        return function () {
            return this._z ? this._z.abbr(this) : t.call(this);
        };
    }
    function k(t) {
        return function () {
            return (this._z = null), t.apply(this, arguments);
        };
    }
    (i.tz = T),
        (i.defaultZone = null),
        (i.updateOffset = function (t, e) {
            var n,
                o = i.defaultZone;
            if ((void 0 === t._z && (o && A(t) && !t._isUTC && ((t._d = i.utc(t._a)._d), t.utc().add(o.parse(t), "minutes")), (t._z = o)), t._z))
                if (((n = t._z.utcOffset(t)), Math.abs(n) < 16 && (n /= 60), void 0 !== t.utcOffset)) {
                    var r = t._z;
                    t.utcOffset(-n, e), (t._z = r);
                } else t.zone(n, e);
        }),
        (C.tz = function (t, e) {
            if (t) {
                if ("string" != typeof t) throw new Error("Time zone name must be a string, got " + t + " [" + typeof t + "]");
                return (this._z = M(t)), this._z ? i.updateOffset(this, e) : D("Moment Timezone has no data for " + t + ". See http://momentjs.com/timezone/docs/#/data-loading/."), this;
            }
            if (this._z) return this._z.name;
        }),
        (C.zoneName = Z(C.zoneName)),
        (C.zoneAbbr = Z(C.zoneAbbr)),
        (C.utc = k(C.utc)),
        (C.local = k(C.local)),
        (C.utcOffset =
            ((x = C.utcOffset),
            function () {
                return 0 < arguments.length && (this._z = null), x.apply(this, arguments);
            })),
        (i.tz.setDefault = function (t) {
            return (n < 2 || (2 == n && o < 9)) && D("Moment Timezone setDefault() requires Moment.js >= 2.9.0. You are using Moment.js " + i.version + "."), (i.defaultZone = t ? M(t) : null), i;
        });
    var F = i.momentProperties;
    return "[object Array]" === Object.prototype.toString.call(F) ? (F.push("_z"), F.push("_a")) : F && (F._z = null), i;
});
