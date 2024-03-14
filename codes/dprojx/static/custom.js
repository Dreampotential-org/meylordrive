// capture all errors and send to slack
window.onerror = function (msg, url, lineNo, columnNo, error) {
    var string = msg.toLowerCase();
    var substring = "script error";
    if (string.indexOf(substring) > -1){
        alert('Script Error: See Browser Console for Detail');
    } else {
        var message = [
            'Message: ' + msg,
            'URL: ' + url,
            'Line: ' + lineNo,
            'Column: ' + columnNo,
            'Error object: ' + JSON.stringify(error)
        ].join(' - ');

        log_error_to_slack(message);
    }
    return false;
};

function log_error_to_slack(msg) {
    $.ajax({
        url: '/log-errors/',
        data: JSON.stringify({
          'error': msg,
        }),
        type: 'post',
        success: function(results) {
            //callback(JSON.parse(results))
        }
    })
}

var GLOBAL_FILE = null;
var CURRENT_POSITION = null;
var CURRENT_POSITION_LOW = null;

function init_all() {
    if ($("#user_taken").val() == 'True') {
        swal({
          title: "Email already taken.",
          text: "Please try signing in.",
          icon: "error",
        });
    }

    // hack email to fix validation
    $("input[name='email']").attr("type", "email")
    $(".secAction .btnVideo").on('click', function(e) {
        e.preventDefault();
        $('#takeavideoModal').addClass('is-visible');
    });

    $("#takevideobtn").on("click", function(e){
      e.preventDefault();
      $('#upload-vid').click()
    });

    $('#upload_vid_form').submit(function(e) {
        e.preventDefault();
        var data = new FormData();
        data.append("file", GLOBAL_FILE, GLOBAL_FILE.name);

        var xhr = new XMLHttpRequest();
        // xhr.withCredentials = true;
        function updateProgress(e) {
            if (e.lengthComputable) {
                console.log(e.loaded)
                console.log(e.loaded+  " / " + e.total)
                $(".swal-title").text(parseInt(e.loaded/e.total*100) + "%")
            }
        }

        xhr.upload.addEventListener('progress', updateProgress, false)
        xhr.addEventListener("readystatechange", function() {
            if (this.readyState === 4) {
                if (this.status == 200) {
                    swal({
                      title: "Good job!",
                      text: "Video submitted successfully!",
                      icon: "success",
                    });
                    $("#overlay_loading").hide()
                    $("#takeavideoModal").removeClass("is-visible")
                } else {
                    alert('data upload failed');
                }
            }
        });
        $("#overlay_loading").show()
        xhr.open("POST", "/upload/");
        xhr.send(data);
    });

    $('#upload-vid').on('change', function(e) {
        e.preventDefault();
        var file = e.target.files[0];
        GLOBAL_FILE = file;
        $("#upload_vid_form").submit()
        swal({
            title: "0%",
            text: "Video uploading please wait.",
            icon: "info",
            buttons: false,
            closeOnEsc: false,
            closeOnClickOutside: false,
        });
    });

    $(".secAction .btnEvent").on('click', function(e) {
        window.location = '/gps-checkin';
    });


    $('#signin').on('click', function(e) {
      e.preventDefault();
      $('#signinModal').addClass('is-visible');
    });
    $('#signup').on('click', function(e) {
      e.preventDefault();
      $('#signupModal').addClass('is-visible');
    });
    $('.modal-overlay').on('click', function(e) {
      $('.modal').removeClass('is-visible');
    });
    $('.toggleBar').on('click', function(e) {
      $('.slideMenu').toggle();
        $(this).toggleClass('toggleClose');
    });

    handle_gps()
}

function init_gps() {
    log_error_to_slack("GSP INIT")
    var geo_options_low = {
        enableHighAccuracy: false,
        maximumAge        : 30000,
        timeout           : 27000
    };

    navigator.geolocation.watchPosition(
        geo_success_low, geo_error, geo_options_low
    );

   function geo_error(err) {
        if (err.code  == 1) {
            swal({
              title: "GPS Disabled.",
              text: "Please enable this for Safari to Allow GPS checkin.",
              icon: "error",
            });
        }
       console.log("errror no gps")
       console.warn('ERROR(' + err.code + '): ' + err.message);
       // alert('ERROR(' + err.code + '): ' + err.message);
       log_error_to_slack(
            'ERROR(' + err.code + '): ' + err.message);
       // init_gps()
    }

    geo_options = {
      enableHighAccuracy: true,
      maximumAge        : 30000,
      timeout           : 27000
    };

    navigator.geolocation.watchPosition(
        geo_success, geo_error, geo_options
    );

    function geo_success_low(position) {
        CURRENT_POSITION_LOW = position
        console.log(position.coords.latitude +
                    " " +  position.coords.longitude);
    }

    function geo_success(position) {
        CURRENT_POSITION = position
        console.log(position.coords.latitude +
                    " " +  position.coords.longitude);
    }
}

function handle_gps() {
    if (!(window.location.pathname == '/gps-checkin/')) {
        return
    }
    // show gps
    $('#LocationModal').addClass('is-visible');
    // setup event
    $(".modal-body .btnSubmit").on('click', function(e) {
        e.preventDefault();
        $('#LocationModal').removeClass('is-visible');
        init_gps()

        swal({
            title: "Checking for GPS Signal",
            text: "Please wait while we find GSP location",
            icon: "info",
            buttons: false,
            closeOnEsc: false,
            closeOnClickOutside: false,
        });

        setTimeout(function() {
            var counter = 0;
            var i = setInterval(function() {
                if (CURRENT_POSITION == null && CURRENT_POSITION_LOW == null) {
                    console.log("No GPS Signal. Try again");
                } else {

                    swal({
                        title: "GPS Location Found",
                        text: "Now, enter event and submit",
                        icon: "success",
                    });

                    clearInterval(i);
                }
                counter++;
            }, 200);
        }, 2000);

    })

    $('#locationAuth').on('click', function(e) {
        var text = $(".mainContainer textarea").val()
        if (text.length == 0) {
            $(".eventBox textarea").css("border-color", "red")
            $(".eventBox textarea").css("border", "1")


            swal({
              title: "Note required",
              text: "Please enter description of event",
              type: "warning",
            })
            return
        }

        if (CURRENT_POSITION == null && CURRENT_POSITION_LOW == null) {
            alert("No GPS Signal. Try again");
            return
        }

        var current_loc = null;

        if (CURRENT_POSITION == null) {
            current_loc = CURRENT_POSITION_LOW;
        } else {
            current_loc = CURRENT_POSITION;
        }

        $("#overlay_loading").show()
        $.ajax({
            url: '/gps-checkin/',
            data: {
              'msg': text,
              'lat': current_loc.coords.latitude,
              'long': current_loc.coords.longitude,
            },
            type: 'post',
            success: function(results) {
                if (results.status && results.status == 'okay') {
                    console.log(results)
                    swal({
                      title: "Good job!",
                      text: "Gps and Note submitted successfully!",
                      showCancelButton: false,
                      confirmButtonText: "ok",
                      allowOutsideClick: false,
                      type: "success",
                    }).then(function() {
                        window.location = '/';
                    })
                    $("#overlay_loading").hide()
                }
            }
        });
    });

}

window.addEventListener("DOMContentLoaded", init_all, false);
