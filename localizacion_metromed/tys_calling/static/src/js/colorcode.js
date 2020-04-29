odoo.define('tys_calling.colorcode', function(require) {
"use strict";

var models = require('point_of_sale.models');
var screen_class = require('point_of_sale.screens');
var core = require('web.core');
var gui = require('point_of_sale.gui');
var popup_class = require('point_of_sale.popups');
var Model = require('web.DataModel');
var time = require('web.time');
var _t = core._t;
//    instance.web.list.columns.add('field.calling', 'instance.calling.color_code');
//    instance.calling.color_code = instance.web.list.Column.extend({
//        _format: function (row_data, options) {
//            res = this._super.apply(this, arguments);
//            var amount = res;
//            if (amount == 'complete'){
//                return "<font color='#ffa500'>"+(amount)+"</font>";
//            }
//            return res
//        }
//    });
//
//here you can add more widgets if you need, as above...
//
var _t = odoo.web._t;

odoo.web.list.Binary.include({
    placeholder: "/tys_calling/static/src/img/gtk-no.png",
    _format: function (row_data, options) {
        var value = row_data[this.id].value;
        var download_url;
        if (value && value.substr(0, 10).indexOf('complete') == -1) {
            download_url = "data:application/octet-stream;base64," + value;
        } else {
            download_url = this.placeholder;
        }
        alert('valor = ', download_url)
        return _.template("<img width='50' height='50' src='<%-href%>'/>", {
            href: download_url,
        });
    }

});
};