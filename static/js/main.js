$(document).ready(function() {

    // Scroll to sections from main menu
    $('.header-menu a[href^=\\#]').click(function(e) {
        e.preventDefault();
        $('html, body').animate({scrollTop:$(this.hash).offset().top}, 2000);
    });

    // Modal countdown coundown
    $('.fixed-promotion-close').click(function(e) {
        e.stopPropagation();
        $(this).parents('.fixed-promotion').fadeOut();
    });

    $('.fixed-promotion').click(function(e) {
        $('html, body').animate({scrollTop:$('#promotion').offset().top - 85}, 2000);
        $(this).fadeOut();
    });

    // Hamburger menu button
    $('.hamburger').click(function() {
        $(this).toggleClass('active');
        $('.header-menu').slideToggle();
    });

    // Languages button
    $('.languages-button').click(function() {
        $('.languages-list').slideToggle();
    });

    // Change showcase text
    var showcaseParagraphs = $(".showcase-content p");
    var showcaseParagraphIndex = -1;

    function showShowcaseParagraphs() {
        ++showcaseParagraphIndex;
        showcaseParagraphs.eq(showcaseParagraphIndex % showcaseParagraphs.length)
            .fadeIn(2000)
            .delay(30000)
            .fadeOut(2000, showShowcaseParagraphs);
    }

    showShowcaseParagraphs();

    // Tabs
    $('.tabs-navigation a').click(function(e) {
        e.preventDefault();
        $(this).parents('.tabs-navigation').find('a').removeClass('active');
        $(this).addClass('active');
        var targetId = $(this).attr('href');
        $(this).parents('.tabs-navigation').next('.tabs-content').find('.tab').removeClass('active');
        $(this).parents('.tabs-navigation').next('.tabs-content').find(targetId).addClass('active');

        if ($('.tab.active').find('.state-table').length) {
            $('.state-table table').DataTable().draw();
        };
    });

    // Pyramid hover
    function hoverPyramid(element1, element2) {
        $(element1).hover(
            function() {
                $(element2).css('opacity', '1');
            },
            function() {
                $(element2).css('opacity', '0');
            }
        );
    };

    hoverPyramid('.pyramid-description-1', '.pyramid-side-1');
    hoverPyramid('.pyramid-description-2', '.pyramid-side-2');
    hoverPyramid('.pyramid-description-3', '.pyramid-side-3');
    hoverPyramid('.pyramid-description-4', '.pyramid-side-4');
    hoverPyramid('.pyramid-description-5', '.pyramid-side-3, .pyramid-side-4');

    // Faq section
    $('.faq-question').click(function() {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            $(this).next().slideUp();
        } else if (!$(this).hasClass('active')) {
            $('.faq-question').removeClass('active');
            $('.faq-answer').slideUp();
            $(this).addClass('active');
            $(this).next().slideDown();
        };
    });

    // Timer
    var targetDate = new Date('2018/11/19 18:00:00');
    var targetTimeSeconds = (targetDate.getTime() - Date.now()) / 1000;

    $('.countdown').ClassyCountdown({
        end: $.now() + targetTimeSeconds,
        labelsOptions: {
            lang: {
                days: 'Дней',
                hours: 'Часов',
                minutes: 'Мин',
                seconds: 'Сек'
            }
        },
        style: {
            days: {
                gauge: {
                    thickness: 0.05,
                    bgColor: "#8dc5f9",
                    fgColor: "#dbed59"
                }
            },
            hours: {
                gauge: {
                    thickness: 0.05,
                    bgColor: "#8dc5f9",
                    fgColor: "#dbed59"
                }
            },
            minutes: {
                gauge: {
                    thickness: 0.05,
                    bgColor: "#8dc5f9",
                    fgColor: "#dbed59"
                }
            },
            seconds: {
                gauge: {
                    thickness: 0.05,
                    bgColor: "#8dc5f9",
                    fgColor: "#dbed59"
                }
            }
        },
        onEndCallback: function () {
            console.log('timer stopped');
        }
    });

    // Sorting data in table
    $('.state-table table').DataTable({
        "initComplete": function() {
            var ps = new PerfectScrollbar('.dataTables_scrollBody', {
                minScrollbarLength: '100'
            });
        },
        paging: false,
        searching: false,
        info: false,
        scrollY: '364',
        scrollX: true
    });

    // Graphic
    var data1 = [], data2 = [];

    $.ajax({
        dataType: "json",
        url: 'static/load-eth-history.json',
        // url: '/static/load-eth-history.json',
        async: false
    }).done(function(response) {
        data1 = response;
    });

    $.ajax({
        dataType: "json",
        url: 'static/load-investors-history.json',
        async: false
    }).done(function(response) {
        data2 = response;
    });

    (function() {
        Highcharts.chart('graph', {
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: ''
            },
            subtitle: {
                text: document.ontouchstart === undefined ?
                    '' : ''
            },
            xAxis: [{
                type: 'datetime'
            },{
                type: 'datetime'
            }],
            yAxis: [{
                gridLineWidth: 0,
                title: {
                    text: 'ETH',
                },
                labels: {
                    format: '{value}'
                }
            },{
                gridLineWidth: 0,
                title: {
                    text: 'Кошельки',
                },
                labels: {
                    format: '{value}'
                },
                opposite: true
            }],
            legend: {
                enabled: false
            },
            tooltip: {
                shared: true
            },
            plotOptions: {
                area: {
                    fillColor: {
                        linearGradient: {
                            x1: 0,
                            y1: 0,
                            x2: 0,
                            y2: 1
                        },
                        stops: [
                            [0, '#2a67a1'],
                            [1, 'rgba(255, 255, 255, 0.4)']
                        ]
                    },
                    marker: {
                        radius: 2
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    },
                    threshold: null
                }
            },

            series: [{
                type: 'area',
                name: 'ETH',
                color: '#6985ca',
                data: data1
            },
            {
                type: 'spline',
                name: 'Кошельки',
                color: '#6985ca',
                data: data2
            }]
        });
    })();

});
