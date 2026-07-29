define(function (require, exports, module) {
    //初始化页面
    exports.initialize = function () {
        exports.initData();
        // this.loadEvents();
        exports.loadTemplateFun();
    };

    //模板方法
    exports.loadTemplateFun = function () {

        //模板内容html
        EM.template.config("escape", false);

        // 格式化日期
        EM.template.helper("formatDate", function (value, fmt, emptyValue) {
            return formatDate(value, fmt);
        });

        //格式化字符长度
        EM.template.helper("formatLength", function (txt) {
            if (txt != undefined && txt != "") {
                if (txt.length > 50) {
                    return txt.substr(0, 50) + "...";
                }
                else {
                    return txt;
                }
            }
            else {
                return "";
            }
        });
    };

    exports.loadEvents = function () {

    };

    //初始化数据
    exports.initData = function () {
        var url = "../ResearchReport/PageAjax";
        var data = {
            code: EM("#sCode123").val(),
            icode: EM("#hidIndustryCode").val()
        };
        EM.get(url, data, function (result) {
            if (typeof (result) == 'string') {
                result = {};
            }
            if (result) {
                result.type = $("#style_type123").val();
                result.color = $("#style_color123").val();

                result.iTop = (window.screen.availHeight - 500) / 2;       //获得窗口的垂直位置;
                result.iLeft = (window.screen.availWidth - 860) / 2;           //获得窗口的水平位置;


                //绑定数据
                var resultHtml = EM.template("tmpl", result);
                document.getElementById("templateDiv").innerHTML = resultHtml;
                AutoScroll();
                //移除模板
                document.getElementById("tmpl").parentElement.removeChild(document.getElementById("tmpl"));
            }
        });
    };

    //初始化
    exports.initialize();
});