var cam_summary;
function get_cam_sum() {
    $.getJSON("_cam_summary",
        function (data) {
            $('#lat').text(data.lat.toFixed(8));
            $('#lon').text(data.lon.toFixed(8));
            $('#alt').text(data.alt.toFixed(3));
            $('#mode').text(data.mode);
            $('#sats').text(data.sats);
            $('#cam_ready').text(data.ready);
            $('#cam_total').text(data.total);
            $('#cam_capture').text(data.total-data.ready);
            $('#cam_required1').text(data.required);
            $('#cam_required2').text(data.required);
            $('#cam_required3').text(data.required);
            // make cam_summary available through entire application
            cam_summary = data;
        }
    );
}
setInterval('get_cam_sum()', 2000);
//response.setHeader("Cache-Control", "no-cache, no-store, must-revalidate"); // HTTP 1.1.
//response.setHeader("Pragma", "no-cache"); // HTTP 1.0.
//response.setHeader("Expires", "0"); // Proxies.
