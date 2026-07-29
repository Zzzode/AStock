define(function (require, exports, module) {
    var style = document.getElementById("style_type123").value;
    var color = document.getElementById("style_color123").value;
    //初始化页面
    exports.initialize = function () {
        exports.loadTemplateFun();
        exports.initData();
        // this.loadEvents();
    };

    exports.loadTemplateFun = function () {

        // 格式化字符串
        EM.template.helper("formatStr", function (value, emptyValue) {
            return formatStr(value, emptyValue);
        });

        // 格式化日期
        EM.template.helper("formatDate", function (value, fmt, emptyValue) {
            return formatDate(value, fmt);
        });

        // 格式化保留小数
        EM.template.helper("formatFixed", function (value, digit, emptyValue) {
            if (!digit && digit != 0) {
                digit = 2;
            }
            return toFixed(value, digit, emptyValue);
        });

        // 格式化金额
        EM.template.helper("formatMoney", function (value, emptyValue) {
            return formatMoney(value, emptyValue);
        });

        // 预测统计，最新年份
        EM.template.helper("getYears", function (list) {
            var years = [];
            for (var i = 0; i < list.length; i++) {
                if (list[i].YEAR_MARK == 'A') {
                    years.push(list[i].YEAR);
                }
            }
            return years.join('、');
        });

        // 拼接字符串
        EM.template.helper("compactStr", function (str1, str2, emptyValue) {
            if (emptyValue == undefined || emptyValue == null) {
                emptyValue = '--';
            }

            if (str1 && str2) {
                return str1 + str2;
            } else if (str1) {
                return str1;
            } else if (str2) {
                return str2;
            }

            return emptyValue;
        });

    }

    //加载事件
    exports.loadEvents = function () {

        //预测明细，每股收益
        EM("#lycmx_mgsy").click(function () {
            EM(this).siblings().removeClass("current");
            EM(this).addClass("current");

            EM("#ycmx_mgsy").show();
            EM("#ycmx_jlr").hide();
        });

        //预测明细，净利润
        EM("#lycmx_jlr").click(function () {
            EM(this).siblings().removeClass("current");
            EM(this).addClass("current");

            EM("#ycmx_mgsy").hide();
            EM("#ycmx_jlr").show();
        });
    }

    //function,格式化图表分割数据
    exports.formatChartMinOrMax = function (value, splitNumber) {
        if (value == 0)
            return value;

        if (Math.abs(value) >= splitNumber) {
            value = value > 0 ? Math.ceil(value / splitNumber) * splitNumber : Math.floor(value / splitNumber) * splitNumber;
        }
        else {
            var key = 10;
            while (Math.abs(value * key) < splitNumber) {
                key = key * key;
            }
            value = value > 0 ? Math.ceil(value * key / splitNumber) * splitNumber / key : Math.floor(value * key / splitNumber) * splitNumber / key;
        }
        return value;
    };

    //机构预测，每股收益Chart
    exports.jgycmgsyChart = function (data) {

        if (!data || data.length == 0 || document.getElementById('jgycmgsyChart') == null)
            return;

        // 基于准备好的dom，初始化echarts实例
        var myChart;
        if (color.toLowerCase() == "w") {
            myChart = echarts.init(document.getElementById('jgycmgsyChart'), white);
        }
        else {
            myChart = echarts.init(document.getElementById('jgycmgsyChart'), black);
        }
        var xData = [];
        var barData = [];
        var lineData = [];
        var splitNumber = 5;
        var barMin = 0;
        var barMax = 0;
        var lineMin = 0;
        var lineMax = 0;
        var value = 0;
        for (var i = 0; i < data.length; i++) {
            var temp = toFixed(data[i].EPS, 2, '-');

            xData.push(data[i].YEAR + data[i].YEAR_MARK);
            barData.push(temp);
            value = Number(temp);
            if (value < barMin)
                barMin = value;
            if (value > barMax)
                barMax = value;

            temp = toFixed(data[i].EPS_RATIO, 2, '-');
            lineData.push(temp);
            value = Number(temp);
            if (value < lineMin)
                lineMin = value;
            if (value > lineMax)
                lineMax = value;
        }
        barMin = exports.formatChartMinOrMax(barMin, splitNumber);
        barMax = exports.formatChartMinOrMax(barMax, splitNumber);
        lineMin = exports.formatChartMinOrMax(lineMin, splitNumber);
        lineMax = exports.formatChartMinOrMax(lineMax, splitNumber);

        // 指定图表的配置项和数据
        var option = {
            tooltip: {
                trigger: "axis",
                formatter: function (params) {
                    var str = "";
                    for (var i = 0; i < params.length; i++) {
                        if (i == 0) {
                            str += params[params.length - 1].name + "<br/>";
                            str += "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:" + params[i].color
                            + ";'></span>" + params[i].seriesName + "：" + (params[i].value ? params[i].value : "-") + "元<br/>";
                        }
                        else {
                            str += "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:" + params[i].color
                            + ";'></span>" + params[i].seriesName + "：" + params[i].value + (params[i].value != "-" ? "%" : "") + "<br/>";
                        }
                    }
                    return str;
                }
            },
            legend: {
                left: 'center',
                bottom: '15',
                data: ['每股收益', {
                    name: '每股收益增长',
                    icon: 'line'
                }]
            },
            grid: {
                x: 40,
                y: 20,
                x2: 45,
                y2: 70
            },
            xAxis: {
                type: 'category',
                position: 'buttom',
                data: xData,
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                axisTick: {
                    alignWithLabel: true
                }
            },
            yAxis: [{
                type: 'value',
                position: 'left',
                min: barMin,
                max: barMax,
                interval: Number(((barMax - barMin) / splitNumber).toFixed(2)),
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            }, {
                type: 'value',
                position: 'right',
                min: lineMin,
                max: lineMax,
                interval: Number(((lineMax - lineMin) / splitNumber).toFixed(2)),
                axisLabel: {
                    formatter: function (value, index) {
                        return value + "%";
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            }],
            series: [{
                name: '每股收益',
                type: 'bar',
                yAxisIndex: 0,
                barWidth: '50%',
                itemStyle: {
                    normal: {
                        color: 'rgb(191,102,29)'
                    }
                },
                data: barData
            }, {
                name: '每股收益增长',
                type: 'line',
                yAxisIndex: 1,
                itemStyle: {
                    normal: {
                        color: '#ff0000'
                    }
                },
                data: lineData
            }]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    };

    //机构预测，市盈率Chart
    exports.jgycsylChart = function (data) {

        if (!data || data.length == 0 || document.getElementById('jgycsylChart') == null)
            return 0;

        // 基于准备好的dom，初始化echarts实例
        var myChart;
        if (color.toLowerCase() == "w") {
            myChart = echarts.init(document.getElementById('jgycsylChart'), white);
        }
        else {
            myChart = echarts.init(document.getElementById('jgycsylChart'), black);
        }
        var xData = [];
        var seriesData = [];
        for (var i = 0; i < data.length; i++) {
            var temp = data[i];
            xData.push(temp.YEAR + temp.YEAR_MARK);
            seriesData.push(toFixed(temp.PE, 2, '-'));
        }

        // 指定图表的配置项和数据
        var option = {
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                left: 'center',
                bottom: '15',
                data: ['市盈率']
            },
            grid: {
                x: 40,
                y: 20,
                x2: 20,
                y2: 70
            },
            xAxis: {
                type: 'category',
                position: 'buttom',
                data: xData,
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                axisTick: {
                    alignWithLabel: true
                }
            },
            yAxis: {
                type: 'value',
                position: 'left',
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            },
            series: {
                name: '市盈率',
                type: 'bar',
                barWidth: '50%',
                itemStyle: {
                    normal: {
                        color: 'rgb(191,102,29)'
                    }
                },
                data: seriesData
            }
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    };

    //预测统计，净资产收益率Chart
    exports.jzcsylChart = function (data) {

        if (!data || data.length == 0)
            return;

        // 基于准备好的dom，初始化echarts实例
        var myChart;
        if (color.toLowerCase() == "w") {
            myChart = echarts.init(document.getElementById('jzcsylChart'), white);
        }
        else {
            myChart = echarts.init(document.getElementById('jzcsylChart'), black);
        }
        var xData = [];
        var barData = [];
        var lineData = [];
        for (var i = 0; i < data.length; i++) {
            var temp = data[i];
            xData.push(temp.YEAR + temp.YEAR_MARK);
            barData.push(toFixed(temp.ROE, 2, '-'));
        }

        // 指定图表的配置项和数据
        var option = {
            tooltip: {
                trigger: "axis",
                formatter: function (params) {
                    var str = "";
                    for (var i = 0; i < params.length; i++) {
                        if (i == 0) {
                            str += params[params.length - 1].name + "<br/>";
                        }
                        str += "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:" + params[i].color
                        + ";'></span>" + params[i].seriesName + "：" + params[i].value + (params[i].value != "-" ? "%" : "") + "<br/>";
                    }
                    return str;
                }
            },
            legend: {
                left: 'center',
                bottom: '15',
                data: ['净资产收益率']
            },
            grid: {
                x: 40,
                y: 20,
                x2: 45,
                y2: 70
            },
            xAxis: {
                type: 'category',
                position: 'buttom',
                data: xData,
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                axisTick: {
                    alignWithLabel: true
                }
            },
            yAxis: {
                type: 'value',
                position: 'left',
                axisLabel: {
                    formatter: function (value, index) {
                        return value + "%";
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            },
            series: {
                name: '净资产收益率',
                type: 'bar',
                yAxisIndex: 0,
                barWidth: '50%',
                itemStyle: {
                    normal: {
                        color: 'rgb(191,102,29)'
                    }
                },
                data: barData
            }
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    };

    //预测统计，归属净利润Chart
    exports.gsjlrChart = function (data) {

        if (!data || data.length == 0)
            return;

        // 基于准备好的dom，初始化echarts实例
        var myChart;
        if (color.toLowerCase() == "w") {
            myChart = echarts.init(document.getElementById('gsjlrChart'), white);
        }
        else {
            myChart = echarts.init(document.getElementById('gsjlrChart'), black);
        }
        var xData = [];
        var barData = [];
        var lineData = [];
        var splitNumber = 5;
        var barMin = 0;
        var barMax = 0;
        var lineMin = 0;
        var lineMax = 0;
        var value = 0;
        for (var i = 0; i < data.length; i++) {
            var temp = data[i];
            xData.push(temp.YEAR + temp.YEAR_MARK);

            value = toFixed(temp.PARENT_NETPROFIT / 1e8, 2, '-');
            barData.push(value);
            if (value != "-") {
                value = Number(value);
                if (value < barMin)
                    barMin = value;
                if (value > barMax)
                    barMax = value;
            }

            value = toFixed(temp.PARENT_NETPROFIT_RATIO, 2, '-');
            lineData.push(value);
            if (value != '-') {
                value = Number(value);
                if (value < lineMin)
                    lineMin = value;
                if (value > lineMax)
                    lineMax = value;
            }
        }
        barMin = exports.formatChartMinOrMax(barMin, splitNumber);
        barMax = exports.formatChartMinOrMax(barMax, splitNumber);
        lineMin = exports.formatChartMinOrMax(lineMin, splitNumber);
        lineMax = exports.formatChartMinOrMax(lineMax, splitNumber);

        // 指定图表的配置项和数据
        var option = {
            tooltip: {
                trigger: "axis",
                formatter: function (params) {
                    var str = "";
                    for (var i = 0; i < params.length; i++) {
                        if (i == 0) {
                            str += params[params.length - 1].name + "<br/>";
                            str += "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:" + params[i].color
                            + ";'></span>" + params[i].seriesName + "：" + (params[i].value ? params[i].value : "-") + "亿元<br/>";
                        }
                        else {
                            str += "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:" + params[i].color
                            + ";'></span>" + params[i].seriesName + "：" + params[i].value + (params[i].value != "-" ? "%" : "") + "<br/>";
                        }
                    }
                    return str;
                }
            },
            legend: {
                left: 'center',
                bottom: '15',
                data: ['归属净利润', {
                    name: '增长',
                    icon: 'line'
                }]
            },
            grid: {
                x: 40,
                y: 20,
                x2: 45,
                y2: 70
            },
            xAxis: {
                type: 'category',
                position: 'buttom',
                data: xData,
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                axisTick: {
                    alignWithLabel: true
                }
            },
            yAxis: [{
                type: 'value',
                position: 'left',
                min: barMin,
                max: barMax,
                interval: Number(((barMax - barMin) / splitNumber).toFixed(2)),
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            }, {
                type: 'value',
                position: 'right',
                min: lineMin,
                max: lineMax,
                interval: Number(((lineMax - lineMin) / splitNumber).toFixed(2)),
                axisLabel: {
                    formatter: function (value, index) {
                        return value + "%";
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            }],
            series: [{
                name: '归属净利润',
                type: 'bar',
                yAxisIndex: 0,
                barWidth: '50%',
                itemStyle: {
                    normal: {
                        color: 'rgb(191,102,29)'
                    }
                },
                data: barData
            }, {
                name: '增长',
                type: 'line',
                yAxisIndex: 1,
                itemStyle: {
                    normal: {
                        color: '#ff0000'
                    }
                },
                data: lineData
            }]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    };

    //预测统计，营业收入Chart
    exports.yysrChart = function (data) {

        if (!data || data.length == 0)
            return;

        // 基于准备好的dom，初始化echarts实例
        var myChart;
        if (color.toLowerCase() == "w") {
            myChart = echarts.init(document.getElementById('yysrChart'), white);
        }
        else {
            myChart = echarts.init(document.getElementById('yysrChart'), black);
        }

        var xData = [];
        var barData = [];
        var lineData = [];
        var splitNumber = 5;
        var barMin = 0;
        var barMax = 0;
        var lineMin = 0;
        var lineMax = 0;
        var value = 0;
        for (var i = 0; i < data.length; i++) {
            var temp = data[i];
            xData.push(temp.YEAR + temp.YEAR_MARK);

            value = toFixed(temp.TOTAL_OPERATE_INCOME / 1e8, 2, '-');
            barData.push(value);
            if (value != "-") {
                value = Number(value);
                if (value < barMin)
                    barMin = value;
                if (value > barMax)
                    barMax = value;
            }

            value = toFixed(temp.TOTAL_OPERATE_INCOME_RATIO, 2, '-');
            lineData.push(value);
            if (value != '-') {
                value = Number(value);
                if (value < lineMin)
                    lineMin = value;
                if (value > lineMax)
                    lineMax = value;
            }
        }
        barMin = exports.formatChartMinOrMax(barMin, splitNumber);
        barMax = exports.formatChartMinOrMax(barMax, splitNumber);
        lineMin = exports.formatChartMinOrMax(lineMin, splitNumber);
        lineMax = exports.formatChartMinOrMax(lineMax, splitNumber);


        // 指定图表的配置项和数据
        var option = {
            tooltip: {
                trigger: "axis",
                formatter: function (params) {
                    var str = "";
                    for (var i = 0; i < params.length; i++) {
                        if (i == 0) {
                            str += params[params.length - 1].name + "<br/>";
                            str += "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:" + params[i].color
                            + ";'></span>" + params[i].seriesName + "：" + (params[i].value ? params[i].value : "-") + "亿元<br/>";
                        }
                        else {
                            str += "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:" + params[i].color
                            + ";'></span>" + params[i].seriesName + "：" + params[i].value + (params[i].value != "-" ? "%" : "") + "<br/>";
                        }
                    }
                    return str;
                }
            },
            legend: {
                left: 'center',
                bottom: '15',
                data: ['营业收入', {
                    name: '营业收入增长',
                    icon: 'line'
                }]
            },
            grid: {
                x: 40,
                y: 20,
                x2: 45,
                y2: 70
            },
            xAxis: {
                type: 'category',
                position: 'buttom',
                data: xData,
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                axisTick: {
                    alignWithLabel: true
                }
            },
            yAxis: [{
                type: 'value',
                position: 'left',
                min: barMin,
                max: barMax,
                interval: Number(((barMax - barMin) / splitNumber).toFixed(2)),
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            }, {
                type: 'value',
                position: 'right',
                min: lineMin,
                max: lineMax,
                interval: Number(((lineMax - lineMin) / splitNumber).toFixed(2)),
                axisLabel: {
                    formatter: function (value, index) {
                        return value + "%";
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid'
                    }
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            }],
            series: [{
                name: '营业收入',
                type: 'bar',
                yAxisIndex: 0,
                barWidth: '50%',
                itemStyle: {
                    normal: {
                        color: 'rgb(191,102,29)'
                    }
                },
                data: barData
            }, {
                name: '营业收入增长',
                type: 'line',
                yAxisIndex: 1,
                itemStyle: {
                    normal: {
                        color: '#ff0000'
                    }
                },
                data: lineData
            }]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    };

    //初始化数据
    exports.initData = function () {
        var url = "../ProfitForecast/PageAjax";
        var data = {
            code: EM("#sCode123").val()
        }
        EM.get(url, data, function (result) {
            if (typeof (result) == 'string') {
                result = {};
            }

            //绑定数据
            var resultHtml = EM.template("tmpl", result);
            document.getElementById("templateDiv").innerHTML = resultHtml;
            AutoScroll();
            //移除模板
            document.getElementById("tmpl").parentElement.removeChild(document.getElementById("tmpl"));

            //机构预测，每股收益Chart
            exports.jgycmgsyChart(result.yctj_chart);
            //机构预测，市盈率Chart
            exports.jgycsylChart(result.yctj_chart);

            //预测统计，净资产收益率Chart
            exports.jzcsylChart(result.yctj_chart);
            //预测统计，归属净利润Chart
            exports.gsjlrChart(result.yctj_chart);
            //预测统计，营业收入Chart
            exports.yysrChart(result.yctj_chart);

            //绑定事件
            exports.loadEvents();
        });
    }
    //初始化
    exports.initialize();
});