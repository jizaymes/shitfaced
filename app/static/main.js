// select file input
const file_upload = document.getElementById('file_upload');

// add event listener
file_upload.addEventListener('change', () => {
    uploadFile(file_upload.files[0]);
});

function clearTaskArea()
{
  document.getElementById("tasks").innerHTML = ""
}

function clearErrorArea()
{
  setError("")
}

function setError(text) {
  document.getElementById('error_area').innerHTML = text
}

function setImage(mongoId) {
  togglePendingAreaAndResultsAreas();
  const elementId = "shitface_image_area"
  const html = `<img src="http://localhost:8000/get_shitfaced/${mongoId}">`
  const shitface_image_area = document.getElementById(elementId)

  shitface_image_area.innerHTML = html

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
    const html = `
      <tr>
        <td id='task_status_${taskID}'>${res.task_status}</td>    
      </tr>`;

    findExistingStatus = document.getElementById('task_status_' + taskID)

    if(!findExistingStatus) {
      newRow = document.getElementById('tasks').insertRow(0);
      newRow.innerHTML = html;
      findExistingStatus = document.getElementById('task_status_' + taskID)
    }
    
    findExistingStatus.innerHTML = res.task_status

    const taskStatus = res.task_status;
    if (taskStatus === 'FAILURE') {
      togglePendingAndErrorAreas()
      setError("Failed due to : " + res.task_result)
      return false;
    }

    if (taskStatus === 'SUCCESS') {
      setImage(res.task_result);
      return true;
    }
    setTimeout(function() {
      getStatus(taskID);
    }, 1000);
  })
  .catch(err => console.log(err));
}

const uploadFile = (file) => {
  clearErrorArea();
  clearTaskArea();
  const fd = new FormData();
  fd.append('file', file);

  toggleUploadAndPendingAreas();  

  // send `POST` request
  fetch('/upload', {
      method: 'POST',
      body: fd
  })
  .then(response => response.json())
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