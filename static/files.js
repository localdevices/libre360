var photos;
function loadTable()
{
    $(function () {
          $('#logtable').bootstrapTable({
              pagination: true,
              pageList: [10, 15, 20, 50, 100],
              pageSize: 10,
              pageNumber: 1
          });
    });
}

function fetchSurveys(){
    // query survey runs of project
    $.getJSON(
        "_surveys",
        {
            project_id: $('#project').val(),
        },
        function(data){
            console.log(data);
            var dropdown = []
            // start with the 'All' item
            dropdown.push('<option value="All">All</option>');
            if (data.length > 0){
                for (var i = 0; i < data.length; i++) {
                        dropdown.push('<option value="',
                          data[i].survey_run, '">',
                          data[i].survey_run, '</option>');
                }
                $('#survey').prop('disabled', false)
            }
            $("#survey").html(dropdown.join(''));
        }
    );
}

function fetchFiles(onDone){
    $.getJSON(
        "_files",
        {
            project_id: $('#project').val(),
            survey_run: $('#survey').val()
        },
        function(data){
            console.log('data loaded');
            $('#logtable').bootstrapTable("load", data);
            if(data.length > 0)
            {
                photos = JSON.stringify(data);
                // make download button active if data is received
                document.getElementById("download").disabled = false
                document.getElementById("delete").disabled = false
            }
            else
            {
                document.getElementById("download").disabled = true
                document.getElementById("delete").disabled = true
            }

            onDone();
        }
    );
}

function downloadFiles(onDone){
    // redirect to download page
    var url = '/odm360.zip?photos=' + photos
    window.location.replace(url)
    onDone();
}

function deleteFiles(onDone){
    $.getJSON(
        "_delete",
        {
            photos: photos
        },
        function(data){
            console.log('deleting data');
            $('#logtable').bootstrapTable(
                "load", []
            );
            onDone();
        }
    );
}
loadTable();
fetchSurveys();
$('#query').click(function() {
    $('#query').html('<span class="spinner-border spinner-border-sm mr-2" id="spinnerFetch" role="status" aria-hidden="true"></span>Loading...').addClass('disabled');
    fetchFiles(function(){
        $('#query').removeClass("disabled");
        $('#query').html('Load');
    });

    console.log('Query is done.')
});

$('#download').click(function() {
    $('#download').html('<span class="spinner-border spinner-border-sm mr-2" id="spinnerFetch" role="status" aria-hidden="true"></span>Downloading...').addClass('disabled');
    downloadFiles(function(){
        $('#download').removeClass("disabled");
        $('#download').html('Download');
    });
    console.log('Download is done')
});

$('#delete').click(function() {
    $('#delete').html('<span class="spinner-border spinner-border-sm mr-2" id="spinnerFetch" role="status" aria-hidden="true"></span>Deleting...').addClass('disabled');
    document.getElementById("download").disabled = true
    document.getElementById("query").disabled = true
    document.getElementById("delete").disabled = true

    deleteFiles(function(){
        $('#delete').removeClass("disabled");
        $('#delete').html('Delete');
        document.getElementById("query").disabled = false

    });
    console.log('Delete is done')
});

$('#project').change(function() {
    console.log('Changing survey runs')
    $('#survey').empty();
    $('#survey').prop('disabled', true)
    fetchSurveys();
});
