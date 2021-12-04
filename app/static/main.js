// select file input
const file_upload = document.getElementById('file_upload');

// add event listener
file_upload.addEventListener('change', () => {
    uploadFile(file_upload.files[0]);
});

function clearErrorArea()
{
  setError("")
}

function setError(text) {
  document.getElementById('error_area').innerHTML = text
}

function setImage(mongoId) {
  togglePendingAreaAndResultsAreas();

  const html = `<img src="get_shitfaced/${mongoId}"><br><br><input type='button' value="Start Over" onClick='location.reload();'>`
  document.getElementById("shitface_image_area").innerHTML = html

  return true;
}


function getStatus(taskID) {
  fetch(`/tasks/${taskID}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(res => {
    if (res.task_status === 'FAILURE') {
      togglePendingAndErrorAreas()
      setError("Failed due to : " + res.task_result)
      return false;
    } else if (res.task_status === 'SUCCESS') {
      setImage(res.task_result);
      return true;
    }

    // PENDING, just loop and check back in a second
    setTimeout(function() {
      getStatus(taskID);
    }, 1000);
  })
  .catch(err => console.log(err));
}

const uploadFile = (file) => {
  clearErrorArea();

  const fd = new FormData();
  fd.append('file', file);

  // send `POST` request
  fetch('/upload', {
      method: 'POST',
      body: fd
  })
  .then(response => response.json())
  .then(toggleUploadAndPendingAreas())
  .then(task => getStatus(task.task_id))

}

function togglePendingAreaAndResultsAreas() {
  document.getElementById('upload_area').style = "display: none;";  
  document.getElementById('pending_area').style = "display: none;";
  document.getElementById('results_area').style = "display: block;";
}

function toggleUploadAndPendingAreas() {
  document.getElementById('upload_area').style = "display: none;";
  document.getElementById('pending_area').style = "display: block;";
}

function togglePendingAndErrorAreas() {
  document.getElementById('pending_area').style = "display: none;";
  document.getElementById('upload_area').style = "display: block;";
}