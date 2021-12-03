// select file input
const file_upload = document.getElementById('file_upload');

// add event listener
file_upload.addEventListener('change', () => {
    uploadFile(file_upload.files[0]);
});

function setImage(taskID) {

  document.getElementById('shitfaced_viewport').innerHTML = `<img src="http://localhost:8000/get_shitfaced/${taskID}">`

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
        <td id='taskID_${taskID}'>${taskID}</td>
        <td id='task_status_${taskID}'>${res.task_status}</td>
        <td id='task_result_${taskID}'>${res.task_result}</td>        
      </tr>`;

    findExistingStatus = document.getElementById('task_status_' + taskID)
    findExistingResult = document.getElementById('task_result_' + taskID)    


    if(!findExistingStatus) {
      newRow = document.getElementById('tasks').insertRow(0);
      newRow.innerHTML = html;
      findExistingStatus = document.getElementById('task_status_' + taskID)
    }
    
    findExistingStatus.innerHTML = res.task_status

    const taskStatus = res.task_status;
    if (taskStatus === 'FAILURE') return false;

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
  document.getElementById('upload_area').disabled = true
  
  const fd = new FormData();
  fd.append('file', file);

  // send `POST` request
  fetch('/upload', {
      method: 'POST',
      body: fd
  })
  .then(response => response.json())
  .then(task => getStatus(task.task_id))
}
